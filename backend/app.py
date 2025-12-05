import io
import matplotlib

matplotlib.use('Agg')

import os
from flask import Flask, current_app, request, jsonify, send_from_directory, session, redirect, url_for, make_response
from flask_cors import CORS
from werkzeug.utils import secure_filename
from functools import wraps
from src.utils.dicom import load_dicom_with_interpolation
from src.utils.nifti import load_nifti
from src.utils.rotate import apply_rotation
from src.utils.save import save_visualization
from src.utils.compress import rle_encode
from src.utils.crop_voxel import crop_3d_array_max_xy
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import uuid
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = './uploads'

# CORSの設定
CORS(app, supports_credentials=True)

# アップロード可能な拡張子
ALLOWED_EXTENSIONS = {'dcm', 'nii', 'nii.gz'}

# ユーザー認証情報（ハードコード）
USERS = {
    'admin': 'password123'
}

# セッションデータを保存するための辞書
SESSION_DATA = {}

TransposeOrder = (1, 2, 0)
RotationAngles = (0, 0, 90)

def allowed_file(filename):
    """許可されたファイル拡張子かどうかをチェック"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    """ユーザー認証が必要なエンドポイントのためのデコレータ"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['POST'])
def login():
    """ログイン処理"""
    username = request.form.get('username')
    password = request.form.get('password')
    if username in USERS and USERS[username] == password:
        session['logged_in'] = True
        session['user_id'] = str(uuid.uuid4())
        SESSION_DATA[session['user_id']] = {}  # セッションデータの初期化
        return jsonify({'status': 'success'})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/logout')
def logout():
    """ログアウト処理"""
    user_id = session.pop('user_id', None)
    session.pop('logged_in', None)
    if user_id in SESSION_DATA:
        del SESSION_DATA[user_id]  # セッションデータの削除
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
@login_required
def upload_files():
    """ファイルアップロード処理"""
    if 'dicom_files' not in request.files and 'nifti_files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    user_id = session['user_id']
    user_upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], user_id)
    os.makedirs(user_upload_dir, exist_ok=True)

    # DICOMファイルの処理
    if 'dicom_files' in request.files:
        dicom_files = request.files.getlist('dicom_files')
        dicom_dir = os.path.join(user_upload_dir, 'dicom')
        os.makedirs(dicom_dir, exist_ok=True)
        for file in dicom_files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(dicom_dir, filename)
                file.save(file_path)
            else:
                return jsonify({'error': 'Invalid DICOM file type'}), 400

    # NIFTIファイルの処理
    nifti_info_list = []
    if 'nifti_files' in request.files:
        nifti_files = request.files.getlist('nifti_files')
        nifti_dir = os.path.join(user_upload_dir, 'nifti')
        os.makedirs(nifti_dir, exist_ok=True)

        # アルファベット順でソート
        nifti_files_sorted = sorted(nifti_files, key=lambda f: f.filename.lower())

        organ_counter = 25     # 通常臓器用
        cancer_counter = 31   # cancer 用（開始番号）

        for file in nifti_files_sorted:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(nifti_dir, filename)
                file.save(file_path)

                fname = filename.lower()

                # ---- value の振り分け ----
                if "background" in fname:
                    value = 1
                elif "cancer" in fname or "lymph" in fname:
                    value = cancer_counter
                    cancer_counter += 1
                else:
                    value = organ_counter
                    organ_counter += 1

                nifti_info = {
                    'path': file_path,
                    'value': value,
                }
                print(f"{filename}: {value}")
                nifti_info_list.append(nifti_info)

            else:
                return jsonify({'error': 'Invalid NIFTI file type'}), 400

    # midpointsを取得
    midpoints_str = request.form.get('midpoints', None)
    if midpoints_str:
        try:
            midpoints = [int(x) for x in midpoints_str.split(',')]
        except ValueError:
            return jsonify({'error': 'Invalid midpoints format'}), 400
    else:
        midpoints = None  # midpointsが提供されない場合はNone

    # スケールファクターを取得
    scale_factor = float(request.form.get('scale_factor', 0.5))
    print(f"スケールファクター: {scale_factor}")

    # 処理と可視化
    output_dir = os.path.join(user_upload_dir, 'output_images')
    os.makedirs(output_dir, exist_ok=True)

    try:
        new_3d_array, dicom_array = create_3d_array(dicom_dir, nifti_info_list, scale_factor)
        SESSION_DATA[user_id]['new_3d_array'] = new_3d_array
        SESSION_DATA[user_id]['dicom_data'] = dicom_array

        image_files = visualize_3d_array(new_3d_array, SESSION_DATA[user_id]['dicom_data'], output_dir, midpoints)

        image_urls = []
        for img in image_files:
            filename = os.path.relpath(img['file'], user_upload_dir)
            filename = filename.replace('\\', '/')
            image_url = url_for('get_image', filename=filename, _external=True)
            image_urls.append({
                'view': img['view'],
                'type': img['type'],
                'url': image_url
            })

        return jsonify({'images': image_urls})

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/get_image/<path:filename>')
@login_required
def get_image(filename):
    user_id = session['user_id']
    user_upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], user_id)
    filename = filename.replace('\\', '/')  
    directory = os.path.dirname(filename)
    file = os.path.basename(filename)
    return send_from_directory(os.path.join(user_upload_dir, directory), file)

@app.route('/get_dicom_shape', methods=['GET'])
@login_required
def get_dicom_shape():
    """DICOMデータの形状を取得"""
    user_id = session['user_id']
    if 'dicom_data' in SESSION_DATA[user_id]:
        shape = SESSION_DATA[user_id]['dicom_data'].shape
        return jsonify({'shape': list(shape)})
    else:
        return jsonify({'error': 'DICOM data not found'}), 400

def create_3d_array(dicom_path, nifti_data, scale_factor=1.0):
    """DICOMと複数のNIFTIデータから新たな3次元配列を作成"""
    dicom_data = load_dicom_with_interpolation(dicom_path, scale_factor)
    rotation_data = np.transpose(dicom_data, TransposeOrder)
    dicom_array = apply_rotation(rotation_data, RotationAngles)

    # new_3d_array は DICOM の強度をベースに作る（ここは既存仕様に合わせる）
    new_3d_array = dicom_array.copy()

    # DICOM 由来の値を 1~24 に制限（もしこのクリップが不要なら無効化してもOK）
    new_3d_array = np.clip(new_3d_array, 1, 24)

    # デバッグ用：各 NIfTI の情報を出力
    for nifti_info in nifti_data:
        path = nifti_info.get('path')
        value = nifti_info.get('value')
        # load_nifti は replacement_value を埋め込んだ配列を返す
        nifti_array = load_nifti(path, replacement_value=value)

        # サイズチェック
        if dicom_array.shape != nifti_array.shape:
            raise ValueError(f"DICOM and NIFTI data sizes do not match for {path}: dicom {dicom_array.shape} vs nifti {nifti_array.shape}")

        # デバッグ出力：非ゼロボクセル数を出す（ここで 0 ならその NIfTI は空）
        nonzero_count = int(np.count_nonzero(nifti_array))
        print(f"[NIFTI LOAD] file={os.path.basename(path)}, assigned_value={value}, nonzero_voxels={nonzero_count}")

        if nonzero_count == 0:
            # 重要：ここで 0 なら "そのファイルには該当ラベル領域が無い" ことを意味する
            # 必要なら警告・スキップ
            print(f"Warning: NIfTI {path} has 0 mask voxels — skipping.")
            continue

        # 上書き（nifti_array が既に replacement_value を持つので nifti_array != 0 で判定）
        mask = nifti_array != 0
        # 代入（この方法は np.where と等価だが、デバッグしやすい）
        new_3d_array[mask] = nifti_array[mask]

    return new_3d_array, dicom_array
def create_label_colormap(unique_labels):
    """ラベル値に基づく完全固定カラーマップを作成"""

    organ_colors = [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
        "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
        "#bcbd22", "#17becf", "#ff1493", "#00fa9a"
    ]

    cancer_colors = [
        "#ff0000", "#cc0000", "#990000", "#ff4d4d",
        "#ff6666", "#ff8080"
    ]

    label_to_color = {}

    for label in sorted(unique_labels):
        if label == 0:
            label_to_color[label] = "black"
        elif label == 1:
            label_to_color[label] = "#404040"       # background
        elif 25 <= label < 31:
            idx = (label - 25) % len(organ_colors)
            label_to_color[label] = organ_colors[idx]
        elif label >= 31:
            idx = (label - 100) % len(cancer_colors)
            label_to_color[label] = cancer_colors[idx]
        else:
            # fallback
            label_to_color[label] = "#ffffff"

    # colormap を作成
    colors = [label_to_color[l] for l in sorted(unique_labels)]
    cmap = matplotlib.colors.ListedColormap(colors)

    # 値→色のインデックス用に辞書も返す
    index_map = {l: i for i, l in enumerate(sorted(unique_labels))}
    return cmap, index_map


def visualize_3d_array(new_3d_array, dicom_data, output_dir, midpoints=None):
    """3次元配列を可視化し、各断面ごとに画像を保存（統一配色版）"""
    if midpoints is None:
        midpoints = [s // 2 for s in new_3d_array.shape]
    else:
        if len(midpoints) != 3:
            raise ValueError("Midpoints must be a list of three integers.")
        for i, m in enumerate(midpoints):
            if not (0 <= m < new_3d_array.shape[i]):
                raise ValueError(f"Midpoint {m} is out of bounds for axis {i} with size {new_3d_array.shape[i]}")

    # --- 固定カラーマップを使用 ---
    unique_labels = np.unique(new_3d_array)
    print(f"unique_labels: {unique_labels}")
    custom_cmap, index_map = create_label_colormap(unique_labels)

    # カラーマップのインデックスに変換
    indexed_array = np.vectorize(index_map.get)(new_3d_array)

    # 全体の最小値・最大値を事前に計算（統一配色のため）
    dicom_vmin, dicom_vmax = dicom_data.min(), dicom_data.max()
    new_vmin, new_vmax = new_3d_array.min(), new_3d_array.max()
    
    # 差分画像の範囲も事前に計算
    diff_vmin, diff_vmax = (new_3d_array - dicom_data).min(), (new_3d_array - dicom_data).max()

    views = ['Sagittal', 'Coronal', 'Axial']
    image_files = []

    for i, (view, midpoint) in enumerate(zip(views, midpoints)):
        if view == 'Sagittal':
            dicom_slice = dicom_data[midpoint, :, :]
            new_slice = new_3d_array[midpoint, :, :]
        elif view == 'Coronal':
            dicom_slice = dicom_data[:, midpoint, :]
            new_slice = new_3d_array[:, midpoint, :]
        else:  # Axial
            dicom_slice = dicom_data[:, :, midpoint]
            new_slice = new_3d_array[:, :, midpoint]

        diff_slice = new_slice - dicom_slice

        # DICOM Slice（グレースケールは統一範囲を適用）
        fig, ax = plt.subplots()
        ax.imshow(dicom_slice, cmap='gray', vmin=dicom_vmin, vmax=dicom_vmax)
        ax.set_title(f'{view} - DICOM (Slice {midpoint})')
        ax.axis('off')
        dicom_file = os.path.join(output_dir, f'{view}_DICOM.png')
        save_visualization(fig, dicom_file)
        plt.close(fig)
        image_files.append({'view': view, 'type': 'DICOM', 'file': dicom_file})

        # Fused Image（カスタムカラーマップに統一範囲を適用）
        fig, ax = plt.subplots()
        indexed_slice = indexed_array[midpoint, :, :] if view=="Sagittal" else \
                 indexed_array[:, midpoint, :] if view=="Coronal" else \
                 indexed_array[:, :, midpoint]
        im = ax.imshow(indexed_slice, cmap=custom_cmap, interpolation='nearest')

        ax.set_title(f'{view} - Fused (Slice {midpoint})')
        ax.axis('off')

        # カラーバーを左側に配置
        from mpl_toolkits.axes_grid1 import make_axes_locatable
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("left", size="5%", pad=0.05)
        cbar = plt.colorbar(im, cax=cax)
        cax.yaxis.set_ticks_position('left')
        cax.yaxis.set_label_position('left')

        fused_file = os.path.join(output_dir, f'{view}_Fused.png')
        save_visualization(fig, fused_file)
        plt.close(fig)
        image_files.append({'view': view, 'type': 'Fused', 'file': fused_file})

        # Difference Image（hot カラーマップに統一範囲を適用）
        fig, ax = plt.subplots()
        ax.imshow(diff_slice, cmap='hot', interpolation='nearest', 
                 vmin=diff_vmin, vmax=diff_vmax)
        ax.set_title(f'{view} - Difference')
        ax.axis('off')
        diff_file = os.path.join(output_dir, f'{view}_Difference.png')
        save_visualization(fig, diff_file)
        plt.close(fig)
        image_files.append({'view': view, 'type': 'Difference', 'file': diff_file})

    return image_files

@app.route('/regenerate', methods=['POST'])
@login_required
def regenerate_image():
    """画像の再生成"""
    user_id = session['user_id']
    user_upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], user_id)
    output_dir = os.path.join(user_upload_dir, 'output_images')
    os.makedirs(output_dir, exist_ok=True)

    if 'new_3d_array' not in SESSION_DATA[user_id] or 'dicom_data' not in SESSION_DATA[user_id]:
        return jsonify({'error': 'No processed data found'}), 400

    # JSONデータから midpoints を取得
    data = request.get_json()
    midpoints = data.get('midpoints')

    if not midpoints or not isinstance(midpoints, list) or len(midpoints) != 3:
        return jsonify({'error': 'Invalid midpoints format'}), 400

    try:
        # 現在のタイムスタンプを取得
        timestamp = int(time.time())
        image_files = visualize_3d_array(SESSION_DATA[user_id]['new_3d_array'], SESSION_DATA[user_id]['dicom_data'], output_dir, midpoints)

        image_urls = []
        for img in image_files:
            filename = os.path.relpath(img['file'], user_upload_dir)
            filename = filename.replace('\\', '/')
            # URLにタイムスタンプを追加
            image_url = url_for('get_image', filename=filename, _external=True, t=timestamp)
            image_urls.append({
                'view': img['view'],
                'type': img['type'],
                'url': image_url
            })
        return jsonify({'images': image_urls})

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/download_array', methods=['GET']) 
@login_required
def download_array():
    """圧縮した3D配列データをプレーンテキストファイルとしてダウンロード"""
    user_id = session.get('user_id')
    if not user_id:
        current_app.logger.warning(f"Attempted access without user_id in session")
        return jsonify({'error': 'User not authenticated', 'details': 'No user_id found in session'}), 401

    if 'new_3d_array' not in SESSION_DATA.get(user_id, {}):
        current_app.logger.warning(f"No processed data found for user_id: {user_id}")
        return jsonify({'error': 'No processed data found', 'details': 'new_3d_array not found in session data'}), 400

    array_data = SESSION_DATA[user_id]['new_3d_array']
    
    # 配列を整数型に変換
    array_data_int = array_data.astype(int)
    
    # crop_data = array_data_int
    crop_data = crop_3d_array_max_xy(array_data_int)
    
    # メモリ上のテキストストリームを作成
    buffer = io.StringIO()

    # 配列をスライスごとに圧縮してバッファに書き込む
    for i in range(crop_data.shape[2]):
        # 2Dスライスをフラットにする
        flattened_slice = crop_data[:, :, i].flatten()
        # 圧縮する
        compressed_slice = rle_encode(flattened_slice)
        # 圧縮したデータをバッファに書き込む
        buffer.write(' '.join(map(str, compressed_slice)) + '\n')

    # バッファの内容を取得
    buffer.seek(0)
    data = buffer.getvalue()

    # レスポンスを作成
    response = make_response(data)
    response.headers['Content-Disposition'] = 'attachment; filename=compressed_3d_array.txt'
    response.headers['Content-Type'] = 'text/plain'

    return response

if __name__ == '__main__':
    app.run(debug=True)
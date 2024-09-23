import matplotlib
matplotlib.use('Agg')

import os
from flask import Flask, request, jsonify, send_file, send_from_directory, session, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
from functools import wraps
from src.utils.dicom import load_dicom
from src.utils.nifti import load_nifti
from src.utils.rotate import apply_rotation
from src.utils.save import save_visualization
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import uuid

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = './uploads'

# アップロード可能な拡張子
ALLOWED_EXTENSIONS = {'dcm', 'nii', 'nii.gz'}

# ユーザー認証情報（ハードコード）
USERS = {
    'admin': 'password123'
}

# セッションデータを保存するための辞書
SESSION_DATA = {}

TransposeOrder = (1, 2, 0)
RotationAngles = (180, 0, 90)

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
    user_id = session.pop('logged_in', None)
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
        for idx, file in enumerate(nifti_files):
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(nifti_dir, filename)
                file.save(file_path)
                # NIFTIファイル情報のリストを作成
                nifti_info = {
                    'path': file_path,
                    'value': idx + 2,  # 値は2から始まる（1は背景として予約）
                }
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

    # 処理と可視化
    output_dir = os.path.join(user_upload_dir, 'output_images')
    os.makedirs(output_dir, exist_ok=True)

    try:
        new_3d_array, dicom_array = create_3d_array(dicom_dir, nifti_info_list)
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

def create_custom_cmap(colors):
    n_bins = 100
    return LinearSegmentedColormap.from_list('custom', colors, N=n_bins)

def create_3d_array(dicom_path, nifti_data):
    """DICOMと複数のNIFTIデータから新たな3次元配列を作成"""
    dicom_data = load_dicom(dicom_path)
    rotation_data = np.transpose(dicom_data, TransposeOrder)
    dicom_array = apply_rotation(rotation_data, RotationAngles)
    new_3d_array = dicom_array.copy()

    for nifti_info in nifti_data:
        nifti_array = load_nifti(nifti_info['path'], nifti_info['value'])

        if dicom_array.shape != nifti_array.shape:
            raise ValueError(f"DICOM and NIFTI data sizes do not match for {nifti_info['path']}")

        new_3d_array = np.where(nifti_array != 0, nifti_info['value'], new_3d_array)

    return new_3d_array, dicom_array

def visualize_3d_array(new_3d_array, dicom_data, output_dir, midpoints=None):
    """3次元配列を可視化し、各断面ごとに画像を保存"""
    if midpoints is None:
        midpoints = [s // 2 for s in new_3d_array.shape]
    else:
        if len(midpoints) != 3:
            raise ValueError("Midpoints must be a list of three integers.")
        for i, m in enumerate(midpoints):
            if not (0 <= m < new_3d_array.shape[i]):
                raise ValueError(f"Midpoint {m} is out of bounds for axis {i} with size {new_3d_array.shape[i]}")

    colors = ['black', 'gray'] + ['red', 'green', 'blue', 'yellow', 'cyan', 'magenta'][:len(set(new_3d_array.flatten())) - 2]
    custom_cmap = create_custom_cmap(colors)

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

        # DICOM Slice
        fig, ax = plt.subplots()
        ax.imshow(dicom_slice, cmap='gray')
        ax.set_title(f'{view} - DICOM (Slice {midpoint})')
        ax.axis('off')
        dicom_file = os.path.join(output_dir, f'{view}_DICOM.png')
        save_visualization(fig, dicom_file)
        plt.close(fig)
        image_files.append({'view': view, 'type': 'DICOM', 'file': dicom_file})

        # Fused Image
        fig, ax = plt.subplots()
        im = ax.imshow(new_slice, cmap=custom_cmap)
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

        # Difference Image
        fig, ax = plt.subplots()
        ax.imshow(diff_slice, cmap='hot')
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

    midpoints_str = request.form.get('midpoints', None)
    if midpoints_str:
        try:
            midpoints = [int(x) for x in midpoints_str.split(',')]
        except ValueError:
            return jsonify({'error': 'Invalid midpoints format'}), 400
    else:
        return jsonify({'error': 'Midpoints are required'}), 400

    try:
        image_files = visualize_3d_array(SESSION_DATA[user_id]['new_3d_array'], SESSION_DATA[user_id]['dicom_data'], output_dir, midpoints)

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

if __name__ == '__main__':
    app.run(debug=True)
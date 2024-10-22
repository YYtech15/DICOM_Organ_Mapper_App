import pydicom
import numpy as np
from pathlib import Path
from tqdm import tqdm
import json
import os

from src.utils.interpolation import bspline_interpolate_3d_chunked_ct

def load_hu_ranges(file_path='src/data/hu_ranges_24.json'):
    """
    JSON ファイルから HU ranges を読み込む
    """
    # スクリプトのディレクトリを基準にした絶対パスを取得
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    absolute_file_path = os.path.join(base_path, file_path)
    
    try:
        with open(absolute_file_path, 'r') as f:
            data = json.load(f)
        return data['hu_ranges']
    except FileNotFoundError:
        print(f"エラー: ファイル '{absolute_file_path}' が見つかりません。")
        print(f"現在の作業ディレクトリ: {os.getcwd()}")
        return None
    except json.JSONDecodeError:
        print(f"エラー: ファイル '{absolute_file_path}' の JSON 形式が無効です。")
        return None

def apply_hu_ranges(pixel_array, rescale_intercept, rescale_slope):
    """
    pixel_arrayをHU値に変換し、指定されたHU値の範囲に基づいてボクセル値を置き換える
    """
    # ピクセル値をHU値に変換
    hu_array = pixel_array * rescale_slope + rescale_intercept
    
    # HU値の範囲と対応するボクセル値を外部ファイルから読み込む
    hu_ranges = load_hu_ranges('src/data/hu_ranges_24.json')
    if hu_ranges is None:
        raise ValueError("Failed to load HU ranges")
    
    # 結果を格納する配列を作成
    result = np.zeros_like(hu_array, dtype=np.uint16)
    
    # 各HU値の範囲に対して処理を行う
    for min_hu, max_hu, value in hu_ranges:
        mask = (hu_array >= min_hu) & (hu_array < max_hu)
        result[mask] = value
    
    return result

def load_dicom(directory):
    """
    DICOMファイルを読み込み、HU値に基づいて変換された3D配列として返す
    """
    dicom_files = sorted(Path(directory).glob('*.dcm'))
    if not dicom_files:
        raise ValueError("No DICOM files found in the directory.")
    slices = [pydicom.dcmread(str(f)) for f in tqdm(dicom_files, desc="Loading DICOM files")]
    slices.sort(key=lambda x: float(x.ImagePositionPatient[2]))
    
    # すべてのスライスが同じ行数と列数を持つことを確認
    if len(set(s.Rows for s in slices)) > 1 or len(set(s.Columns for s in slices)) > 1:
        raise ValueError("All DICOM slices must have the same dimensions")
    
    # 3D配列を作成
    img_shape = (len(slices), slices[0].Rows, slices[0].Columns)
    img3d = np.zeros(img_shape, dtype=np.uint16)
    
    for i, slice in enumerate(tqdm(slices, desc="Creating 3D array")):
        pixel_array = slice.pixel_array
        rescale_intercept = slice.RescaleIntercept
        rescale_slope = slice.RescaleSlope
        
        # HU値の範囲に基づいてボクセル値を置き換え
        img3d[i, :, :] = apply_hu_ranges(pixel_array, rescale_intercept, rescale_slope)
    
    return img3d

def load_dicom_with_interpolation(directory, scale_factor=1.0):
    """
    DICOMファイルを読み込み、B-スプライン補間を適用して3D配列として返す
    :param directory: DICOMファイルが格納されているディレクトリ
    :param scale_factor: リサイズのスケールファクター（デフォルトは1.0で元のサイズ）
    :return: 補間後の3D numpy配列
    """
    # 既存のload_dicom関数を使用してDICOMデータを読み込む
    original_data = load_dicom(directory)
    
    # スケールファクターが1.0でない場合にのみ補間を適用
    if scale_factor != 1.0:
        print(f"スケールファクター{scale_factor}でB-スプライン補間を適用します。")
        return bspline_interpolate_3d_chunked_ct(original_data, scale_factor)
    else:
        print("スケールファクターが1.0のため、補間を適用しません。")
        return original_data
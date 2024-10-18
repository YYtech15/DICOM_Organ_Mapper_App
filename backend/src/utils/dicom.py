# src/utils_dicom.py

import pydicom
import numpy as np
from pathlib import Path
from tqdm import tqdm

# HU値の範囲と対応するボクセル値を定義
hu_ranges = [
    (-3000, -901, 0),  # Air
    (-901, -499, 1),   # Lung
    (-499, -1, 2),     # ADIPOSETISSUE
    (-1, 200, 3),      # SOFTTISSUE
    (200, 1700, 4),    # Bone
    (1700, 2000, 5)    # Teeth
]

def apply_hu_ranges(pixel_array, rescale_intercept, rescale_slope):
    """
    pixel_arrayをHU値に変換し、指定されたHU値の範囲に基づいてボクセル値を置き換える
    """
    # ピクセル値をHU値に変換
    hu_array = pixel_array * rescale_slope + rescale_intercept
    
    # 結果を格納する配列を作成
    result = np.zeros_like(hu_array, dtype=np.uint8)
    
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
    img3d = np.zeros(img_shape, dtype=np.uint8)
    
    for i, slice in enumerate(tqdm(slices, desc="Creating 3D array")):
        pixel_array = slice.pixel_array
        rescale_intercept = slice.RescaleIntercept
        rescale_slope = slice.RescaleSlope
        
        # HU値の範囲に基づいてボクセル値を置き換え
        img3d[i, :, :] = apply_hu_ranges(pixel_array, rescale_intercept, rescale_slope)
    
    return img3d

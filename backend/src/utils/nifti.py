# src/utils_nifti.py

import numpy as np
import nibabel as nib

def load_nifti(file_path, replacement_value=0):
    '''
    NIFTIファイルを読み込み、1の値を指定した値に置き換えた3D配列として返す
    '''
    img = nib.load(file_path)
    data = img.get_fdata()
    
    # 1の値を指定した値に置き換え
    data = np.where(data == 1, replacement_value, 0)
    
    return data

# src/utils_nifti.py

import numpy as np
import nibabel as nib

def load_nifti(file_path, replacement_value=0):
    """
    NIFTIを読み込み、マスク部分を replacement_value に置換した配列を返す。
    マスク判定は「> 0.5」で行う（1 や 255 とかのしきい値に対応）。
    戻り値は読み取りやすくするため float ではなく同じ dtype の配列を返します。
    """
    img = nib.load(file_path)
    data = img.get_fdata()

    # マスク検出（閾値で判定）
    mask = data > 0.5

    # 出力配列を用意して置換値を設定
    out = np.zeros_like(data, dtype=np.int32)
    out[mask] = int(replacement_value)

    return out

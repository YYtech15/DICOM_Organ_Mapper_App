import numpy as np

def crop_3d_array_max_xy(arr):
    """
    256×256×485の3D numpy配列から、すべてのxy平面で等しく、
    非1要素を含む最大の矩形領域を切り出します。
    z軸方向は元の大きさを維持します。

    Parameters:
    arr (numpy.ndarray): 256×256×485の形状を持つ3D numpy配列。値は1から24の範囲内。

    Returns:
    numpy.ndarray: すべてのxy平面で等しく切り出され、z軸方向は元の大きさを維持した3D配列。
    """
    # 入力配列の検証
    # if arr.shape != (256, 256, 485) or arr.min() < 1:
        # raise ValueError(f"現在は{arr.shape}の形状です。256×256×485の形状で、値は1から24の範囲内である必要があります。")
    # if arr.shape != (256, 256, 217) or arr.min() < 1:
    #     raise ValueError(f"現在は{arr.shape}の形状です。256×256×217の形状で、値は1から24の範囲内である必要があります。")
    # if arr.shape != (256, 256, 377) or arr.min() < 1:
    #     raise ValueError(f"現在は{arr.shape}の形状です。256×256×217の形状で、値は1から24の範囲内である必要があります。")
    # z軸に沿って非1要素の位置を確認
    non_one = arr != 1
    
    # xy平面上で非1要素を含む最大の矩形領域を見つける
    x_non_one = np.any(non_one, axis=(1, 2))
    y_non_one = np.any(non_one, axis=(0, 2))
    
    x_indices = np.where(x_non_one)[0]
    y_indices = np.where(y_non_one)[0]
    
    if len(x_indices) == 0 or len(y_indices) == 0:
        print("非1要素が見つかりませんでした。元の配列を返します。")
        return arr.copy()
    
    x_start, x_end = x_indices[0], x_indices[-1] + 1
    y_start, y_end = y_indices[0], y_indices[-1] + 1
    
    # xy平面上で最大の範囲を切り出し、z軸は全て保持
    cropped_arr = arr[x_start:x_end, y_start:y_end, :].copy()
    
    print("元の形状:", arr.shape)
    print("切り出し後の形状:", cropped_arr.shape)
    return cropped_arr
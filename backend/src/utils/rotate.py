# src/utils_rotate.py

import numpy as np
from scipy.ndimage import affine_transform
import time

def apply_rotation(data, rotation_angles):
    """
    3D arrayに回転を適用する（高速版）
    """
    start_time = time.time()
    print("Starting rotation...")

    # 角度をラジアンに変換
    ax, ay, az = np.deg2rad(rotation_angles)
    
    # 各軸周りの回転行列を計算
    Rx = np.array([[1, 0, 0],
                   [0, np.cos(ax), -np.sin(ax)],
                   [0, np.sin(ax),  np.cos(ax)]])
    
    Ry = np.array([[ np.cos(ay), 0, np.sin(ay)],
                   [0, 1, 0],
                   [-np.sin(ay), 0, np.cos(ay)]])
    
    Rz = np.array([[np.cos(az), -np.sin(az), 0],
                   [np.sin(az),  np.cos(az), 0],
                   [0, 0, 1]])
    
    # 回転行列を組み合わせる
    R = Rz @ Ry @ Rx  # 行列の積を使用
    # affine_transformは逆行列を使用するため、Rを逆行列化
    R_inv = np.linalg.inv(R)
    
    # データの中心を計算
    center = np.array(data.shape) / 2.0
    # オフセットを計算
    offset = center - R_inv @ center

    # アフィン変換を適用
    print("Applying affine transformation...")
    rotated_data = affine_transform(data, R_inv, offset=offset, order=1, mode='constant', cval=0.0)
    
    end_time = time.time()
    print(f"Fast rotation completed in {end_time - start_time:.2f} seconds.")
    
    return rotated_data

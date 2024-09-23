import numpy as np
import numba
import time

@numba.njit(parallel=True)
def rotate_volume(data, R_inv, offset):
    """
    Numbaを使用して高速化した3Dボリュームの回転関数
    """
    shape = data.shape
    output = np.zeros(shape, dtype=data.dtype)
    for x in numba.prange(shape[0]):
        for y in range(shape[1]):
            for z in range(shape[2]):
                # 出力座標から入力座標へのマッピング
                coord = np.array([x, y, z], dtype=np.float64)
                input_coord = np.dot(R_inv, coord) + offset

                xi, yi, zi = input_coord
                if (0 <= xi < shape[0]-1 and 0 <= yi < shape[1]-1 and 0 <= zi < shape[2]-1):
                    x0 = int(np.floor(xi))
                    y0 = int(np.floor(yi))
                    z0 = int(np.floor(zi))
                    xd = xi - x0
                    yd = yi - y0
                    zd = zi - z0

                    # 8つの隣接点の値を取得
                    c000 = data[x0, y0, z0]
                    c100 = data[x0+1, y0, z0]
                    c010 = data[x0, y0+1, z0]
                    c001 = data[x0, y0, z0+1]
                    c101 = data[x0+1, y0, z0+1]
                    c011 = data[x0, y0+1, z0+1]
                    c110 = data[x0+1, y0+1, z0]
                    c111 = data[x0+1, y0+1, z0+1]

                    # トリリニア補間
                    c00 = c000 * (1 - xd) + c100 * xd
                    c01 = c001 * (1 - xd) + c101 * xd
                    c10 = c010 * (1 - xd) + c110 * xd
                    c11 = c011 * (1 - xd) + c111 * xd
                    c0 = c00 * (1 - yd) + c10 * yd
                    c1 = c01 * (1 - yd) + c11 * yd
                    c = c0 * (1 - zd) + c1 * zd

                    output[x, y, z] = c
                else:
                    output[x, y, z] = 0.0
    return output

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
    # Numbaでの計算のため、逆行列を計算
    R_inv = np.linalg.inv(R)
    
    # データの中心を計算
    center = np.array(data.shape) / 2.0
    # オフセットを計算（修正済み）
    offset = center - R_inv @ center

    # アフィン変換を適用
    print("Applying affine transformation...")
    rotated_data = rotate_volume(data, R_inv, offset)
    
    end_time = time.time()
    print(f"Fast rotation completed in {end_time - start_time:.2f} seconds.")
    
    return rotated_data

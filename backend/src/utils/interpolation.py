import numpy as np
from scipy.ndimage import zoom
from tqdm import tqdm

def bspline_interpolate_3d_chunked(ct_data, scale_factor, chunk_size=64):
    """
    3次元CTデータをチャンクに分割し、B-スプライン補間を適用してリサイズする。
    :param ct_data: 入力CTデータ（3次元NumPy配列）
    :param scale_factor: スケールファクター（例：0.5で半分のサイズに）
    :param chunk_size: 各チャンクのサイズ
    :return: 補間後の3次元NumPy配列
    """
    original_shape = np.array(ct_data.shape)
    new_shape = (original_shape * scale_factor).astype(int)
    
    print(f"元のデータサイズ: {original_shape}")
    print(f"リサイズ後のデータサイズ: {new_shape}")
    
    # 結果を格納する配列を作成
    result = np.zeros(new_shape, dtype=ct_data.dtype)
    
    # チャンクのサイズと数を計算
    z_ranges = range(0, original_shape[0], chunk_size)
    
    with tqdm(total=len(z_ranges), desc="Interpolating chunks") as pbar:
        for i in z_ranges:
            # チャンクの範囲を定義（軸0のみチャンク化）
            chunk_slice = np.s_[i:i+chunk_size, :, :]
            chunk_data = ct_data[chunk_slice]
            
            # チャンクの新しいサイズを計算
            chunk_original_shape = np.array(chunk_data.shape)
            chunk_new_shape = (chunk_original_shape * scale_factor).astype(int)
            
            # チャンクに対してB-スプライン補間を適用
            chunk_result = bspline_interpolate_3d(chunk_data, scale_factor)
            
            # 補間結果を全体の結果配列に挿入
            new_i = int(i * scale_factor)
            result[new_i:new_i+chunk_new_shape[0], :, :] = chunk_result
            
            pbar.update(1)
    
    return result

def bspline_interpolate_3d(ct_data, scale_factor):
    """
    3次元CTデータにB-スプライン補間を適用し、指定したスケールファクターでリサイズする。
    :param ct_data: 入力CTデータ（3次元NumPy配列）
    :param scale_factor: スケールファクター（例：0.5で半分のサイズに）
    :return: 補間後の3次元NumPy配列
    """
    # スケールファクターがリストまたはタプルでない場合、各軸に適用
    if not isinstance(scale_factor, (list, tuple, np.ndarray)):
        scale_factor = [scale_factor] * ct_data.ndim
    
    # B-スプライン補間（order=3は3次のスプライン補間を意味します）
    interpolated_data = zoom(ct_data, zoom=scale_factor, order=3)
    return interpolated_data
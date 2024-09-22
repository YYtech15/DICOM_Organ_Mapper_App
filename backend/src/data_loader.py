# utils/data_loader.py

import os
import numpy as np
import pydicom
import nibabel as nib
from .anonymizer import anonymize_dicom

def load_dicom_files(directory):
    """
    複数のDICOMファイルを読み込んで3Dボリュームデータを生成する

    Args:
        directory (str): DICOMファイルが含まれるディレクトリのパス

    Returns:
        numpy.ndarray: 3Dボリュームデータ
    """
    slices = []
    # ファイル名をソートして正しい順序で読み込む
    for filename in sorted(os.listdir(directory)):
        if filename.lower().endswith('.dcm'):
            filepath = os.path.join(directory, filename)
            ds = pydicom.dcmread(filepath)
            ds = anonymize_dicom(ds)  # データの匿名化
            slices.append(ds.pixel_array)
    if not slices:
        raise ValueError('No DICOM files found in the directory.')
    volume = np.stack(slices, axis=0)
    return volume

def load_nifti_files(directory):
    """
    複数のNIFTIファイルを読み込んでリストとして返す

    Args:
        directory (str): NIFTIファイルが含まれるディレクトリのパス

    Returns:
        list of numpy.ndarray: NIFTIデータのリスト
    """
    nifti_data_list = []
    for filename in sorted(os.listdir(directory)):
        if filename.lower().endswith(('.nii', '.nii.gz')):
            file_path = os.path.join(directory, filename)
            nifti_img = nib.load(file_path)
            data = nifti_img.get_fdata()
            nifti_data_list.append(data)
    if not nifti_data_list:
        raise ValueError('No NIFTI files found in the directory.')
    return nifti_data_list

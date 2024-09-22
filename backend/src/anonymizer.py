# utils/anonymizer.py

def anonymize_dicom(ds):
    """
    DICOMデータセットを匿名化する

    Args:
        ds (pydicom.Dataset): DICOMデータセット

    Returns:
        pydicom.Dataset: 匿名化されたDICOMデータセット
    """
    # 個人情報フィールドをクリアまたは置き換える
    ds.PatientName = 'Anonymous'
    ds.PatientID = '000000'
    ds.PatientBirthDate = ''
    ds.PatientSex = ''
    ds.InstitutionName = ''
    ds.ReferringPhysicianName = ''
    ds.PatientAddress = ''
    # 必要に応じて他のフィールドも匿名化
    return ds

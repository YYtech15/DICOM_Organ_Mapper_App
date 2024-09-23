import React, { useState } from 'react';

interface ImageData {
  view: string;
  type: string;
  url: string;
}

interface FileUploadProps {
  onUploadSuccess: (imageData: ImageData[]) => void;
  onUploadStart: () => void;
}

const FileUpload: React.FC<FileUploadProps> = ({
  onUploadSuccess,
  onUploadStart,
}) => {
  const [dicomFiles, setDicomFiles] = useState<FileList | null>(null);
  const [niftiFiles, setNiftiFiles] = useState<FileList | null>(null);

  const handleDicomFilesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setDicomFiles(e.target.files);
    }
  };

  const handleNiftiFilesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setNiftiFiles(e.target.files);
    }
  };

  const handleUpload = () => {
    if (!dicomFiles && !niftiFiles) {
      alert('ファイルを選択してください。');
      return;
    }

    onUploadStart();

    const formData = new FormData();

    if (dicomFiles) {
      for (let i = 0; i < dicomFiles.length; i++) {
        formData.append('dicom_files', dicomFiles[i]);
      }
    }

    if (niftiFiles) {
      for (let i = 0; i < niftiFiles.length; i++) {
        formData.append('nifti_files', niftiFiles[i]);
      }
    }

    fetch('http://localhost:5000/upload', {
      method: 'POST',
      credentials: 'include',
      body: formData,
    })
      .then(response => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error('Upload failed');
        }
      })
      .then(data => {
        onUploadSuccess(data.images);
      })
      .catch(error => {
        console.error('Upload error:', error);
        alert('アップロード中にエラーが発生しました: ' + error.message);
      });
  };

  return (
    <div className="file-upload-container">
      <div>
        <label>DICOMフォルダを選択（複数選択可能）:</label>
        <input
          type="file"
          multiple
          onChange={handleDicomFilesChange}
          webkitdirectory=""
          mozdirectory=""
        />
      </div>
      <div>
        <label>ROIフォルダを選択（ROIフォルダ内にNIFTIファイルがあること）:</label>
        <input
          type="file"
          multiple
          onChange={handleNiftiFilesChange}
          webkitdirectory=""
          mozdirectory=""
        />
      </div>
      <button onClick={handleUpload}>アップロード</button>
    </div>
  );
};

export default FileUpload;
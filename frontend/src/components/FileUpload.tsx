// src/components/FileUpload.tsx

import React, { useState } from 'react';

interface FileUploadProps {
  onUploadSuccess: (imageUrl: string) => void;
  onUploadStart: () => void;
  dicomShape: number[] | null;
  midpoints: number[];
  onMidpointChange: (axisIndex: number, value: number) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({
  onUploadSuccess,
  onUploadStart,
  dicomShape,
  midpoints,
  onMidpointChange,
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

    // midpointsをフォームデータに追加
    formData.append('midpoints', midpoints.join(','));

    fetch('http://localhost:5000/upload', {
      method: 'POST',
      credentials: 'include',
      body: formData,
    })
      .then(response => {
        if (response.ok) {
          return response.blob();
        } else {
          return response.json().then(errorData => {
            throw new Error(errorData.error || 'Unknown error');
          });
        }
      })
      .then(blob => {
        const imageUrl = URL.createObjectURL(blob);
        onUploadSuccess(imageUrl);
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

      {dicomShape && midpoints.length === 3 && (
        <div className="midpoint-sliders">
          {['Sagittal', 'Coronal', 'Axial'].map((axis, index) => (
            <div key={axis}>
              <label>
                {axis} Midpoint: {midpoints[index]}
              </label>
              <input
                type="range"
                min="0"
                max={dicomShape[index] - 1}
                value={midpoints[index]}
                onChange={(e) => onMidpointChange(index, parseInt(e.target.value))}
              />
            </div>
          ))}
        </div>
      )}

      <button onClick={handleUpload}>アップロード</button>
    </div>
  );
};

export default FileUpload;
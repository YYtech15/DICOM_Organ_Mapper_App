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
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          DICOMフォルダを選択（複数選択可能）:
        </label>
        <input
          type="file"
          multiple
          onChange={handleDicomFilesChange}
          webkitdirectory=""
          mozdirectory=""
          className="mt-1 block w-full text-sm text-gray-500
            file:mr-4 file:py-2 file:px-4
            file:rounded-full file:border-0
            file:text-sm file:font-semibold
            file:bg-violet-50 file:text-violet-700
            hover:file:bg-violet-100"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          ROIフォルダを選択（ROIフォルダ内にNIFTIファイルがあること）:
        </label>
        <input
          type="file"
          multiple
          onChange={handleNiftiFilesChange}
          webkitdirectory=""
          mozdirectory=""
          className="mt-1 block w-full text-sm text-gray-500
            file:mr-4 file:py-2 file:px-4
            file:rounded-full file:border-0
            file:text-sm file:font-semibold
            file:bg-violet-50 file:text-violet-700
            hover:file:bg-violet-100"
        />
      </div>
      <button 
        onClick={handleUpload}
        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
      >
        アップロード
      </button>
    </div>
  );
};

export default FileUpload;
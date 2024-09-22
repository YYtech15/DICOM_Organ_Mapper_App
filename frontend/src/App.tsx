// src/App.tsx

import React, { useState, useEffect } from 'react';
import { ClipLoader } from 'react-spinners';
import FileUpload from './components/FileUpload';

const App: React.FC = () => {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [loggedIn, setLoggedIn] = useState(false);
  const [dicomShape, setDicomShape] = useState<number[] | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [midpoints, setMidpoints] = useState<number[]>([]);

  useEffect(() => {
    // 自動ログイン処理
    const loginData = new FormData();
    loginData.append('username', 'admin');
    loginData.append('password', 'password123');

    fetch('http://localhost:5000/login', {
      method: 'POST',
      credentials: 'include',
      body: loginData,
    })
      .then(response => response.json())
      .then(data => {
        if (data.status === 'success') {
          console.log('Logged in successfully');
          setLoggedIn(true);
        } else {
          console.error('Login failed:', data.error);
          alert('自動ログインに失敗しました: ' + data.error);
        }
      })
      .catch(error => {
        console.error('Login error:', error);
        alert('自動ログイン中にエラーが発生しました: ' + error.message);
      });
  }, []);

  const handleUploadSuccess = (imageUrl: string) => {
    setImageUrl(imageUrl);
    setIsLoading(false);

    // DICOMデータの形状を取得
    fetch('http://localhost:5000/get_dicom_shape', { credentials: 'include' })
      .then(response => response.json())
      .then(data => {
        if (data.shape) {
          setDicomShape(data.shape);
          // midpointsを初期化
          const initialMidpoints = data.shape.map((size: number) => Math.floor(size / 2));
          setMidpoints(initialMidpoints);
        } else {
          alert('DICOMデータの形状を取得できませんでした。');
        }
      })
      .catch(error => {
        console.error('Error fetching DICOM shape:', error);
        alert('DICOMデータの形状を取得中にエラーが発生しました。');
      });
  };

  const handleUploadStart = () => {
    setIsLoading(true);
  };

  const regenerateImage = () => {
    setIsLoading(true);
    const formData = new FormData();
    formData.append('midpoints', midpoints.join(','));

    fetch('http://localhost:5000/regenerate', {
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
        setImageUrl(imageUrl);
        setIsLoading(false);
      })
      .catch(error => {
        console.error('Regenerate error:', error);
        alert('画像の再生成中にエラーが発生しました: ' + error.message);
        setIsLoading(false);
      });
  };

  const handleMidpointChange = (axisIndex: number, value: number) => {
    const newMidpoints = [...midpoints];
    newMidpoints[axisIndex] = value;
    setMidpoints(newMidpoints);
  };

  return (
    <div className="app-container">
      <h1>DICOM+ROIビューアー</h1>
      {loggedIn ? (
        isLoading ? (
          <div className="loading-container">
            <ClipLoader color="#123abc" loading={isLoading} size={50} />
            <p>処理中です。しばらくお待ちください...</p>
          </div>
        ) : !imageUrl ? (
          <FileUpload
            onUploadSuccess={handleUploadSuccess}
            onUploadStart={handleUploadStart}
            dicomShape={dicomShape}
            midpoints={midpoints}
            onMidpointChange={handleMidpointChange}
          />
        ) : (
          <div>
            <h2>処理結果</h2>
            <img
              src={imageUrl}
              alt="Visualization"
              style={{ maxWidth: '100%', height: 'auto' }}
            />
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
                      onChange={(e) => handleMidpointChange(index, parseInt(e.target.value))}
                    />
                  </div>
                ))}
              </div>
            )}
            <div className='regenerate-button'>
              <button onClick={regenerateImage}>画像を再生成</button>
            </div>
          </div>
        )
      ) : (
        <p>ログインしています...</p>
      )}
    </div>
  );
};

export default App;
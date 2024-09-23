import React, { useState, useEffect } from 'react';
import { ClipLoader } from 'react-spinners';
import FileUpload from './components/FileUpload';
import ImageViewer from './components/ImageViewer';

interface ImageData {
  view: string;
  type: string;
  url: string;
}

const App: React.FC = () => {
  const [loggedIn, setLoggedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [images, setImages] = useState<ImageData[]>([]);

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

  const handleUploadSuccess = (imageData: ImageData[]) => {
    console.log('Upload success. Received image data:', imageData);
    setImages(imageData);
    setIsLoading(false);
  };

  const handleUploadStart = () => {
    setIsLoading(true);
  };

  const handleRegenerateRequest = () => {
    setIsLoading(true);
    fetch('http://localhost:5000/regenerate', {
      method: 'POST',
      credentials: 'include',
    })
      .then(response => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error('Regeneration failed');
        }
      })
      .then(data => {
        console.log('Regenerate success. Received image data:', data.images);
        setImages(data.images);
        setIsLoading(false);
      })
      .catch(error => {
        console.error('Regenerate error:', error);
        alert('画像の再生成中にエラーが発生しました: ' + error.message);
        setIsLoading(false);
      });
  };

  useEffect(() => {
    console.log('Current images state:', images);
  }, [images]);

  return (
    <div className="app-container">
      <h1>DICOM+ROIビューアー</h1>
      {loggedIn ? (
        isLoading ? (
          <div className="loading-container">
            <ClipLoader color="#123abc" loading={isLoading} size={50} />
            <p>処理中です。しばらくお待ちください...</p>
          </div>
        ) : images.length === 0 ? (
          <FileUpload
            onUploadSuccess={handleUploadSuccess}
            onUploadStart={handleUploadStart}
          />
        ) : (
          <ImageViewer 
            images={images} 
            onRegenerateRequest={handleRegenerateRequest}
          />
        )
      ) : (
        <p>ログインしています...</p>
      )}
    </div>
  );
};

export default App;
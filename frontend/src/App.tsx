'use client'

import React, { useState, useEffect } from 'react';
import { ClipLoader } from 'react-spinners';
import FileUpload from './components/FileUpload';
import ImageViewer from './components/ImageViewer';

interface ImageData {
  view: string;
  type: string;
  url: string;
}

export default function App() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [images, setImages] = useState<ImageData[]>([]);

  useEffect(() => {
    // Auto login process
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
    <div className="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12">
      <div className="relative py-3 sm:max-w-xl sm:mx-auto">
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 to-light-blue-500 shadow-lg transform -skew-y-6 sm:skew-y-0 sm:-rotate-6 sm:rounded-3xl"></div>
        <div className="relative px-4 py-10 bg-white shadow-lg sm:rounded-3xl sm:p-20">
          <h1 className="text-3xl font-bold text-gray-900 mb-8 text-center">DICOM+ROIビューアー</h1>
          {loggedIn ? (
            isLoading ? (
              <div className="flex flex-col items-center justify-center">
                <ClipLoader color="#4F46E5" loading={isLoading} size={50} />
                <p className="mt-4 text-gray-600">処理中です。しばらくお待ちください...</p>
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
            <p className="text-center text-gray-600">ログインしています...</p>
          )}
        </div>
      </div>
    </div>
  );
}
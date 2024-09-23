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
  const [dicomShape, setDicomShape] = useState<number[]>([]);

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
    fetchDicomShape();
  };

  const handleUploadStart = () => {
    setIsLoading(true);
  };

  const fetchDicomShape = () => {
    fetch('http://localhost:5000/get_dicom_shape', {
      method: 'GET',
      credentials: 'include',
    })
      .then(response => response.json())
      .then(data => {
        if (data.shape) {
          setDicomShape(data.shape);
        } else {
          console.error('Failed to get DICOM shape:', data.error);
        }
      })
      .catch(error => {
        console.error('Error fetching DICOM shape:', error);
      });
  };

  const handleRegenerateRequest = (midpoints: number[]) => {
    setIsLoading(true);
    fetch('http://localhost:5000/regenerate', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ midpoints }),
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
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-center">
          DICOM+ROIビューアー
        </h1>

        {loggedIn ? (
          isLoading ? (
            <div className="flex justify-center items-center h-64">
              <ClipLoader color="#4A90E2" size={50} />
              <p className="ml-4 text-xl">処理中です。しばらくお待ちください...</p>
            </div>
          ) : images.length === 0 ? (
            <FileUpload onUploadSuccess={handleUploadSuccess} onUploadStart={handleUploadStart} />
          ) : (
            <ImageViewer 
              images={images} 
              onRegenerateRequest={handleRegenerateRequest}
              dicomShape={dicomShape}
            />
          )
        ) : (
          <p className="text-center text-xl">ログインしています...</p>
        )}
      </div>
    </div>
  );
}
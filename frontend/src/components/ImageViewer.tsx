import React, { useState, useEffect, useRef, useCallback } from 'react';
import Controls from './Controls';

interface ImageData {
  view: string;
  type: string;
  url: string;
}

interface ImageViewerProps {
  images: ImageData[];
  onRegenerateRequest: (midpoints: number[]) => void;
  dicomShape: number[];
}

interface ImageState {
  zoomLevel: number;
  panPosition: { x: number; y: number };
}

export default function ImageViewer({ images, onRegenerateRequest, dicomShape }: ImageViewerProps) {
  const [midpoints, setMidpoints] = useState<number[]>([]);
  const [imageStates, setImageStates] = useState<Record<string, ImageState>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);
  const containerRefs = useRef<Record<string, HTMLDivElement | null>>({});
  const isDragging = useRef<Record<string, boolean>>({});
  const lastPosition = useRef<Record<string, { x: number; y: number }>>({});

  useEffect(() => {
    if (dicomShape.length === 3) {
      setMidpoints(dicomShape.map(dim => Math.floor(dim / 2)));
    }

    const initialStates: Record<string, ImageState> = {};
    images.forEach(img => {
      const key = `${img.view}-${img.type}`;
      initialStates[key] = { zoomLevel: 1, panPosition: { x: 0, y: 0 } };
    });
    setImageStates(initialStates);
  }, [dicomShape, images]);

  const handleZoomChange = (view: string, type: string, value: number) => {
    const key = `${view}-${type}`;
    setImageStates(prev => ({
      ...prev,
      [key]: {
        ...prev[key],
        zoomLevel: value,
        panPosition: value === 1 ? { x: 0, y: 0 } : prev[key].panPosition
      }
    }));
  };

  const handleMidpointChange = (index: number, value: number) => {
    const newMidpoints = [...midpoints];
    newMidpoints[index] = value;
    setMidpoints(newMidpoints);
  };

  const handleMouseDown = (view: string, type: string, e: React.MouseEvent) => {
    const key = `${view}-${type}`;
    isDragging.current[key] = true;
    lastPosition.current[key] = { x: e.clientX, y: e.clientY };
  };

  const handleMouseMove = useCallback((view: string, type: string, e: MouseEvent) => {
    const key = `${view}-${type}`;
    if (isDragging.current[key]) {
      const deltaX = e.clientX - lastPosition.current[key].x;
      const deltaY = e.clientY - lastPosition.current[key].y;
      setImageStates(prev => {
        const currentState = prev[key];
        const containerWidth = containerRefs.current[key]?.clientWidth || 0;
        const containerHeight = containerRefs.current[key]?.clientHeight || 0;
        const imageWidth = containerWidth * currentState.zoomLevel;
        const imageHeight = containerHeight * currentState.zoomLevel;
        const maxPanX = (imageWidth - containerWidth) / 2;
        const maxPanY = (imageHeight - containerHeight) / 2;

        const newPanX = Math.max(-maxPanX, Math.min(maxPanX, currentState.panPosition.x + deltaX / currentState.zoomLevel));
        const newPanY = Math.max(-maxPanY, Math.min(maxPanY, currentState.panPosition.y + deltaY / currentState.zoomLevel));

        return {
          ...prev,
          [key]: {
            ...currentState,
            panPosition: { x: newPanX, y: newPanY }
          }
        };
      });
      lastPosition.current[key] = { x: e.clientX, y: e.clientY };
    }
  }, []);

  const handleMouseUp = useCallback((view: string, type: string) => {
    const key = `${view}-${type}`;
    isDragging.current[key] = false;
  }, []);

  useEffect(() => {
    const handleGlobalMouseMove = (e: MouseEvent) => {
      Object.keys(isDragging.current).forEach(key => {
        if (isDragging.current[key]) {
          const [view, type] = key.split('-');
          handleMouseMove(view, type, e);
        }
      });
    };

    const handleGlobalMouseUp = () => {
      Object.keys(isDragging.current).forEach(key => {
        if (isDragging.current[key]) {
          const [view, type] = key.split('-');
          handleMouseUp(view, type);
        }
      });
    };

    window.addEventListener('mousemove', handleGlobalMouseMove);
    window.addEventListener('mouseup', handleGlobalMouseUp);

    return () => {
      window.removeEventListener('mousemove', handleGlobalMouseMove);
      window.removeEventListener('mouseup', handleGlobalMouseUp);
    };
  }, [handleMouseMove, handleMouseUp]);

  const groupedImages = images.reduce((acc, img) => {
    if (!acc[img.view]) {
      acc[img.view] = {};
    }
    acc[img.view][img.type] = img.url;
    return acc;
  }, {} as Record<string, Record<string, string>>);

  const handleDownload = async () => {
    try {
      setIsLoading(true);
      setDownloadError(null);
      
      const response = await fetch('http://localhost:5000/download_array', {
        method: 'GET',
        credentials: 'include',
      });
  
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Download failed');
      }
  
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.indexOf('text/plain') === -1) {
        throw new Error('Received incorrect file type');
      }
  
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = 'voxel.inp'; // Adjusted to match backend filename
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading file:', error);
      setDownloadError(error instanceof Error ? error.message : 'An unknown error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {Object.entries(groupedImages).map(([view, types]) => (
        <div key={view} className="bg-white shadow-md rounded-lg overflow-hidden">
          <h3 className="text-lg font-semibold bg-gray-100 px-4 py-2 border-b">{view}</h3>
          <div className="p-4">
            <div className="space-y-4">
              {Object.entries(types).map(([type, url]) => {
                const key = `${view}-${type}`;
                const { zoomLevel, panPosition } = imageStates[key] || { zoomLevel: 1, panPosition: { x: 0, y: 0 } };
                return (
                  <div key={type} className="space-y-2">
                    <h4 className="text-sm font-medium text-gray-600">{type}</h4>
                    <div
                      ref={el => containerRefs.current[key] = el}
                      className="relative overflow-hidden rounded-md"
                      style={{
                        height: '400px',
                        width: '100%',
                        cursor: zoomLevel > 1 ? 'move' : 'default'
                      }}
                      onMouseDown={(e) => handleMouseDown(view, type, e)}
                    >
                      <div
                        style={{
                          transform: `scale(${zoomLevel}) translate(${panPosition.x}px, ${panPosition.y}px)`,
                          transformOrigin: 'center',
                          height: '100%',
                          width: '100%',
                          transition: 'transform 0.1s ease-out'
                        }}
                      >
                        <img
                          src={url}
                          alt={`${view} ${type}`}
                          className="h-full w-full object-contain"
                          onError={(e) => console.error(`Error loading image: ${url}`, e)}
                          onLoad={() => console.log(`Image loaded successfully: ${url}`)}
                        />
                      </div>
                    </div>
                    <Controls
                      zoomLevel={zoomLevel}
                      onZoomChange={(value) => handleZoomChange(view, type, value)}
                    />
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      ))}
      <div className="space-y-4">
        <div className="flex flex-col space-y-2">
          {['Sagittal', 'Coronal', 'Axial'].map((view, index) => (
            <div key={view} className="flex items-center space-x-2">
              <label htmlFor={`midpoint-${view}`} className="w-20">{view}:</label>
              <input
                id={`midpoint-${view}`}
                type="range"
                min="0"
                max={dicomShape[index] - 1}
                value={midpoints[index]}
                onChange={(e) => handleMidpointChange(index, parseInt(e.target.value))}
                className="w-full"
              />
              <span className="w-12 text-right">{midpoints[index]}</span>
            </div>
          ))}
        </div>
        <div className="flex justify-center">
          <button
            className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
            onClick={() => onRegenerateRequest(midpoints)}
          >
            画像を再生成
          </button>
        </div>
        <button
          className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
          onClick={handleDownload}
          disabled={isLoading}
        >
          {isLoading ? 'Downloading...' : '3D配列データをダウンロード'}
        </button>
      {isLoading && <p>ダウンロード中です。お待ちください...</p>}
      {downloadError && <p style={{ color: 'red' }}>エラー: {downloadError}</p>}
      </div>
    </div>
  );
}
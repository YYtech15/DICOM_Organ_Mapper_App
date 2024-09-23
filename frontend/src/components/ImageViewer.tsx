import React, { useState, useEffect } from 'react';
import Controls from './Controls';

interface ImageData {
  view: string;
  type: string;
  url: string;
}

interface ImageViewerProps {
  images: ImageData[];
  onRegenerateRequest: () => void;
}

export default function ImageViewer({ images, onRegenerateRequest }: ImageViewerProps) {
  const [zoomLevel, setZoomLevel] = useState(1);
  const [contrastLevel, setContrastLevel] = useState(1);

  useEffect(() => {
    console.log('ImageViewer received images:', images);
  }, [images]);

  const handleZoomChange = (value: number) => {
    setZoomLevel(value);
  };

  const handleContrastChange = (value: number) => {
    setContrastLevel(value);
  };

  const groupedImages = images.reduce((acc, img) => {
    if (!acc[img.view]) {
      acc[img.view] = {};
    }
    acc[img.view][img.type] = img.url;
    return acc;
  }, {} as Record<string, Record<string, string>>);

  console.log('Grouped images:', groupedImages);

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Object.entries(groupedImages).map(([view, types]) => (
          <div key={view} className="bg-white shadow-md rounded-lg overflow-hidden">
            <h3 className="text-lg font-semibold bg-gray-100 px-4 py-2 border-b">{view}</h3>
            <div className="p-4 space-y-4">
              {Object.entries(types).map(([type, url]) => (
                <div key={type} className="space-y-2">
                  <h4 className="text-sm font-medium text-gray-600">{type}</h4>
                  <div
                    className="relative overflow-hidden rounded-md"
                    style={{ 
                      transform: `scale(${zoomLevel})`,
                      transformOrigin: 'top left',
                    }}
                  >
                    <img 
                      src={url} 
                      alt={`${view} ${type}`} 
                      className="w-full h-auto"
                      style={{ filter: `contrast(${contrastLevel})` }}
                      onError={(e) => console.error(`Error loading image: ${url}`, e)}
                      onLoad={() => console.log(`Image loaded successfully: ${url}`)}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
      <Controls
        zoomLevel={zoomLevel}
        onZoomChange={handleZoomChange}
        contrastLevel={contrastLevel}
        onContrastChange={handleContrastChange}
      />
      <div className="flex justify-center">
        <button 
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          onClick={onRegenerateRequest}
        >
          画像を再生成
        </button>
      </div>
    </div>
  );
}
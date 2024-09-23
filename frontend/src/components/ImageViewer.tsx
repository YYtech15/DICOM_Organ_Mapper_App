import React, { useState, useEffect } from 'react';
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

export default function ImageViewer({ images, onRegenerateRequest, dicomShape }: ImageViewerProps) {
  const [zoomLevel, setZoomLevel] = useState(1);
  const [midpoints, setMidpoints] = useState<number[]>([]);

  useEffect(() => {
    console.log('ImageViewer received images:', images);
    // Initialize midpoints with default values (half of each dimension)
    if (dicomShape.length === 3) {
      setMidpoints(dicomShape.map(dim => Math.floor(dim / 2)));
    }
  }, [images, dicomShape]);

  const handleZoomChange = (value: number) => {
    setZoomLevel(value);
  };

  const handleMidpointChange = (index: number, value: number) => {
    const newMidpoints = [...midpoints];
    newMidpoints[index] = value;
    setMidpoints(newMidpoints);
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
      />
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
      </div>
    </div>
  );
}
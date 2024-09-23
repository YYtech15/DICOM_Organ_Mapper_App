import React, { useState, useEffect } from 'react';
import Controls from './Controls';

interface SliceViewerProps {
  axis: 'sagittal' | 'coronal' | 'axial';
  maxIndex: number;
}

export default function SliceViewer({ axis, maxIndex }: SliceViewerProps) {
  const [sliceIndex, setSliceIndex] = useState(Math.floor(maxIndex / 2));
  const [imageSrc, setImageSrc] = useState('');
  const [zoomLevel, setZoomLevel] = useState(1);

  useEffect(() => {
    fetch(`/get_slice?axis=${axis}&index=${sliceIndex}`, { credentials: 'include' })
      .then(response => response.blob())
      .then(blob => {
        setImageSrc(URL.createObjectURL(blob));
      })
      .catch(error => {
        console.error('Error fetching slice image:', error);
      });
  }, [sliceIndex, axis]);

  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSliceIndex(Number(e.target.value));
  };

  const handleZoomChange = (value: number) => {
    setZoomLevel(value);
  };

  return (
    <div className="bg-white shadow-md rounded-lg overflow-hidden h-full flex flex-col">
      <h2 className="text-lg font-semibold bg-gray-100 px-4 py-2 border-b">{axis} View</h2>
      <div className="p-4 flex-grow flex flex-col">
        <div className="flex-grow relative overflow-hidden rounded-md">
          <div
            className="absolute inset-0 flex items-center justify-center"
            style={{ 
              transform: `scale(${zoomLevel})`,
              transformOrigin: 'center',
            }}
          >
            <img 
              src={imageSrc} 
              alt={`${axis} slice`} 
              className="max-w-full max-h-full object-contain"
            />
          </div>
        </div>
        <div className="mt-4 space-y-2">
          <label htmlFor={`sliceIndex-${axis}`} className="block text-sm font-medium text-gray-700">
            Slice Index: {sliceIndex}
          </label>
          <input
            id={`sliceIndex-${axis}`}
            type="range"
            min="0"
            max={maxIndex}
            value={sliceIndex}
            onChange={handleSliderChange}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
        </div>
        <Controls
          zoomLevel={zoomLevel}
          onZoomChange={handleZoomChange}
        />
      </div>
    </div>
  );
}
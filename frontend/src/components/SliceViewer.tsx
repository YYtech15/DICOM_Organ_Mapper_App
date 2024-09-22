// src/components/SliceViewer.tsx
import React, { useState, useEffect } from 'react';
import Controls from './Controls';

interface SliceViewerProps {
  axis: 'sagittal' | 'coronal' | 'axial';
  maxIndex: number;
}

const SliceViewer: React.FC<SliceViewerProps> = ({ axis, maxIndex }) => {
  const [sliceIndex, setSliceIndex] = useState(Math.floor(maxIndex / 2));
  const [imageSrc, setImageSrc] = useState('');
  const [zoomLevel, setZoomLevel] = useState(1);
  const [contrastLevel, setContrastLevel] = useState(1);

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

  const handleContrastChange = (value: number) => {
    setContrastLevel(value);
  };

  return (
    <div className="slice-viewer">
      <h2>{axis} View</h2>
      <div
        className="image-container"
        style={{ transform: `scale(${zoomLevel})`, filter: `contrast(${contrastLevel})` }}
      >
        <img src={imageSrc} alt={`${axis} slice`} />
      </div>
      <input
        type="range"
        min="0"
        max={maxIndex}
        value={sliceIndex}
        onChange={handleSliderChange}
      />
      <Controls
        zoomLevel={zoomLevel}
        onZoomChange={handleZoomChange}
        contrastLevel={contrastLevel}
        onContrastChange={handleContrastChange}
      />
    </div>
  );
};

export default SliceViewer;

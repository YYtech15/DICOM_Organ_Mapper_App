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

const ImageViewer: React.FC<ImageViewerProps> = ({ images, onRegenerateRequest }) => {
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
    <div className="image-viewer">
      <div className="image-grid">
        {Object.entries(groupedImages).map(([view, types]) => (
          <div key={view} className="image-group">
            <h3>{view}</h3>
            <div className="image-row">
              {Object.entries(types).map(([type, url]) => (
                <div key={type} className="image-item">
                  <h4>{type}</h4>
                  <div
                    className="image-container"
                    style={{ transform: `scale(${zoomLevel})`, filter: `contrast(${contrastLevel})` }}
                  >
                    <img 
                      src={url} 
                      alt={`${view} ${type}`} 
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
      <button className="regenerate-button" onClick={onRegenerateRequest}>画像を再生成</button>
    </div>
  );
};

export default ImageViewer;
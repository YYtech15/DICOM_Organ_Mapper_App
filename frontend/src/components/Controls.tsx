// src/components/Controls.tsx
import React from 'react';

interface ControlsProps {
  zoomLevel: number;
  onZoomChange: (value: number) => void;
  contrastLevel: number;
  onContrastChange: (value: number) => void;
}

const Controls: React.FC<ControlsProps> = ({
  zoomLevel,
  onZoomChange,
  contrastLevel,
  onContrastChange,
}) => {
  const handleZoomInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onZoomChange(Number(e.target.value));
  };

  const handleContrastInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onContrastChange(Number(e.target.value));
  };

  return (
    <div className="controls">
      <div className="control-group">
        <label>
          ズーム:
          <input
            type="range"
            min="0.5"
            max="2"
            step="0.1"
            value={zoomLevel}
            onChange={handleZoomInputChange}
          />
        </label>
        <span>{zoomLevel.toFixed(1)}x</span>
      </div>
      <div className="control-group">
        <label>
          コントラスト:
          <input
            type="range"
            min="0.5"
            max="2"
            step="0.1"
            value={contrastLevel}
            onChange={handleContrastInputChange}
          />
        </label>
        <span>{contrastLevel.toFixed(1)}x</span>
      </div>
    </div>
  );
};

export default Controls;

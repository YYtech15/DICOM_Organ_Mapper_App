import React from 'react';

interface ControlsProps {
  zoomLevel: number;
  onZoomChange: (value: number) => void;
  contrastLevel: number;
  onContrastChange: (value: number) => void;
}

export default function Controls({
  zoomLevel,
  onZoomChange,
  contrastLevel,
  onContrastChange,
}: ControlsProps) {
  const handleZoomInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onZoomChange(Number(e.target.value));
  };

  const handleContrastInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onContrastChange(Number(e.target.value));
  };

  return (
    <div className="bg-white shadow-md rounded-lg p-6 space-y-4">
      <div className="space-y-2">
        <label htmlFor="zoom" className="block text-sm font-medium text-gray-700">
          ズーム: {zoomLevel.toFixed(1)}x
        </label>
        <input
          id="zoom"
          type="range"
          min="0.5"
          max="2"
          step="0.1"
          value={zoomLevel}
          onChange={handleZoomInputChange}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
        />
      </div>
      <div className="space-y-2">
        <label htmlFor="contrast" className="block text-sm font-medium text-gray-700">
          コントラスト: {contrastLevel.toFixed(1)}x
        </label>
        <input
          id="contrast"
          type="range"
          min="0.5"
          max="2"
          step="0.1"
          value={contrastLevel}
          onChange={handleContrastInputChange}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
        />
      </div>
    </div>
  );
}
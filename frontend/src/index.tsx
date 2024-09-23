// src/index.tsx

import React from 'react';
import ReactDOM from 'react-dom/client';  // 変更点：'react-dom/client'からインポート
import App from './App';
import './styles/App.css';
import './styles/index.css';

const rootElement = document.getElementById('root');
if (rootElement) {
  const root = ReactDOM.createRoot(rootElement);  // createRootを使用
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
} else {
  console.error('Failed to find the root element.');
}

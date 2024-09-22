// src/global.d.ts

import * as React from 'react';

declare module 'react' {
  interface InputHTMLAttributes<T> extends React.HTMLAttributes<T> {
    webkitdirectory?: string;
    mozdirectory?: string;
    directory?: string;
  }
}

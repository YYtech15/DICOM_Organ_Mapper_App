// src/utils/api.ts

export const uploadFile = async (file: File): Promise<boolean> => {
    const formData = new FormData();
    formData.append('file', file);
  
    const response = await fetch('/upload', {
      method: 'POST',
      credentials: 'include',
      body: formData,
    });
    const data = await response.json();
    return data.status === 'success';
  };
  
  export const getMaxIndices = async (): Promise<{ sagittal: number; coronal: number; axial: number }> => {
    const response = await fetch('/get_max_indices', { credentials: 'include' });
    const data = await response.json();
    return data;
  };
  
  export const getSliceImage = async (axis: string, index: number): Promise<string> => {
    const response = await fetch(`/get_slice?axis=${axis}&index=${index}`, { credentials: 'include' });
    const blob = await response.blob();
    return URL.createObjectURL(blob);
  };
  
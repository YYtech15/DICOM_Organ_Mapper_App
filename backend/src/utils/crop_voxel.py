import numpy as np

def crop_3d_array(arr):
    """
    Crops a 3D numpy array to the minimal size that encloses all non-zero elements.

    Parameters:
    arr (numpy.ndarray): A 3D numpy array of shape (512, 512, 970).

    Returns:
    numpy.ndarray: The cropped array containing the 3D object with minimal empty space.
    """
    # Find indices where elements are non-zero
    non_zero_indices = np.array(np.nonzero(arr))
    
    # Compute the minimal and maximal indices along each axis
    min_indices = np.min(non_zero_indices, axis=1)
    max_indices = np.max(non_zero_indices, axis=1) + 1  # Add 1 because slice end is exclusive
    
    # Create slices for each dimension
    slices = [slice(min_idx, max_idx) for min_idx, max_idx in zip(min_indices, max_indices)]
    
    # Use tuple(slices) to slice the array
    cropped_arr = arr[tuple(slices)]
    print("Cropped shape:", cropped_arr.shape)
    return cropped_arr

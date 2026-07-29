"""Laplacian Variance sharpness metric."""

from typing import Union
import numpy as np
import cv2
from .base import SharpnessMetric


class LaplacianVarianceSharpness(SharpnessMetric):
    """Laplacian Variance sharpness metric.
    
    This method calculates sharpness as the variance of the Laplacian kernel response.
    Higher variance indicates sharper images with more edges.
    
    Method: Variance of Laplacian kernel response.
    """

    def __init__(self, ksize: int = 1):
        """Initialize Laplacian Variance sharpness calculator.
        
        Args:
            ksize: Size of the kernel (default: 1)
        """
        self.ksize = ksize

    def calculate(self, image: Union[np.ndarray, str]) -> float:
        """Calculate Laplacian Variance sharpness score.
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            float: Laplacian Variance sharpness score
        """
        img = self._load_image(image)
        
        # Apply Laplacian filter
        laplacian = cv2.Laplacian(img, cv2.CV_64F, ksize=2*self.ksize + 1)
        
        # Calculate variance
        variance = np.var(laplacian)
        
        return float(variance)

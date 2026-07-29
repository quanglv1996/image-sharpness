"""Tenengrad sharpness metric using Sobel operator."""

from typing import Union
import numpy as np
import cv2
from .base import SharpnessMetric


class TenengradSharpness(SharpnessMetric):
    """Tenengrad sharpness metric using Sobel operator.
    
    This method calculates sharpness based on the sum of Sobel gradients.
    Higher values indicate sharper images.
    
    Method: Tenengrad = sum(Gx^2 + Gy^2) where Gx, Gy are Sobel gradients.
    """

    def __init__(self, ksize: int = 3):
        """Initialize Tenengrad sharpness calculator.
        
        Args:
            ksize: Kernel size for Sobel operator (must be odd, default: 3)
        """
        if ksize % 2 == 0:
            raise ValueError("Kernel size must be odd")
        self.ksize = ksize

    def calculate(self, image: Union[np.ndarray, str]) -> float:
        """Calculate Tenengrad sharpness score.
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            float: Tenengrad sharpness score
        """
        img = self._load_image(image)
        
        # Calculate Sobel gradients
        gx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=self.ksize)
        gy = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=self.ksize)
        
        # Calculate Tenengrad
        tenengrad = np.sum(gx ** 2 + gy ** 2)
        
        return float(tenengrad)

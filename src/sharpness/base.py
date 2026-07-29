"""Base class for image sharpness metrics."""

from abc import ABC, abstractmethod
from typing import Union
import numpy as np
import cv2


class SharpnessMetric(ABC):
    """Abstract base class for sharpness metrics.
    
    This class defines the interface for all sharpness calculation methods.
    Following Single Responsibility Principle: each subclass calculates
    sharpness using a specific method.
    """

    @abstractmethod
    def calculate(self, image: Union[np.ndarray, str]) -> float:
        """Calculate sharpness score for an image.
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            float: Sharpness score
        """
        pass

    def _load_image(self, image: Union[np.ndarray, str]) -> np.ndarray:
        """Load image from file or return if already loaded.
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            np.ndarray: Grayscale image as numpy array
        """
        if isinstance(image, str):
            img = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
            if img is None:
                raise ValueError(f"Cannot load image from {image}")
            return img
        elif isinstance(image, np.ndarray):
            if len(image.shape) == 3:
                return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            return image
        else:
            raise TypeError("Image must be a numpy array or file path")

    def __call__(self, image: Union[np.ndarray, str]) -> float:
        """Allow using instance as a callable function."""
        return self.calculate(image)

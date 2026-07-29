"""Contrast measurement metrics."""

from typing import Union
import numpy as np
import cv2
from .base import SharpnessMetric


class ContrastMetric(SharpnessMetric):
    """Abstract base class for contrast metrics."""
    
    def calculate(self, image: Union[np.ndarray, str]) -> float:
        """Calculate contrast score."""
        pass


class RMSContrast(ContrastMetric):
    """RMS (Root Mean Square) Contrast metric.
    
    Measures the standard deviation of pixel values.
    Range: 0-127.5 (0=uniform, higher=more contrast)
    
    Formula: sqrt(mean((I - mean(I))^2))
    """
    
    def calculate(self, image: Union[np.ndarray, str]) -> float:
        """Calculate RMS contrast.
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            float: RMS contrast value (0-127.5)
        """
        img = self._load_image(image).astype(np.float32)
        mean_val = np.mean(img)
        rms = float(np.sqrt(np.mean((img - mean_val) ** 2)))
        return rms


class MichelsonContrast(ContrastMetric):
    """Michelson Contrast metric.
    
    Compares bright and dark regions.
    Range: 0-1 (0=uniform, 1=max contrast)
    
    Formula: (L_max - L_min) / (L_max + L_min)
    
    Best for images with distinct bright and dark regions.
    """
    
    def calculate(self, image: Union[np.ndarray, str]) -> float:
        """Calculate Michelson contrast.
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            float: Michelson contrast (0-1)
        """
        img = self._load_image(image).astype(np.float32)
        
        max_val = np.max(img)
        min_val = np.min(img)
        
        # Avoid division by zero
        if max_val + min_val == 0:
            return 0.0
        
        contrast = (max_val - min_val) / (max_val + min_val)
        return float(contrast)


class WeberContrast(ContrastMetric):
    """Weber Contrast metric.
    
    Compares object to background brightness.
    Range: -1 to +∞ (typically 0-1)
    
    Formula: (I_object - I_background) / I_background
    
    Best for measuring contrast of objects against background.
    """
    
    def __init__(self, background_percentile: float = 10):
        """Initialize Weber contrast calculator.
        
        Args:
            background_percentile: Percentile for background estimation
                                  (default: 10 = darkest 10%)
        """
        if not 0 <= background_percentile <= 100:
            raise ValueError("Percentile must be between 0 and 100")
        self.background_percentile = background_percentile
    
    def calculate(self, image: Union[np.ndarray, str]) -> float:
        """Calculate Weber contrast.
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            float: Weber contrast value
        """
        img = self._load_image(image).astype(np.float32)
        
        # Estimate background (dark pixels)
        background = np.percentile(img, self.background_percentile)
        
        # Avoid division by zero
        if background == 0:
            background = 1
        
        # Calculate mean intensity
        mean_intensity = np.mean(img)
        
        # Weber contrast
        contrast = (mean_intensity - background) / background
        
        return float(np.clip(contrast, -1, 10))  # Clip to reasonable range


class LocalContrast(ContrastMetric):
    """Local Contrast metric.
    
    Measures contrast in local neighborhoods.
    More sensitive to texture and detail.
    """
    
    def __init__(self, kernel_size: int = 31):
        """Initialize local contrast calculator.
        
        Args:
            kernel_size: Size of local neighborhood (default: 31)
        """
        if kernel_size % 2 == 0:
            raise ValueError("Kernel size must be odd")
        self.kernel_size = kernel_size
    
    def calculate(self, image: Union[np.ndarray, str]) -> float:
        """Calculate local contrast.
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            float: Average local contrast
        """
        img = self._load_image(image).astype(np.float32)
        
        # Calculate local mean
        local_mean = cv2.blur(img, (self.kernel_size, self.kernel_size))
        
        # Calculate local standard deviation
        local_sq_mean = cv2.blur(img ** 2, (self.kernel_size, self.kernel_size))
        local_std = np.sqrt(np.maximum(local_sq_mean - local_mean ** 2, 0))
        
        # Average local contrast
        contrast = float(np.mean(local_std))
        
        return contrast


class EdgeContrast(ContrastMetric):
    """Edge-based Contrast metric.
    
    Measures contrast specifically at edges.
    High value indicates strong edges with good contrast.
    """
    
    def __init__(self, kernel_size: int = 3):
        """Initialize edge contrast calculator.
        
        Args:
            kernel_size: Sobel kernel size (default: 3)
        """
        if kernel_size % 2 == 0:
            raise ValueError("Kernel size must be odd")
        self.kernel_size = kernel_size
    
    def calculate(self, image: Union[np.ndarray, str]) -> float:
        """Calculate edge contrast.
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            float: Edge contrast value
        """
        img = self._load_image(image).astype(np.float32)
        
        # Calculate gradients
        gx = cv2.Sobel(img, cv2.CV_32F, 1, 0, ksize=self.kernel_size)
        gy = cv2.Sobel(img, cv2.CV_32F, 0, 1, ksize=self.kernel_size)
        
        # Magnitude of gradients
        magnitude = np.sqrt(gx ** 2 + gy ** 2)
        
        # Edge contrast is the average gradient magnitude at strong gradients
        threshold = np.percentile(magnitude, 75)
        edge_pixels = magnitude[magnitude > threshold]
        
        if len(edge_pixels) > 0:
            edge_contrast = float(np.mean(edge_pixels))
        else:
            edge_contrast = 0.0
        
        return edge_contrast


class DynamicRangeContrast(ContrastMetric):
    """Dynamic Range Contrast metric.
    
    Measures the spread of intensity values.
    Range: 0-255
    
    Formula: max(I) - min(I)
    """
    
    def calculate(self, image: Union[np.ndarray, str]) -> float:
        """Calculate dynamic range contrast.
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            float: Dynamic range (0-255)
        """
        img = self._load_image(image).astype(np.float32)
        
        dynamic_range = float(np.max(img) - np.min(img))
        return dynamic_range

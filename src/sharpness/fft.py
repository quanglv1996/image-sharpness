"""FFT-based sharpness metric."""

from typing import Union
import numpy as np
import cv2
from .base import SharpnessMetric


class FFTSharpness(SharpnessMetric):
    """FFT-based sharpness metric.
    
    This method calculates sharpness in the frequency domain.
    It computes the high-frequency content of the image.
    Higher values indicate sharper images with more high-frequency components.
    
    Method: Sum of high-frequency magnitude in FFT spectrum.
    """

    def __init__(self, high_freq_threshold: float = 0.1):
        """Initialize FFT sharpness calculator.
        
        Args:
            high_freq_threshold: Threshold for high-frequency ratio
                                (default: 0.1, meaning top 10% frequencies)
        """
        if not 0 < high_freq_threshold < 1:
            raise ValueError("high_freq_threshold must be between 0 and 1")
        self.high_freq_threshold = high_freq_threshold

    def calculate(self, image: Union[np.ndarray, str]) -> float:
        """Calculate FFT-based sharpness score.
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            float: FFT sharpness score
        """
        img = self._load_image(image).astype(np.float32)
        
        # Compute FFT
        fft = np.fft.fft2(img)
        fft_shift = np.fft.fftshift(fft)
        
        # Get magnitude spectrum
        magnitude = np.abs(fft_shift)
        
        # Extract high-frequency components
        # Higher frequencies are at the edges of the FFT spectrum
        h, w = magnitude.shape
        center_h, center_w = h // 2, w // 2
        
        # Create mask for high-frequency regions
        # Exclude central low-frequency region
        radius = min(
            int(h * (1 - self.high_freq_threshold) / 2),
            int(w * (1 - self.high_freq_threshold) / 2)
        )
        
        y, x = np.ogrid[:h, :w]
        mask = (np.abs(y - center_h) > radius) | (np.abs(x - center_w) > radius)
        
        # Calculate high-frequency energy
        high_freq_energy = np.sum(magnitude[mask])
        
        return float(high_freq_energy)

"""Noise measurement metrics."""

from typing import Union, Dict
import numpy as np
import cv2
from scipy import signal
from .base import SharpnessMetric


class NoiseMetric(SharpnessMetric):
    """Abstract base class for noise metrics."""
    
    def calculate(self, image: Union[np.ndarray, str]) -> float:
        """Calculate noise level."""
        pass


class LaplacianNoiseEstimation(NoiseMetric):
    """Laplacian kernel-based noise estimation.
    
    Estimates noise using Laplacian filtering.
    Higher values indicate more noise.
    """
    
    def calculate(self, image: Union[np.ndarray, str]) -> float:
        """Estimate noise using Laplacian kernel.
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            float: Noise estimation value
        """
        img = self._load_image(image).astype(np.float32)
        
        # Apply Laplacian filter
        laplacian = cv2.Laplacian(img, cv2.CV_32F)
        
        # Noise estimate is variance of Laplacian
        noise = float(np.var(laplacian))
        
        return noise


class GaussianNoiseEstimation(NoiseMetric):
    """Gaussian noise estimation.
    
    Estimates Gaussian noise using smoothing-based method.
    Compares original and smoothed versions.
    """
    
    def __init__(self, kernel_size: int = 5):
        """Initialize Gaussian noise estimator.
        
        Args:
            kernel_size: Gaussian blur kernel size (default: 5)
        """
        if kernel_size % 2 == 0:
            raise ValueError("Kernel size must be odd")
        self.kernel_size = kernel_size
    
    def calculate(self, image: Union[np.ndarray, str]) -> float:
        """Estimate Gaussian noise level.
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            float: Estimated Gaussian noise standard deviation
        """
        img = self._load_image(image).astype(np.float32)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(img, (self.kernel_size, self.kernel_size), 0)
        
        # Difference between original and blurred
        difference = img - blurred
        
        # Noise estimate is standard deviation of difference
        noise_std = float(np.std(difference))
        
        return noise_std


class SaltPepperNoiseDetection(NoiseMetric):
    """Salt and Pepper noise detection.
    
    Detects impulse noise by looking for extreme pixel values.
    """
    
    def __init__(self, threshold: float = 0.05):
        """Initialize salt & pepper noise detector.
        
        Args:
            threshold: Threshold for noise pixels (default: 0.05 = 5%)
        """
        if not 0 <= threshold <= 1:
            raise ValueError("Threshold must be between 0 and 1")
        self.threshold = threshold
    
    def calculate(self, image: Union[np.ndarray, str]) -> float:
        """Detect salt and pepper noise.
        
        Returns percentage of likely noise pixels.
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            float: Estimated noise ratio (0-1)
        """
        img = self._load_image(image).astype(np.float32)
        
        # Apply median filter
        median = cv2.medianBlur(img.astype(np.uint8), 5)
        median = median.astype(np.float32)
        
        # Detect pixels that are very different from median
        difference = np.abs(img - median)
        
        # Pixels significantly different from median likely noise
        noise_mask = difference > 50  # Threshold for impulse noise
        
        noise_ratio = float(np.sum(noise_mask) / noise_mask.size)
        
        return noise_ratio


class ShotNoiseEstimation(NoiseMetric):
    """Shot noise estimation.
    
    Estimates Poisson/shot noise related to low light conditions.
    Uses statistics of image intensity.
    """
    
    def calculate(self, image: Union[np.ndarray, str]) -> float:
        """Estimate shot noise level.
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            float: Shot noise estimation
        """
        img = self._load_image(image).astype(np.float32)
        
        # Shot noise variance is proportional to intensity
        # Normalize to 0-1
        img_norm = img / 255.0
        
        # Expected shot noise (Poisson)
        shot_noise = np.mean(np.sqrt(np.maximum(img_norm, 0)))
        
        return float(shot_noise)


class StructuralNoiseMetric(NoiseMetric):
    """Structural noise detection.
    
    Detects correlated/structured noise patterns.
    """
    
    def __init__(self, window_size: int = 8):
        """Initialize structural noise detector.
        
        Args:
            window_size: Window size for analysis (default: 8)
        """
        self.window_size = window_size
    
    def calculate(self, image: Union[np.ndarray, str]) -> float:
        """Detect structured noise.
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            float: Structural noise metric
        """
        img = self._load_image(image).astype(np.float32)
        
        # Compute DCT (Discrete Cosine Transform) coefficients
        h, w = img.shape
        
        # Divide image into blocks and compute DCT
        dct_energies = []
        
        for i in range(0, h - self.window_size + 1, self.window_size):
            for j in range(0, w - self.window_size + 1, self.window_size):
                block = img[i:i+self.window_size, j:j+self.window_size]
                dct = cv2.dct(block)
                
                # High-frequency energy (likely noise)
                hf_energy = np.sum(dct[1:, 1:] ** 2)
                dct_energies.append(hf_energy)
        
        if len(dct_energies) == 0:
            return 0.0
        
        # Average high-frequency energy as noise metric
        noise_metric = float(np.mean(dct_energies))
        
        return noise_metric


class CombinedNoiseMetric(NoiseMetric):
    """Combined noise estimation.
    
    Combines multiple noise estimation methods.
    """
    
    def calculate(self, image: Union[np.ndarray, str]) -> float:
        """Estimate overall noise level.
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            float: Combined noise estimation (0-100 scale)
        """
        # Create individual metrics
        gaussian = GaussianNoiseEstimation()
        laplacian = LaplacianNoiseEstimation()
        salt_pepper = SaltPepperNoiseDetection()
        shot = ShotNoiseEstimation()
        
        # Calculate individual scores
        gaussian_noise = gaussian.calculate(image)
        laplacian_noise = laplacian.calculate(image)
        sp_noise = salt_pepper.calculate(image) * 100  # Convert to 0-100
        shot_noise = shot.calculate(image) * 100  # Convert to 0-100
        
        # Normalize and combine
        # Use different weights for different noise types
        combined = (
            min(gaussian_noise / 50 * 100, 100) * 0.3 +
            min(laplacian_noise / 50 * 100, 100) * 0.3 +
            sp_noise * 0.2 +
            shot_noise * 0.2
        )
        
        return float(np.clip(combined, 0, 100))
    
    def get_noise_breakdown(self, image: Union[np.ndarray, str]) -> Dict[str, float]:
        """Get detailed noise breakdown.
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            dict: Individual noise measurements
        """
        return {
            'gaussian': float(GaussianNoiseEstimation().calculate(image)),
            'laplacian': float(LaplacianNoiseEstimation().calculate(image)),
            'salt_pepper': float(SaltPepperNoiseDetection().calculate(image)),
            'shot': float(ShotNoiseEstimation().calculate(image))
        }

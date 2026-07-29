"""Brightness (Exposure) measurement metrics."""

from typing import Union, Dict, Tuple
import numpy as np
import cv2
from .base import SharpnessMetric


class BrightnessMetric(SharpnessMetric):
    """Abstract base class for brightness metrics."""
    
    def calculate(self, image: Union[np.ndarray, str]) -> float:
        """Calculate brightness score."""
        pass


class MedianBrightness(BrightnessMetric):
    """Median brightness metric.
    
    Uses the median pixel value as brightness indicator.
    Range: 0-255 (0=black, 255=white)
    """
    
    def calculate(self, image: Union[np.ndarray, str]) -> float:
        """Calculate median brightness.
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            float: Median brightness value (0-255)
        """
        img = self._load_image(image)
        median = float(np.median(img))
        return median


class MeanBrightness(BrightnessMetric):
    """Mean brightness metric.
    
    Uses the average pixel value as brightness indicator.
    Range: 0-255
    """
    
    def calculate(self, image: Union[np.ndarray, str]) -> float:
        """Calculate mean brightness.
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            float: Mean brightness value (0-255)
        """
        img = self._load_image(image)
        mean = float(np.mean(img))
        return mean


class PercentileBrightness(BrightnessMetric):
    """Percentile-based brightness metric.
    
    Uses a specific percentile of pixel values.
    Useful for understanding brightness distribution.
    """
    
    def __init__(self, percentile: float = 50):
        """Initialize percentile brightness calculator.
        
        Args:
            percentile: Percentile value (0-100, default: 50 = median)
        """
        if not 0 <= percentile <= 100:
            raise ValueError("Percentile must be between 0 and 100")
        self.percentile = percentile
    
    def calculate(self, image: Union[np.ndarray, str]) -> float:
        """Calculate percentile brightness.
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            float: Brightness at specified percentile (0-255)
        """
        img = self._load_image(image)
        value = float(np.percentile(img, self.percentile))
        return value


class HistogramBrightness(BrightnessMetric):
    """Histogram-based brightness analysis.
    
    Analyzes the distribution of pixel values.
    Returns normalized histogram statistics.
    """
    
    def __init__(self, bins: int = 256):
        """Initialize histogram brightness calculator.
        
        Args:
            bins: Number of histogram bins (default: 256)
        """
        self.bins = bins
    
    def calculate(self, image: Union[np.ndarray, str]) -> float:
        """Calculate histogram-based brightness score.
        
        Uses weighted average based on histogram distribution.
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            float: Weighted brightness score
        """
        img = self._load_image(image)
        
        # Calculate histogram
        hist = cv2.calcHist([img], [0], None, [self.bins], [0, 256])
        hist = hist.flatten() / hist.sum()
        
        # Calculate weighted brightness
        bin_centers = np.arange(self.bins)
        weighted_brightness = np.sum(hist * bin_centers)
        
        return float(weighted_brightness)
    
    def get_histogram_stats(self, image: Union[np.ndarray, str]) -> Dict[str, float]:
        """Get detailed histogram statistics.
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            dict: Statistics including mean, median, std, under/over exposure
        """
        img = self._load_image(image)
        
        # Calculate histogram
        hist = cv2.calcHist([img], [0], None, [self.bins], [0, 256])
        hist = hist.flatten()
        hist_normalized = hist / hist.sum()
        
        # Basic statistics
        mean_val = float(np.mean(img))
        median_val = float(np.median(img))
        std_val = float(np.std(img))
        
        # Under/Over exposure (using thresholds)
        under_exposure = float(np.sum(hist[:50]) / hist.sum() * 100)  # Dark pixels < 50
        over_exposure = float(np.sum(hist[200:]) / hist.sum() * 100)   # Bright pixels > 200
        
        # Dynamic range (range of pixel values present)
        non_zero = np.where(hist > 0)[0]
        if len(non_zero) > 0:
            dynamic_range = float(non_zero[-1] - non_zero[0])
        else:
            dynamic_range = 0.0
        
        # Saturation (concentration of pixels in specific range)
        saturation = float(np.max(hist_normalized))
        
        return {
            'mean': mean_val,
            'median': median_val,
            'std': std_val,
            'under_exposure': under_exposure,
            'over_exposure': over_exposure,
            'dynamic_range': dynamic_range,
            'saturation': saturation
        }


class ExposureMetric(BrightnessMetric):
    """Combined exposure metric.
    
    Evaluates overall exposure quality considering brightness distribution.
    """
    
    def calculate(self, image: Union[np.ndarray, str]) -> float:
        """Calculate exposure quality score (0-100).
        
        Considers:
        - Brightness level (optimal around 128)
        - Under/Over exposure presence
        - Distribution spread
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            float: Exposure quality score (0-100)
        """
        img = self._load_image(image)
        
        # Get brightness statistics
        mean_brightness = float(np.mean(img))
        std_brightness = float(np.std(img))
        
        # Histogram analysis
        hist = cv2.calcHist([img], [0], None, [256], [0, 256])
        hist = hist.flatten()
        
        under_exposure = float(np.sum(hist[:50]))
        over_exposure = float(np.sum(hist[200:]))
        total_pixels = hist.sum()
        
        # Score based on ideal exposure
        # Ideal mean brightness is around 128
        brightness_score = 100 - abs(mean_brightness - 128) / 128 * 100
        
        # Penalty for under/over exposure
        exposure_penalty = (under_exposure + over_exposure) / total_pixels * 100
        
        # Reward for good distribution (std between 30-80)
        if 30 <= std_brightness <= 80:
            distribution_score = 100
        else:
            distribution_score = 100 - abs(std_brightness - 55) / 55 * 30
        
        # Combine scores
        final_score = (brightness_score * 0.5 + 
                      (100 - exposure_penalty) * 0.3 + 
                      distribution_score * 0.2)
        
        return float(np.clip(final_score, 0, 100))

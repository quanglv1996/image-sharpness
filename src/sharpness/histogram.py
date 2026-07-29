"""Histogram analysis for image quality assessment."""

from typing import Union, Dict, Tuple
import numpy as np
import cv2
from .base import SharpnessMetric


class HistogramAnalysis(SharpnessMetric):
    """Comprehensive histogram analysis.
    
    Analyzes exposure, saturation, dynamic range, and clipping.
    """
    
    def __init__(self, bins: int = 256):
        """Initialize histogram analyzer.
        
        Args:
            bins: Number of histogram bins (default: 256)
        """
        self.bins = bins
    
    def calculate(self, image: Union[np.ndarray, str]) -> float:
        """Calculate overall histogram quality score (0-100).
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            float: Histogram quality score (0-100)
        """
        stats = self.get_histogram_stats(image)
        
        # Calculate score based on exposure and distribution
        score = 100.0
        
        # Penalize under/over exposure
        score -= stats['under_exposure_ratio'] * 20
        score -= stats['over_exposure_ratio'] * 20
        
        # Reward good dynamic range
        if stats['dynamic_range'] < 100:
            score -= 20
        
        # Penalize clipping
        score -= stats['left_clip_ratio'] * 10
        score -= stats['right_clip_ratio'] * 10
        
        return float(np.clip(score, 0, 100))
    
    def get_histogram_stats(self, image: Union[np.ndarray, str]) -> Dict[str, float]:
        """Get comprehensive histogram statistics.
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            dict: Detailed histogram statistics
        """
        img = self._load_image(image)
        
        # Calculate histogram
        hist = cv2.calcHist([img], [0], None, [self.bins], [0, 256])
        hist = hist.flatten()
        hist_normalized = hist / (hist.sum() + 1e-8)
        
        # Basic statistics
        mean_val = float(np.mean(img))
        median_val = float(np.median(img))
        std_val = float(np.std(img))
        
        # Under/Over exposure
        # Under: pixels < 50 (very dark)
        under_exposure_ratio = float(np.sum(hist[:50]) / (hist.sum() + 1e-8))
        # Over: pixels > 200 (very bright)
        over_exposure_ratio = float(np.sum(hist[200:]) / (hist.sum() + 1e-8))
        
        # Clipping (0 and 255 pixel values)
        left_clip_ratio = float(hist[0] / (hist.sum() + 1e-8))
        right_clip_ratio = float(hist[-1] / (hist.sum() + 1e-8))
        
        # Dynamic range (actual range of values present)
        non_zero_idx = np.where(hist > 0)[0]
        if len(non_zero_idx) > 1:
            dynamic_range = float(non_zero_idx[-1] - non_zero_idx[0])
        else:
            dynamic_range = 0.0
        
        # Saturation (concentration in specific value)
        saturation = float(np.max(hist_normalized))
        
        # Entropy (distribution uniformity)
        hist_prob = hist_normalized[hist_normalized > 0]
        entropy = float(-np.sum(hist_prob * np.log2(hist_prob + 1e-8)))
        
        # Histogram skewness (left/right bias)
        bin_centers = np.arange(self.bins)
        skewness = float(np.sum(hist_normalized * (bin_centers - mean_val) ** 3))
        
        return {
            'mean': mean_val,
            'median': median_val,
            'std': std_val,
            'under_exposure_ratio': under_exposure_ratio,
            'over_exposure_ratio': over_exposure_ratio,
            'left_clip_ratio': left_clip_ratio,
            'right_clip_ratio': right_clip_ratio,
            'dynamic_range': dynamic_range,
            'saturation': saturation,
            'entropy': entropy,
            'skewness': skewness,
            'total_pixels': float(hist.sum())
        }
    
    def get_rgb_histograms(self, image: Union[np.ndarray, str]) -> Dict[str, list]:
        """Get RGB channel histograms.
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            dict: RGB histogram data with keys 'red', 'green', 'blue'
                  Each contains list of 256 histogram values (raw counts, normalized to max=1)
        """
        if isinstance(image, str):
            img = cv2.imread(image)
            if img is None:
                raise ValueError(f"Could not load image: {image}")
        else:
            img = image.copy()
        
        # Convert to BGR if grayscale
        if len(img.shape) == 2:
            # Grayscale - replicate to RGB
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif img.shape[2] == 4:
            # RGBA - convert to BGR
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        # Calculate histograms for each channel (BGR format)
        histograms = {}
        colors = {'blue': 0, 'green': 1, 'red': 2}
        
        # Find max value across all channels for consistent scaling
        all_values = []
        for color_name, channel_idx in colors.items():
            hist = cv2.calcHist([img], [channel_idx], None, [self.bins], [0, 256])
            hist = hist.flatten()
            all_values.extend(hist.tolist())
        
        max_val = max(all_values) if all_values else 1
        
        # Normalize histograms to 0-1 range based on max
        for color_name, channel_idx in colors.items():
            hist = cv2.calcHist([img], [channel_idx], None, [self.bins], [0, 256])
            hist = hist.flatten()
            # Normalize to 0-1 range
            hist_normalized = (hist / (max_val + 1e-8)).tolist()
            histograms[color_name] = hist_normalized
        
        return histograms


class ExposureAnalysis(SharpnessMetric):
    """Exposure quality analysis.
    
    Evaluates if image is properly exposed with good distribution.
    """
    
    def calculate(self, image: Union[np.ndarray, str]) -> float:
        """Calculate exposure quality score (0-100).
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            float: Exposure quality (0-100, higher is better)
        """
        stats = self._get_exposure_stats(image)
        
        # Ideal exposure:
        # - Mean brightness around 128
        # - Low under/over exposure
        # - Good dynamic range
        # - Low clipping
        
        brightness_score = 100 - abs(stats['mean'] - 128) / 128 * 50
        exposure_penalty = (stats['under_exposure_ratio'] + 
                           stats['over_exposure_ratio']) * 100
        clipping_penalty = (stats['left_clip_ratio'] + 
                           stats['right_clip_ratio']) * 50
        
        final_score = (brightness_score - exposure_penalty - clipping_penalty)
        
        return float(np.clip(final_score, 0, 100))
    
    def _get_exposure_stats(self, image: Union[np.ndarray, str]) -> Dict[str, float]:
        """Get exposure statistics."""
        analyzer = HistogramAnalysis()
        return analyzer.get_histogram_stats(image)


class SaturationAnalysis(SharpnessMetric):
    """Saturation and color vibrancy analysis.
    
    Measures concentration of pixel values (saturation level).
    """
    
    def calculate(self, image: Union[np.ndarray, str]) -> float:
        """Calculate saturation level (0-100).
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            float: Saturation metric
        """
        img = self._load_image(image)
        
        # Calculate histogram
        hist = cv2.calcHist([img], [0], None, [256], [0, 256])
        hist = hist.flatten()
        hist_normalized = hist / (hist.sum() + 1e-8)
        
        # Saturation is how concentrated the histogram is
        # Use entropy-based measure
        hist_prob = hist_normalized[hist_normalized > 0]
        entropy = -np.sum(hist_prob * np.log2(hist_prob + 1e-8))
        
        # Max entropy is log2(256) = 8
        # Low entropy = high saturation (concentrated)
        saturation = 100 * (1 - entropy / 8)
        
        return float(np.clip(saturation, 0, 100))


class DynamicRangeAnalysis(SharpnessMetric):
    """Dynamic range analysis.
    
    Measures how much of the available range is utilized.
    """
    
    def calculate(self, image: Union[np.ndarray, str]) -> float:
        """Calculate dynamic range utilization (0-255).
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            float: Dynamic range (0-255)
        """
        img = self._load_image(image)
        
        return float(np.max(img) - np.min(img))


class HistogramShape(SharpnessMetric):
    """Histogram shape quality metric.
    
    Evaluates the shape and distribution of histogram.
    """
    
    def calculate(self, image: Union[np.ndarray, str]) -> float:
        """Calculate histogram shape quality (0-100).
        
        Penalizes:
        - Spiky/peaked histograms (low quality)
        - Extremely bimodal histograms (unusual)
        
        Rewards:
        - Smooth distributions
        - Well-spread histograms
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            float: Histogram shape quality (0-100)
        """
        img = self._load_image(image)
        
        # Calculate histogram
        hist = cv2.calcHist([img], [0], None, [256], [0, 256])
        hist = hist.flatten().astype(np.float32)
        hist = hist / (hist.sum() + 1e-8)
        
        # Smoothness: penalize very high peaks
        max_peak = np.max(hist)
        peak_penalty = max(0, (max_peak - 0.05) / 0.05 * 50)
        
        # Spread: reward if using most of the range
        used_range = np.sum(hist > 0.001)  # Bins with meaningful content
        spread_score = min(used_range / 200 * 100, 50)  # Max 50 points
        
        # Multimodality: detect bimodal or multimodal distributions
        # Find peaks in histogram
        peaks = []
        for i in range(1, len(hist) - 1):
            if hist[i] > hist[i-1] and hist[i] > hist[i+1]:
                peaks.append(i)
        
        num_peaks = len(peaks)
        # Ideal: 1-3 peaks (penalize too many)
        if num_peaks > 5:
            peak_penalty += (num_peaks - 5) * 5
        
        # Calculate final score
        score = 100 - peak_penalty - max(0, (num_peaks - 3) * 5) + spread_score
        
        return float(np.clip(score, 0, 100))


class HistogramComparisonMetric(SharpnessMetric):
    """Compare histograms of multiple images.
    
    This metric should be used with two images passed sequentially.
    """
    
    def __init__(self):
        """Initialize histogram comparison metric."""
        self.reference_hist = None
    
    def calculate(self, image: Union[np.ndarray, str]) -> float:
        """Store histogram or compare with stored reference.
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            float: Similarity score on second call (0-100)
        """
        img = self._load_image(image)
        hist = cv2.calcHist([img], [0], None, [256], [0, 256])
        hist = cv2.normalize(hist, hist).flatten()
        
        if self.reference_hist is None:
            # First call: store reference
            self.reference_hist = hist
            return 0.0
        
        # Compare with reference
        similarity = cv2.compareHist(self.reference_hist, hist, cv2.HISTCMP_BHATTACHARYYA)
        # Convert to similarity score (0-100)
        score = 100 * (1 - similarity)
        
        return float(np.clip(score, 0, 100))

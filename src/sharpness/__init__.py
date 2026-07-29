"""Image Sharpness Metrics Package.

This package provides multiple methods for calculating image quality metrics,
including sharpness, brightness, contrast, noise, and histogram analysis,
following SOLID principles and design patterns.

Classes - Sharpness:
    SharpnessMetric: Abstract base class for all metrics
    TenengradSharpness: Tenengrad metric using Sobel operator
    LaplacianVarianceSharpness: Laplacian Variance metric
    FFTSharpness: FFT-based sharpness metric
    CombinedSharpness: Composite metric for combining multiple metrics
    TenengradLaplacianSharpness: Predefined Tenengrad + Laplacian combination
    TenengradFFTSharpness: Predefined Tenengrad + FFT combination

Classes - Brightness:
    MedianBrightness: Median pixel value
    MeanBrightness: Mean pixel value
    PercentileBrightness: Percentile-based brightness
    HistogramBrightness: Histogram-based brightness analysis
    ExposureMetric: Combined exposure quality metric

Classes - Contrast:
    RMSContrast: Root Mean Square contrast
    MichelsonContrast: Michelson contrast (bright vs dark)
    WeberContrast: Weber contrast (object vs background)
    LocalContrast: Local neighborhood contrast
    EdgeContrast: Contrast at edges
    DynamicRangeContrast: Max - Min pixel values

Classes - Noise:
    LaplacianNoiseEstimation: Laplacian kernel-based noise
    GaussianNoiseEstimation: Gaussian noise estimation
    SaltPepperNoiseDetection: Impulse noise detection
    ShotNoiseEstimation: Shot/Poisson noise estimation
    StructuralNoiseMetric: Structured noise detection
    CombinedNoiseMetric: Combined noise measurement

Classes - Histogram:
    HistogramAnalysis: Comprehensive histogram analysis
    ExposureAnalysis: Exposure quality evaluation
    SaturationAnalysis: Color saturation analysis
    DynamicRangeAnalysis: Dynamic range measurement
    HistogramShape: Histogram distribution quality
    HistogramComparisonMetric: Compare histograms

Example:
    >>> from sharpness import (
    ...     TenengradSharpness,
    ...     MedianBrightness,
    ...     RMSContrast,
    ...     HistogramAnalysis
    ... )
    >>> 
    >>> # Sharpness
    >>> tenengrad = TenengradSharpness()
    >>> sharpness = tenengrad.calculate('image.jpg')
    >>> 
    >>> # Brightness
    >>> brightness = MedianBrightness()
    >>> bright_score = brightness.calculate('image.jpg')
    >>> 
    >>> # Contrast
    >>> contrast = RMSContrast()
    >>> contrast_score = contrast.calculate('image.jpg')
    >>> 
    >>> # Histogram Analysis
    >>> hist = HistogramAnalysis()
    >>> stats = hist.get_histogram_stats('image.jpg')
"""

from .base import SharpnessMetric

# Sharpness metrics
from .tenengrad import TenengradSharpness
from .laplacian_variance import LaplacianVarianceSharpness
from .fft import FFTSharpness
from .combined import (
    CombinedSharpness,
    TenengradLaplacianSharpness,
    TenengradFFTSharpness
)

# Brightness metrics
from .brightness import (
    BrightnessMetric,
    MedianBrightness,
    MeanBrightness,
    PercentileBrightness,
    HistogramBrightness,
    ExposureMetric
)

# Contrast metrics
from .contrast import (
    ContrastMetric,
    RMSContrast,
    MichelsonContrast,
    WeberContrast,
    LocalContrast,
    EdgeContrast,
    DynamicRangeContrast
)

# Noise metrics
from .noise import (
    NoiseMetric,
    LaplacianNoiseEstimation,
    GaussianNoiseEstimation,
    SaltPepperNoiseDetection,
    ShotNoiseEstimation,
    StructuralNoiseMetric,
    CombinedNoiseMetric
)

# Histogram analysis
from .histogram import (
    HistogramAnalysis,
    ExposureAnalysis,
    SaturationAnalysis,
    DynamicRangeAnalysis,
    HistogramShape,
    HistogramComparisonMetric
)

__all__ = [
    # Base
    "SharpnessMetric",
    
    # Sharpness
    "TenengradSharpness",
    "LaplacianVarianceSharpness",
    "FFTSharpness",
    "CombinedSharpness",
    "TenengradLaplacianSharpness",
    "TenengradFFTSharpness",
    
    # Brightness
    "BrightnessMetric",
    "MedianBrightness",
    "MeanBrightness",
    "PercentileBrightness",
    "HistogramBrightness",
    "ExposureMetric",
    
    # Contrast
    "ContrastMetric",
    "RMSContrast",
    "MichelsonContrast",
    "WeberContrast",
    "LocalContrast",
    "EdgeContrast",
    "DynamicRangeContrast",
    
    # Noise
    "NoiseMetric",
    "LaplacianNoiseEstimation",
    "GaussianNoiseEstimation",
    "SaltPepperNoiseDetection",
    "ShotNoiseEstimation",
    "StructuralNoiseMetric",
    "CombinedNoiseMetric",
    
    # Histogram
    "HistogramAnalysis",
    "ExposureAnalysis",
    "SaturationAnalysis",
    "DynamicRangeAnalysis",
    "HistogramShape",
    "HistogramComparisonMetric",
]

__version__ = "2.0.0"

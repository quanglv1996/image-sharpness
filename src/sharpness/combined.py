"""Combined sharpness metrics."""

from typing import Union, List, Callable
import numpy as np
from .base import SharpnessMetric


class CombinedSharpness(SharpnessMetric):
    """Composite sharpness metric combining multiple methods.
    
    This class follows the Composite design pattern and Single Responsibility:
    it combines multiple sharpness metrics using configurable aggregation.
    Each metric is injected as a dependency (Dependency Inversion Principle).
    """

    def __init__(self, metrics: List[SharpnessMetric], 
                 weights: List[float] = None,
                 aggregation: str = "weighted_mean"):
        """Initialize combined sharpness calculator.
        
        Args:
            metrics: List of SharpnessMetric instances to combine
            weights: Weight for each metric (default: equal weights)
            aggregation: Aggregation method ("weighted_mean", "mean", "sum")
            
        Raises:
            ValueError: If metrics list is empty or weights don't match metrics
        """
        if not metrics:
            raise ValueError("At least one metric must be provided")
        
        self.metrics = metrics
        self.aggregation = aggregation
        
        if weights is None:
            self.weights = [1.0 / len(metrics)] * len(metrics)
        else:
            if len(weights) != len(metrics):
                raise ValueError("Number of weights must match number of metrics")
            # Normalize weights
            total = sum(weights)
            self.weights = [w / total for w in weights]

    def calculate(self, image: Union[np.ndarray, str]) -> float:
        """Calculate combined sharpness score.
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            float: Combined sharpness score
        """
        scores = [metric.calculate(image) for metric in self.metrics]
        
        if self.aggregation == "weighted_mean":
            result = sum(s * w for s, w in zip(scores, self.weights))
        elif self.aggregation == "mean":
            result = np.mean(scores)
        elif self.aggregation == "sum":
            result = np.sum(scores)
        else:
            raise ValueError(f"Unknown aggregation method: {self.aggregation}")
        
        return float(result)

    def get_individual_scores(self, image: Union[np.ndarray, str]) -> dict:
        """Get individual sharpness scores from each metric.
        
        Args:
            image: numpy array or path to image file
            
        Returns:
            dict: Scores from each metric with their names
        """
        return {
            metric.__class__.__name__: metric.calculate(image) 
            for metric in self.metrics
        }


class TenengradLaplacianSharpness(CombinedSharpness):
    """Combined Tenengrad + Laplacian Variance sharpness metric.
    
    This specialization follows the Template Method pattern,
    providing a predefined combination of Tenengrad and Laplacian Variance metrics.
    """

    def __init__(self, tenengrad_metric: SharpnessMetric = None,
                 laplacian_metric: SharpnessMetric = None,
                 tenengrad_weight: float = 0.5,
                 laplacian_weight: float = 0.5):
        """Initialize Tenengrad + Laplacian combined metric.
        
        Args:
            tenengrad_metric: TenengradSharpness instance (created if not provided)
            laplacian_metric: LaplacianVarianceSharpness instance (created if not provided)
            tenengrad_weight: Weight for Tenengrad metric
            laplacian_weight: Weight for Laplacian metric
        """
        from .tenengrad import TenengradSharpness
        from .laplacian_variance import LaplacianVarianceSharpness
        
        if tenengrad_metric is None:
            tenengrad_metric = TenengradSharpness()
        if laplacian_metric is None:
            laplacian_metric = LaplacianVarianceSharpness()
        
        super().__init__(
            metrics=[tenengrad_metric, laplacian_metric],
            weights=[tenengrad_weight, laplacian_weight],
            aggregation="weighted_mean"
        )


class TenengradFFTSharpness(CombinedSharpness):
    """Combined Tenengrad + FFT sharpness metric.
    
    This specialization combines Tenengrad (spatial domain) with FFT analysis
    (frequency domain) for robust sharpness estimation.
    """

    def __init__(self, tenengrad_metric: SharpnessMetric = None,
                 fft_metric: SharpnessMetric = None,
                 tenengrad_weight: float = 0.5,
                 fft_weight: float = 0.5):
        """Initialize Tenengrad + FFT combined metric.
        
        Args:
            tenengrad_metric: TenengradSharpness instance (created if not provided)
            fft_metric: FFTSharpness instance (created if not provided)
            tenengrad_weight: Weight for Tenengrad metric
            fft_weight: Weight for FFT metric
        """
        from .tenengrad import TenengradSharpness
        from .fft import FFTSharpness
        
        if tenengrad_metric is None:
            tenengrad_metric = TenengradSharpness()
        if fft_metric is None:
            fft_metric = FFTSharpness()
        
        super().__init__(
            metrics=[tenengrad_metric, fft_metric],
            weights=[tenengrad_weight, fft_weight],
            aggregation="weighted_mean"
        )

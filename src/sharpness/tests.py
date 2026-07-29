"""Unit tests for sharpness metrics."""
import sys
sys.path.append('../../.')
import unittest
import numpy as np
import cv2
from src.sharpness import (
    TenengradSharpness,
    LaplacianVarianceSharpness,
    FFTSharpness,
    TenengradLaplacianSharpness,
    TenengradFFTSharpness,
    CombinedSharpness
)


class TestTenengradSharpness(unittest.TestCase):
    """Test Tenengrad sharpness metric."""

    def setUp(self):
        """Create test images."""
        self.sharp_image = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        self.metric = TenengradSharpness()

    def test_calculate_returns_float(self):
        """Test that calculate returns a float."""
        score = self.metric.calculate(self.sharp_image)
        self.assertIsInstance(score, float)

    def test_calculate_returns_positive(self):
        """Test that score is positive."""
        score = self.metric.calculate(self.sharp_image)
        self.assertGreaterEqual(score, 0)

    def test_callable_syntax(self):
        """Test using metric as callable."""
        score = self.metric(self.sharp_image)
        self.assertIsInstance(score, float)

    def test_invalid_kernel_size(self):
        """Test that even kernel size raises error."""
        with self.assertRaises(ValueError):
            TenengradSharpness(ksize=4)

    def test_sharp_vs_blurry_image(self):
        """Test that sharp image has higher score than blurry."""
        # Create a sharp image with edges
        sharp = np.zeros((100, 100), dtype=np.uint8)
        sharp[40:60, 40:60] = 255
        
        # Create a blurry version
        blurry = cv2.GaussianBlur(sharp, (11, 11), 2)
        
        sharp_score = self.metric.calculate(sharp)
        blurry_score = self.metric.calculate(blurry)
        
        # Sharp image should have higher score
        self.assertGreater(sharp_score, blurry_score)


class TestLaplacianVarianceSharpness(unittest.TestCase):
    """Test Laplacian Variance sharpness metric."""

    def setUp(self):
        """Create test images."""
        self.image = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        self.metric = LaplacianVarianceSharpness()

    def test_calculate_returns_float(self):
        """Test that calculate returns a float."""
        score = self.metric.calculate(self.image)
        self.assertIsInstance(score, float)

    def test_calculate_returns_positive(self):
        """Test that score is positive."""
        score = self.metric.calculate(self.image)
        self.assertGreaterEqual(score, 0)

    def test_sharp_vs_blurry_image(self):
        """Test that sharp image has higher score than blurry."""
        sharp = np.zeros((100, 100), dtype=np.uint8)
        sharp[40:60, 40:60] = 255
        
        blurry = cv2.GaussianBlur(sharp, (11, 11), 2)
        
        sharp_score = self.metric.calculate(sharp)
        blurry_score = self.metric.calculate(blurry)
        
        self.assertGreater(sharp_score, blurry_score)


class TestFFTSharpness(unittest.TestCase):
    """Test FFT sharpness metric."""

    def setUp(self):
        """Create test images."""
        self.image = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        self.metric = FFTSharpness()

    def test_calculate_returns_float(self):
        """Test that calculate returns a float."""
        score = self.metric.calculate(self.image)
        self.assertIsInstance(score, float)

    def test_calculate_returns_positive(self):
        """Test that score is positive."""
        score = self.metric.calculate(self.image)
        self.assertGreaterEqual(score, 0)

    def test_invalid_threshold(self):
        """Test that invalid threshold raises error."""
        with self.assertRaises(ValueError):
            FFTSharpness(high_freq_threshold=0)
        
        with self.assertRaises(ValueError):
            FFTSharpness(high_freq_threshold=1.5)


class TestCombinedSharpness(unittest.TestCase):
    """Test Combined sharpness metric."""

    def setUp(self):
        """Create test images and metrics."""
        self.image = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        self.tenengrad = TenengradSharpness()
        self.laplacian = LaplacianVarianceSharpness()

    def test_combined_with_two_metrics(self):
        """Test combining two metrics."""
        combined = CombinedSharpness([self.tenengrad, self.laplacian])
        score = combined.calculate(self.image)
        self.assertIsInstance(score, float)

    def test_combined_with_custom_weights(self):
        """Test combining with custom weights."""
        combined = CombinedSharpness(
            [self.tenengrad, self.laplacian],
            weights=[0.7, 0.3]
        )
        score = combined.calculate(self.image)
        self.assertIsInstance(score, float)

    def test_combined_weights_normalization(self):
        """Test that weights are normalized."""
        combined = CombinedSharpness(
            [self.tenengrad, self.laplacian],
            weights=[3, 1]  # Should be normalized to 0.75, 0.25
        )
        self.assertAlmostEqual(sum(combined.weights), 1.0)

    def test_empty_metrics_raises_error(self):
        """Test that empty metrics list raises error."""
        with self.assertRaises(ValueError):
            CombinedSharpness([])

    def test_mismatched_weights_raises_error(self):
        """Test that mismatched weights raise error."""
        with self.assertRaises(ValueError):
            CombinedSharpness(
                [self.tenengrad, self.laplacian],
                weights=[0.5, 0.3, 0.2]  # Wrong number
            )

    def test_get_individual_scores(self):
        """Test getting individual scores from metrics."""
        combined = CombinedSharpness([self.tenengrad, self.laplacian])
        scores = combined.get_individual_scores(self.image)
        
        self.assertEqual(len(scores), 2)
        self.assertIn("TenengradSharpness", scores)
        self.assertIn("LaplacianVarianceSharpness", scores)

    def test_aggregation_methods(self):
        """Test different aggregation methods."""
        metrics = [self.tenengrad, self.laplacian]
        
        # Test weighted_mean
        combined_weighted = CombinedSharpness(
            metrics, aggregation="weighted_mean"
        )
        score_weighted = combined_weighted.calculate(self.image)
        
        # Test mean
        combined_mean = CombinedSharpness(
            metrics, aggregation="mean"
        )
        score_mean = combined_mean.calculate(self.image)
        
        # Test sum
        combined_sum = CombinedSharpness(
            metrics, aggregation="sum"
        )
        score_sum = combined_sum.calculate(self.image)
        
        # All should return valid scores
        self.assertIsInstance(score_weighted, float)
        self.assertIsInstance(score_mean, float)
        self.assertIsInstance(score_sum, float)

    def test_invalid_aggregation_raises_error(self):
        """Test that invalid aggregation method raises error."""
        combined = CombinedSharpness(
            [self.tenengrad, self.laplacian],
            aggregation="invalid_method"
        )
        
        with self.assertRaises(ValueError):
            combined.calculate(self.image)


class TestPredefinedCombinations(unittest.TestCase):
    """Test predefined metric combinations."""

    def setUp(self):
        """Create test image."""
        self.image = np.random.randint(0, 256, (100, 100), dtype=np.uint8)

    def test_tenengrad_laplacian_combination(self):
        """Test Tenengrad + Laplacian combination."""
        combined = TenengradLaplacianSharpness()
        score = combined.calculate(self.image)
        self.assertIsInstance(score, float)

    def test_tenengrad_fft_combination(self):
        """Test Tenengrad + FFT combination."""
        combined = TenengradFFTSharpness()
        score = combined.calculate(self.image)
        self.assertIsInstance(score, float)

    def test_custom_metric_injection(self):
        """Test injecting custom metrics into combinations."""
        custom_tenengrad = TenengradSharpness(ksize=5)
        custom_laplacian = LaplacianVarianceSharpness(ksize=2)
        
        combined = TenengradLaplacianSharpness(
            tenengrad_metric=custom_tenengrad,
            laplacian_metric=custom_laplacian
        )
        
        score = combined.calculate(self.image)
        self.assertIsInstance(score, float)


class TestPolymorphism(unittest.TestCase):
    """Test polymorphic behavior of metrics."""

    def setUp(self):
        """Create test image and metrics."""
        self.image = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        self.metrics = [
            TenengradSharpness(),
            LaplacianVarianceSharpness(),
            FFTSharpness(),
        ]

    def evaluate_all_metrics(self, image):
        """Helper: evaluate all metrics polymorphically."""
        results = {}
        for metric in self.metrics:
            # All metrics can be used the same way
            score = metric.calculate(image)
            results[metric.__class__.__name__] = score
        return results

    def test_all_metrics_return_float(self):
        """Test that all metrics return float scores."""
        results = self.evaluate_all_metrics(self.image)
        
        for name, score in results.items():
            self.assertIsInstance(score, float, 
                                  f"{name} didn't return float")

    def test_all_metrics_return_positive(self):
        """Test that all metrics return positive scores."""
        results = self.evaluate_all_metrics(self.image)
        
        for name, score in results.items():
            self.assertGreaterEqual(score, 0, 
                                    f"{name} returned negative score")


if __name__ == "__main__":
    unittest.main()

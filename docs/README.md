"""
Image Sharpness Metrics - README

This package provides multiple methods for calculating image sharpness metrics,
following SOLID design principles and best practices.
"""

# Image Sharpness Metrics Package

A comprehensive Python package for calculating image sharpness using multiple methods, designed with SOLID principles and maintainable architecture.

## Features

- **Multiple Sharpness Metrics**:
  - Tenengrad (Sobel-based)
  - Laplacian Variance
  - FFT-based (frequency domain)
  - Combined metrics (Tenengrad + Laplacian, Tenengrad + FFT)

- **SOLID Design Principles**:
  - Single Responsibility: Each class has one reason to change
  - Open/Closed: Extensible without modifying existing code
  - Liskov Substitution: All metrics implement same interface
  - Interface Segregation: Minimal, focused interfaces
  - Dependency Inversion: Depends on abstractions

- **Design Patterns**:
  - Strategy Pattern: Different calculation strategies
  - Composite Pattern: Combine multiple metrics
  - Template Method: Common template for metrics
  - Factory-like: Predefined combinations

## Installation

```bash
pip install opencv-python numpy
```

## Quick Start

### Single Metric

```python
from sharpness import TenengradSharpness

# Create metric instance
metric = TenengradSharpness()

# Calculate sharpness
score = metric.calculate('image.jpg')
print(f"Sharpness Score: {score}")
```

### Predefined Combinations

```python
from sharpness import TenengradLaplacianSharpness, TenengradFFTSharpness

# Tenengrad + Laplacian
combined_tl = TenengradLaplacianSharpness()
score = combined_tl.calculate('image.jpg')

# Tenengrad + FFT
combined_tf = TenengradFFTSharpness()
score = combined_tf.calculate('image.jpg')

# Get individual scores
individual_scores = combined_tl.get_individual_scores('image.jpg')
```

### Custom Combinations

```python
from sharpness import (
    CombinedSharpness,
    TenengradSharpness,
    LaplacianVarianceSharpness,
    FFTSharpness
)

# Create custom combination with custom weights
metrics = [
    TenengradSharpness(),
    LaplacianVarianceSharpness(),
    FFTSharpness()
]

combined = CombinedSharpness(
    metrics=metrics,
    weights=[0.5, 0.3, 0.2],  # 50%, 30%, 20%
    aggregation="weighted_mean"
)

score = combined.calculate('image.jpg')
```

## API Reference

### Base Class

#### `SharpnessMetric` (Abstract Base Class)

Base class for all sharpness metrics.

**Methods:**
- `calculate(image: Union[np.ndarray, str]) -> float`: Calculate sharpness score
- `__call__(image: Union[np.ndarray, str]) -> float`: Callable syntax support

**Protected Methods:**
- `_load_image(image: Union[np.ndarray, str]) -> np.ndarray`: Load or convert image to grayscale

### Individual Metrics

#### `TenengradSharpness`

Tenengrad sharpness metric using Sobel operator.

```python
metric = TenengradSharpness(ksize=3)  # Kernel size (default: 3)
score = metric.calculate(image)
```

**Parameters:**
- `ksize`: Kernel size for Sobel operator (must be odd, default: 3)

**Formula:** Tenengrad = Σ(Gx² + Gy²)

---

#### `LaplacianVarianceSharpness`

Laplacian Variance sharpness metric.

```python
metric = LaplacianVarianceSharpness(ksize=1)
score = metric.calculate(image)
```

**Parameters:**
- `ksize`: Size of the kernel (default: 1)

**Formula:** Variance of Laplacian kernel response

---

#### `FFTSharpness`

FFT-based sharpness metric using frequency domain analysis.

```python
metric = FFTSharpness(high_freq_threshold=0.1)
score = metric.calculate(image)
```

**Parameters:**
- `high_freq_threshold`: Threshold for high-frequency ratio (0-1, default: 0.1)

**Formula:** Sum of high-frequency magnitude in FFT spectrum

### Combined Metrics

#### `CombinedSharpness`

Generic composite metric combining multiple metrics.

```python
combined = CombinedSharpness(
    metrics=[metric1, metric2, metric3],
    weights=[0.5, 0.3, 0.2],
    aggregation="weighted_mean"
)
```

**Parameters:**
- `metrics`: List of SharpnessMetric instances
- `weights`: Weight for each metric (auto-normalized, default: equal weights)
- `aggregation`: Aggregation method ("weighted_mean", "mean", "sum")

**Methods:**
- `calculate(image)`: Calculate combined score
- `get_individual_scores(image)`: Get individual scores from each metric

---

#### `TenengradLaplacianSharpness`

Predefined combination of Tenengrad + Laplacian Variance.

```python
combined = TenengradLaplacianSharpness(
    tenengrad_weight=0.5,
    laplacian_weight=0.5
)
```

---

#### `TenengradFFTSharpness`

Predefined combination of Tenengrad + FFT.

```python
combined = TenengradFFTSharpness(
    tenengrad_weight=0.5,
    fft_weight=0.5
)
```

## Image Format Support

- **File paths**: PNG, JPG, BMP, and other OpenCV-supported formats
- **NumPy arrays**: 
  - Grayscale: shape (H, W)
  - Color: shape (H, W, 3) - automatically converted to grayscale

```python
# From file
score = metric.calculate('path/to/image.jpg')

# From numpy array (grayscale)
import numpy as np
img = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
score = metric.calculate(img)

# From numpy array (color)
img = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
score = metric.calculate(img)
```

## Usage Examples

### Batch Processing

```python
from sharpness import TenengradLaplacianSharpness

metric = TenengradLaplacianSharpness()

images = ['image1.jpg', 'image2.jpg', 'image3.jpg']
results = {}

for image_path in images:
    score = metric(image_path)
    results[image_path] = score

# Find sharpest image
sharpest = max(results, key=results.get)
print(f"Sharpest: {sharpest} (score: {results[sharpest]})")
```

### Compare Metrics

```python
from sharpness import (
    TenengradSharpness,
    LaplacianVarianceSharpness,
    FFTSharpness
)

image = 'image.jpg'

metrics = {
    'Tenengrad': TenengradSharpness(),
    'Laplacian': LaplacianVarianceSharpness(),
    'FFT': FFTSharpness()
}

print("Sharpness Scores:")
for name, metric in metrics.items():
    score = metric(image)
    print(f"  {name}: {score:.2f}")
```

### Dynamic Metric Selection

```python
from sharpness import SharpnessMetric, TenengradSharpness, LaplacianVarianceSharpness

def evaluate_sharpness(metric: SharpnessMetric, image_path: str) -> float:
    """
    Generic evaluation function that works with any metric.
    This demonstrates polymorphism and Liskov Substitution Principle.
    """
    return metric.calculate(image_path)

# Can use any metric
score = evaluate_sharpness(TenengradSharpness(), 'image.jpg')
score = evaluate_sharpness(LaplacianVarianceSharpness(), 'image.jpg')
```

## Class Hierarchy

```
SharpnessMetric (ABC)
├── TenengradSharpness
├── LaplacianVarianceSharpness
├── FFTSharpness
└── CombinedSharpness
    ├── TenengradLaplacianSharpness
    └── TenengradFFTSharpness
```

## SOLID Principles

See [SOLID_DESIGN.md](SOLID_DESIGN.md) for detailed explanation of:
- Single Responsibility Principle
- Open/Closed Principle
- Liskov Substitution Principle
- Interface Segregation Principle
- Dependency Inversion Principle

## Design Patterns

- **Strategy Pattern**: Each metric is an interchangeable strategy
- **Composite Pattern**: Combine metrics into higher-level metrics
- **Template Method Pattern**: Common metric template
- **Factory-like Pattern**: Predefined metric combinations

## Testing

Run unit tests:

```bash
python -m unittest src/sharpness/tests.py
```

Test coverage includes:
- Individual metric calculations
- Combined metrics
- Weight normalization
- Error handling
- Polymorphic behavior
- Sharp vs. blurry image differentiation

## Requirements

- Python 3.7+
- NumPy
- OpenCV (cv2)

## File Structure

```
src/
└── sharpness/
    ├── __init__.py                 # Package initialization & public API
    ├── base.py                     # Abstract base class
    ├── tenengrad.py               # Tenengrad metric
    ├── laplacian_variance.py       # Laplacian Variance metric
    ├── fft.py                      # FFT metric
    ├── combined.py                # Combined metrics
    ├── examples.py                # Usage examples
    ├── tests.py                   # Unit tests
    ├── SOLID_DESIGN.md            # Design principles documentation
    └── README.md                  # This file
```

## Error Handling

All metrics validate input and provide clear error messages:

```python
# Invalid kernel size
try:
    metric = TenengradSharpness(ksize=4)  # Even size
except ValueError as e:
    print(f"Error: {e}")

# Invalid image path
try:
    score = metric.calculate('nonexistent.jpg')
except ValueError as e:
    print(f"Error: {e}")

# Invalid image type
try:
    score = metric.calculate(12345)
except TypeError as e:
    print(f"Error: {e}")
```

## Performance Tips

1. **Reuse metric instances**: Create metric once, use multiple times
   ```python
   metric = TenengradSharpness()  # Create once
   for image in images:
       score = metric(image)      # Reuse
   ```

2. **Use combined metrics wisely**: Combining metrics increases computation
   ```python
   # Faster
   single = TenengradSharpness()
   
   # Slower (3x computation)
   combined = CombinedSharpness([
       TenengradSharpness(),
       LaplacianVarianceSharpness(),
       FFTSharpness()
   ])
   ```

3. **Process in batches**: Read all images into memory if possible

## License

[Your License Here]

## Contributing

Contributions are welcome! To add a new metric:

1. Extend `SharpnessMetric`
2. Implement `calculate()` method
3. Add unit tests
4. Update documentation

Example:

```python
from sharpness.base import SharpnessMetric

class CustomSharpness(SharpnessMetric):
    def calculate(self, image):
        img = self._load_image(image)
        # Your implementation
        return score
```

## FAQ

**Q: Which metric should I use?**
A: It depends on your use case:
- Tenengrad: Fast, good for edges
- Laplacian: Sensitive to noise, good for general sharpness
- FFT: Good for frequency analysis
- Combined: Best overall performance

**Q: Can I combine more than 2 metrics?**
A: Yes, use `CombinedSharpness` with any number of metrics.

**Q: How do I handle image paths on different OS?**
A: All metrics accept both absolute and relative paths. Use `pathlib.Path` for cross-platform compatibility.

**Q: Can I use this with video frames?**
A: Yes, extract frames as NumPy arrays and pass to any metric.

## Changelog

### Version 1.0.0
- Initial release
- Tenengrad, Laplacian Variance, FFT metrics
- Combined metrics with configurable weights
- Comprehensive documentation
- Full test coverage

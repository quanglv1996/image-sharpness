"""Example usage of sharpness metrics."""

from sharpness import (
    TenengradSharpness,
    LaplacianVarianceSharpness,
    FFTSharpness,
    TenengradLaplacianSharpness,
    TenengradFFTSharpness,
    CombinedSharpness
)


def example_single_metrics():
    """Example: Using individual sharpness metrics."""
    print("=" * 60)
    print("EXAMPLE 1: Single Metrics")
    print("=" * 60)
    
    image_path = "path/to/image.jpg"
    
    # Tenengrad (Sobel)
    tenengrad = TenengradSharpness(ksize=3)
    score = tenengrad.calculate(image_path)
    print(f"Tenengrad Score: {score:.2f}")
    
    # Laplacian Variance
    laplacian = LaplacianVarianceSharpness()
    score = laplacian.calculate(image_path)
    print(f"Laplacian Variance Score: {score:.2f}")
    
    # FFT-based
    fft = FFTSharpness()
    score = fft.calculate(image_path)
    print(f"FFT Score: {score:.2f}")


def example_predefined_combinations():
    """Example: Using predefined metric combinations."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Predefined Combinations")
    print("=" * 60)
    
    image_path = "path/to/image.jpg"
    
    # Tenengrad + Laplacian (equal weights)
    combined_tl = TenengradLaplacianSharpness()
    score = combined_tl.calculate(image_path)
    individual_scores = combined_tl.get_individual_scores(image_path)
    
    print(f"\nTenengrad + Laplacian Score: {score:.2f}")
    print("Individual scores:")
    for name, value in individual_scores.items():
        print(f"  {name}: {value:.2f}")
    
    # Tenengrad + FFT (equal weights)
    combined_tf = TenengradFFTSharpness()
    score = combined_tf.calculate(image_path)
    individual_scores = combined_tf.get_individual_scores(image_path)
    
    print(f"\nTenengrad + FFT Score: {score:.2f}")
    print("Individual scores:")
    for name, value in individual_scores.items():
        print(f"  {name}: {value:.2f}")


def example_custom_combination():
    """Example: Creating custom metric combinations."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Custom Combinations")
    print("=" * 60)
    
    image_path = "path/to/image.jpg"
    
    # Create custom combination with different weights
    # Tenengrad (60%) + Laplacian (40%)
    tenengrad = TenengradSharpness()
    laplacian = LaplacianVarianceSharpness()
    
    custom_combined = CombinedSharpness(
        metrics=[tenengrad, laplacian],
        weights=[0.6, 0.4],  # Tenengrad 60%, Laplacian 40%
        aggregation="weighted_mean"
    )
    
    score = custom_combined.calculate(image_path)
    print(f"\nCustom Combination (Tenengrad 60% + Laplacian 40%): {score:.2f}")
    
    # Custom combination with all three methods
    fft = FFTSharpness()
    triple_combined = CombinedSharpness(
        metrics=[tenengrad, laplacian, fft],
        weights=[0.5, 0.3, 0.2],  # 50%, 30%, 20%
        aggregation="weighted_mean"
    )
    
    score = triple_combined.calculate(image_path)
    individual_scores = triple_combined.get_individual_scores(image_path)
    
    print(f"\nCustom Triple Combination Score: {score:.2f}")
    print("Individual scores:")
    for name, value in individual_scores.items():
        print(f"  {name}: {value:.2f}")


def example_callable_syntax():
    """Example: Using metrics as callable objects."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Callable Syntax")
    print("=" * 60)
    
    image_path = "path/to/image.jpg"
    
    # Metrics can be called directly
    tenengrad = TenengradSharpness()
    score = tenengrad(image_path)  # Callable syntax
    print(f"Tenengrad Score (callable): {score:.2f}")


def example_batch_processing():
    """Example: Processing multiple images."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Batch Processing")
    print("=" * 60)
    
    image_paths = [
        "path/to/image1.jpg",
        "path/to/image2.jpg",
        "path/to/image3.jpg"
    ]
    
    # Use combined metric for consistent evaluation
    metric = TenengradLaplacianSharpness()
    
    results = {}
    for image_path in image_paths:
        try:
            score = metric(image_path)
            results[image_path] = score
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
    
    print("\nSharpness Scores:")
    for image_path, score in results.items():
        print(f"  {image_path}: {score:.2f}")
    
    # Sort by sharpness
    sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
    print("\nRanked by Sharpness (highest first):")
    for i, (image_path, score) in enumerate(sorted_results, 1):
        print(f"  {i}. {image_path}: {score:.2f}")


if __name__ == "__main__":
    # Run all examples (uncomment as needed)
    # example_single_metrics()
    # example_predefined_combinations()
    # example_custom_combination()
    # example_callable_syntax()
    # example_batch_processing()
    
    print("Examples are ready to run!")
    print("\nTo use the sharpness metrics:")
    print("  1. Import the desired metric class")
    print("  2. Create an instance")
    print("  3. Call calculate() or use callable syntax")

"""SOLID Principles and Design Patterns Documentation.

This document explains how the sharpness metrics implementation adheres to
SOLID principles and uses design patterns for maintainability and extensibility.
"""

"""
SOLID PRINCIPLES IMPLEMENTATION
================================

1. SINGLE RESPONSIBILITY PRINCIPLE (SRP)
----------------------------------------
Each class has ONE reason to change.

   ✓ SharpnessMetric: Defines the interface for sharpness calculation
   ✓ TenengradSharpness: Only responsible for Tenengrad calculation
   ✓ LaplacianVarianceSharpness: Only responsible for Laplacian calculation
   ✓ FFTSharpness: Only responsible for FFT calculation
   ✓ CombinedSharpness: Only responsible for combining metrics
   
   Benefits:
   - Easy to test each metric independently
   - Easy to fix bugs in specific metrics
   - Each class is small and focused


2. OPEN/CLOSED PRINCIPLE (OCP)
-------------------------------
Classes are OPEN for extension, CLOSED for modification.

   ✓ SharpnessMetric is an abstract base class
   ✓ New metrics can be added by extending SharpnessMetric
   ✓ No need to modify existing code to add new metrics
   
   Example - Adding a new metric:
   
   from sharpness.base import SharpnessMetric
   
   class MyNewSharpness(SharpnessMetric):
       def calculate(self, image):
           # Your implementation
           return score
   
   Benefits:
   - Existing code remains untouched when adding new metrics
   - Reduced risk of breaking existing functionality


3. LISKOV SUBSTITUTION PRINCIPLE (LSP)
---------------------------------------
All subclasses can substitute for their base class.

   ✓ All metrics (Tenengrad, Laplacian, FFT) work the same way
   ✓ They all inherit from SharpnessMetric
   ✓ They can all be used interchangeably
   
   Example:
   
   def evaluate_image_sharpness(metric: SharpnessMetric, image):
       return metric.calculate(image)
   
   # Can pass ANY SharpnessMetric implementation
   evaluate_image_sharpness(TenengradSharpness(), image)
   evaluate_image_sharpness(LaplacianVarianceSharpness(), image)
   evaluate_image_sharpness(FFTSharpness(), image)
   
   Benefits:
   - Polymorphic code is flexible and extensible
   - Can swap implementations without changing client code


4. INTERFACE SEGREGATION PRINCIPLE (ISP)
-----------------------------------------
Clients should not depend on interfaces they don't use.

   ✓ SharpnessMetric interface is minimal (only calculate() and __call__)
   ✓ Helper method _load_image() is protected, not exposed to clients
   ✓ CombinedSharpness provides additional methods only when needed
   
   Benefits:
   - Simple, focused interfaces
   - Less coupling between components
   - Clients only depend on what they need


5. DEPENDENCY INVERSION PRINCIPLE (DIP)
----------------------------------------
Depend on abstractions, not concrete implementations.

   ✓ CombinedSharpness accepts a list of SharpnessMetric (abstractions)
   ✓ TenengradLaplacianSharpness depends on SharpnessMetric interface
   ✓ TenengradFFTSharpness depends on SharpnessMetric interface
   
   Example (Good - DIP):
   
   def __init__(self, metrics: List[SharpnessMetric], ...):
       self.metrics = metrics  # Depends on abstraction
   
   Benefits:
   - Loose coupling between components
   - Easy to swap implementations
   - Testable with mock implementations


DESIGN PATTERNS USED
====================

1. STRATEGY PATTERN
-------------------
Each metric is a strategy for calculating sharpness.

   - SharpnessMetric: Strategy interface
   - TenengradSharpness, LaplacianVarianceSharpness, FFTSharpness: Concrete strategies
   
   Usage:
   
   strategy = TenengradSharpness()
   score = strategy.calculate(image)
   
   # Can change strategy at runtime
   strategy = LaplacianVarianceSharpness()
   score = strategy.calculate(image)


2. COMPOSITE PATTERN
---------------------
CombinedSharpness combines multiple metrics into a single metric.

   - SharpnessMetric: Component interface
   - Individual metrics: Leaf components
   - CombinedSharpness: Composite component
   
   Benefits:
   - Can combine metrics recursively
   - Uniform interface for both individual and composite metrics
   
   Example:
   
   # Create a composite of composites
   tenengrad_laplacian = TenengradLaplacianSharpness()
   fft = FFTSharpness()
   
   mega_combined = CombinedSharpness(
       metrics=[tenengrad_laplacian, fft],
       weights=[0.7, 0.3]
   )


3. TEMPLATE METHOD PATTERN
---------------------------
SharpnessMetric provides a template for metric implementation.

   - Template: _load_image(), __call__()
   - Subclasses implement: calculate()
   
   Example:
   
   class MyMetric(SharpnessMetric):
       def calculate(self, image):
           img = self._load_image(image)  # Template method
           # Your implementation
           return score


4. FACTORY-LIKE PATTERN
-----------------------
TenengradLaplacianSharpness and TenengradFFTSharpness create predefined combinations.

   Benefits:
   - Encapsulates complex creation logic
   - Provides sensible defaults
   - Still allows customization through constructor parameters


CLASS HIERARCHY
===============

SharpnessMetric (ABC)
├── TenengradSharpness
├── LaplacianVarianceSharpness
├── FFTSharpness
└── CombinedSharpness
    ├── TenengradLaplacianSharpness
    └── TenengradFFTSharpness


USAGE EXAMPLES
==============

Single Metric:
    metric = TenengradSharpness()
    score = metric.calculate("image.jpg")

Predefined Combination:
    metric = TenengradLaplacianSharpness()
    score = metric.calculate("image.jpg")

Custom Combination:
    metrics = [
        TenengradSharpness(),
        LaplacianVarianceSharpness(),
        FFTSharpness()
    ]
    combined = CombinedSharpness(
        metrics=metrics,
        weights=[0.5, 0.3, 0.2]
    )
    score = combined.calculate("image.jpg")

Polymorphic Usage:
    def evaluate(metric: SharpnessMetric, image):
        return metric.calculate(image)


BENEFITS OF THIS ARCHITECTURE
==============================

1. Maintainability
   - Each metric is independent and easy to modify
   - Changes to one metric don't affect others
   - Clear separation of concerns

2. Extensibility
   - Easy to add new metrics
   - Easy to create new combinations
   - Existing code doesn't need changes

3. Testability
   - Each metric can be tested independently
   - Can create mock metrics for testing
   - No hidden dependencies

4. Flexibility
   - Metrics can be combined in any way
   - Weights and aggregation methods are configurable
   - Runtime polymorphism for dynamic behavior

5. Code Reusability
   - Common functionality in base class
   - Metrics can be composed into higher-level metrics
   - Shared utility methods (_load_image)
"""

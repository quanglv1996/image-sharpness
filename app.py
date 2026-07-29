"""Flask application for image sharpness comparison."""

import os
import sys
import json
import base64
from io import BytesIO
from pathlib import Path

import cv2
import numpy as np
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from src.sharpness import (
    # Sharpness
    TenengradSharpness,
    LaplacianVarianceSharpness,
    FFTSharpness,
    TenengradLaplacianSharpness,
    TenengradFFTSharpness,
    # Brightness
    MedianBrightness,
    MeanBrightness,
    PercentileBrightness,
    HistogramBrightness,
    ExposureMetric,
    # Contrast
    RMSContrast,
    MichelsonContrast,
    WeberContrast,
    LocalContrast,
    # Noise
    LaplacianNoiseEstimation,
    GaussianNoiseEstimation,
    SaltPepperNoiseDetection,
    # Histogram
    HistogramAnalysis,
)

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_metrics():
    """Get available metrics organized by category."""
    return {
        'sharpness': {
            'tenengrad': TenengradSharpness(),
            'laplacian': LaplacianVarianceSharpness(),
            'fft': FFTSharpness(),
            'tenengrad_laplacian': TenengradLaplacianSharpness(),
            'tenengrad_fft': TenengradFFTSharpness(),
        },
        'brightness': {
            'median': MedianBrightness(),
            'mean': MeanBrightness(),
            'percentile_25': PercentileBrightness(25),
            'percentile_75': PercentileBrightness(75),
            'histogram': HistogramBrightness(),
            'exposure': ExposureMetric(),
        },
        'contrast': {
            'rms': RMSContrast(),
            'michelson': MichelsonContrast(),
            'weber': WeberContrast(),
            'local': LocalContrast(),
        },
        'noise': {
            'laplacian': LaplacianNoiseEstimation(),
            'gaussian': GaussianNoiseEstimation(),
            'salt_pepper': SaltPepperNoiseDetection(),
        },
        'histogram': {
            'analysis': HistogramAnalysis(),
        }
    }


def load_image(file_path):
    """Load image from file."""
    img = cv2.imread(file_path)
    if img is None:
        raise ValueError(f"Cannot load image from {file_path}")
    return img


def crop_region(image, region):
    """Extract region from image based on rectangle coordinates.
    
    Args:
        image: numpy array (H, W, 3)
        region: dict with keys 'x', 'y', 'width', 'height'
    
    Returns:
        Cropped numpy array
    """
    x = max(0, int(region['x']))
    y = max(0, int(region['y']))
    width = int(region['width'])
    height = int(region['height'])
    
    x2 = min(image.shape[1], x + width)
    y2 = min(image.shape[0], y + height)
    
    return image[y:y2, x:x2]


def calculate_sharpness(image_array, metrics_list, region=None):
    """Calculate sharpness using selected metrics.
    
    Args:
        image_array: numpy array (H, W, 3)
        metrics_list: list of metric names to use (format: "category.metric")
        region: optional region dict to crop image
    
    Returns:
        dict with metric names and scores
    """
    # Crop if region specified
    if region and region.get('width', 0) > 0 and region.get('height', 0) > 0:
        image_array = crop_region(image_array, region)
    
    # Convert to grayscale
    if len(image_array.shape) == 3:
        gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
    else:
        gray = image_array
    
    # Get all metrics
    all_metrics = get_metrics()
    
    # Flatten metrics dict for easier access
    flat_metrics = {}
    for category, category_metrics in all_metrics.items():
        for metric_name, metric_obj in category_metrics.items():
            flat_metrics[f"{category}.{metric_name}"] = metric_obj
    
    # Calculate scores
    results = {}
    for metric_name in metrics_list:
        if metric_name in flat_metrics:
            try:
                score = flat_metrics[metric_name].calculate(gray)
                results[metric_name] = float(score)
            except Exception as e:
                results[metric_name] = None
                print(f"Error calculating {metric_name}: {e}")
        else:
            results[metric_name] = None
            print(f"Unknown metric: {metric_name}")
    
    return results


@app.route('/')
def index():
    """Render main page."""
    return render_template('index.html')


@app.route('/api/metrics', methods=['GET'])
def api_metrics():
    """Get available metrics organized by category."""
    metrics_info = {
        'sharpness': {
            'tenengrad': {
                'name': 'Tenengrad (Sobel)',
                'description': 'Calculates sharpness using Sobel gradient operators'
            },
            'laplacian': {
                'name': 'Laplacian Variance',
                'description': 'Variance of Laplacian kernel response'
            },
            'fft': {
                'name': 'FFT-based',
                'description': 'High-frequency content analysis in frequency domain'
            },
            'tenengrad_laplacian': {
                'name': 'Tenengrad + Laplacian',
                'description': 'Combined Tenengrad and Laplacian metrics'
            },
            'tenengrad_fft': {
                'name': 'Tenengrad + FFT',
                'description': 'Spatial and frequency domain analysis'
            }
        },
        'brightness': {
            'median': {
                'name': 'Median Brightness',
                'description': 'Median pixel value (0-255)'
            },
            'mean': {
                'name': 'Mean Brightness',
                'description': 'Average pixel value (0-255)'
            },
            'percentile_25': {
                'name': 'Brightness 25th Percentile',
                'description': '25% of pixels are darker'
            },
            'percentile_75': {
                'name': 'Brightness 75th Percentile',
                'description': '75% of pixels are darker'
            },
            'histogram': {
                'name': 'Histogram Brightness',
                'description': 'Weighted brightness from histogram'
            },
            'exposure': {
                'name': 'Exposure Quality',
                'description': 'Overall exposure quality score (0-100)'
            }
        },
        'contrast': {
            'rms': {
                'name': 'RMS Contrast',
                'description': 'Root Mean Square contrast (standard deviation)'
            },
            'michelson': {
                'name': 'Michelson Contrast',
                'description': 'Bright vs dark regions contrast (0-1)'
            },
            'weber': {
                'name': 'Weber Contrast',
                'description': 'Object vs background contrast'
            },
            'local': {
                'name': 'Local Contrast',
                'description': 'Contrast in local neighborhoods'
            }
        },
        'noise': {
            'laplacian': {
                'name': 'Laplacian Noise',
                'description': 'Noise estimation using Laplacian filter'
            },
            'gaussian': {
                'name': 'Gaussian Noise',
                'description': 'Gaussian noise estimation'
            },
            'salt_pepper': {
                'name': 'Salt & Pepper Noise',
                'description': 'Impulse noise detection'
            }
        },
        'histogram': {
            'analysis': {
                'name': 'Histogram Analysis',
                'description': 'Overall histogram quality (exposure, clipping, dynamic range)'
            }
        }
    }
    return jsonify(metrics_info)


@app.route('/api/upload', methods=['POST'])
def api_upload():
    """Upload image and return base64."""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Read image
        img_data = file.read()
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Cannot decode image'}), 400
        
        # Save uploaded image
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        cv2.imwrite(filepath, img)
        
        # Get image dimensions
        height, width = img.shape[:2]
        
        # Convert to base64 for display
        _, buffer = cv2.imencode('.jpg', img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'success': True,
            'image': f'data:image/jpeg;base64,{img_base64}',
            'width': width,
            'height': height,
            'filepath': filepath
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/compare', methods=['POST'])
def api_compare():
    """Compare sharpness of two images."""
    try:
        data = request.get_json()
        
        if not data or 'image1' not in data or 'image2' not in data:
            return jsonify({'error': 'Both images required'}), 400
        
        if 'metrics' not in data or not data['metrics']:
            return jsonify({'error': 'At least one metric required'}), 400
        
        # Load images from file paths
        img1 = load_image(data['image1'])
        img2 = load_image(data['image2'])
        
        # Get regions if specified
        region1 = data.get('region1')
        region2 = data.get('region2')
        
        # Calculate sharpness
        scores1 = calculate_sharpness(img1, data['metrics'], region1)
        scores2 = calculate_sharpness(img2, data['metrics'], region2)
        
        # Calculate combined score (average if multiple metrics)
        def get_combined_score(scores):
            valid_scores = [s for s in scores.values() if s is not None]
            if not valid_scores:
                return None
            return sum(valid_scores) / len(valid_scores)
        
        combined1 = get_combined_score(scores1)
        combined2 = get_combined_score(scores2)
        
        # Determine winner
        if combined1 is None or combined2 is None:
            winner = None
        elif combined1 > combined2:
            winner = 'image1'
            difference = ((combined1 - combined2) / combined2 * 100) if combined2 != 0 else 0
        elif combined2 > combined1:
            winner = 'image2'
            difference = ((combined2 - combined1) / combined1 * 100) if combined1 != 0 else 0
        else:
            winner = 'tie'
            difference = 0
        
        # Add RGB histogram data if histogram metrics are used
        rgb_data = None
        if any('histogram' in metric for metric in data['metrics']):
            from src.sharpness.histogram import HistogramAnalysis
            hist_analyzer = HistogramAnalysis()
            try:
                rgb_data = {
                    'image1': hist_analyzer.get_rgb_histograms(img1),
                    'image2': hist_analyzer.get_rgb_histograms(img2)
                }
            except Exception as e:
                print(f"Error calculating RGB histograms: {e}")
        
        result = {
            'success': True,
            'image1': {
                'scores': scores1,
                'combined': combined1
            },
            'image2': {
                'scores': scores2,
                'combined': combined2
            },
            'winner': winner,
            'difference': abs(difference) if difference else 0
        }
        
        if rgb_data:
            result['rgb_histograms'] = rgb_data
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Error in compare: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/cleanup', methods=['POST'])
def api_cleanup():
    """Clean up uploaded files."""
    try:
        data = request.get_json()
        
        for filepath in [data.get('image1'), data.get('image2')]:
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

import os
import cv2
import numpy as np
from PIL import Image

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

def validate_screenshot_file(file_path):
    """Validate that a screenshot file exists and is readable"""
    if not os.path.exists(file_path):
        raise ValidationError(f"Screenshot file not found: {file_path}")
    
    try:
        img = cv2.imread(file_path, 0)
        if img is None:
            raise ValidationError(f"Could not read image file: {file_path}")
        return img
    except Exception as e:
        raise ValidationError(f"Error loading screenshot {file_path}: {str(e)}")

def validate_screenshot_dimensions(img, expected_device='iPhone 11 Pro'):
    """Validate screenshot dimensions match expected device"""
    height, width = img.shape
    
    # Basic sanity checks
    if height < 500 or width < 300:
        raise ValidationError(f"Screenshot too small: {width}x{height}. Expected mobile screenshot dimensions.")
    
    # For now, just warn about unexpected dimensions
    if height != 2436 or width != 1125:  # iPhone 11 Pro dimensions
        print(f"Warning: Screenshot dimensions {width}x{height} don't match iPhone 11 Pro (1125x2436)")
        print("Results may be inaccurate. Consider adding device profile for your screen size.")
    
    return True

def validate_anchor_detection(anchor_result, threshold=0.3):
    """Validate that anchor detection found a good match"""
    max_val = np.max(anchor_result)
    
    if max_val < threshold:
        raise ValidationError(
            f"Anchor detection failed. Best match confidence: {max_val:.3f} "
            f"(threshold: {threshold}). Screenshot may not be from OPTC rumble ranking."
        )
    
    return True

def validate_thumbnail_directory(thumbnail_path):
    """Validate thumbnail directory exists and contains PNG files"""
    if not os.path.exists(thumbnail_path):
        raise ValidationError(f"Thumbnail directory not found: {thumbnail_path}")
    
    # Search recursively for PNG files like make_file_list does
    png_files = []
    for root, _, filenames in os.walk(thumbnail_path):
        for filename in filenames:
            if filename.endswith('.png'):
                png_files.append(os.path.join(root, filename))
    
    if len(png_files) == 0:
        raise ValidationError(f"No PNG files found in thumbnail directory: {thumbnail_path}")
    
    print(f"Found {len(png_files)} thumbnail images")
    return True

def validate_required_files():
    """Validate that required overlay and anchor files exist"""
    required_files = [
        'images/anchor.jpeg',
        'images/null.png',
        'images/overlays/str.png',
        'images/overlays/dex.png',
        'images/overlays/qck.png',
        'images/overlays/psy.png',
        'images/overlays/int.png',
        'images/overlays/dual.png',
        'images/overlays/empty.png',
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        raise ValidationError(f"Required files missing: {', '.join(missing_files)}")
    
    return True
# image/intelligence/image_quality_analyzer.py
import cv2
import numpy as np
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ImageQualityData:
    sharpness: float
    blur_score: float
    contrast: float
    brightness: float
    noise_level: float
    overall_score: float

class ImageQualityAnalyzer:
    @staticmethod
    def analyze(file_path: Path) -> ImageQualityData:
        image = cv2.imread(str(file_path))
        if image is None:
            raise ValueError(f"Could not load image: {file_path}")
            
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Sharpness / Blur
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness = float(laplacian_var)
        blur_score = 100.0 / (sharpness + 1e-5)
        
        # Contrast & Brightness
        brightness = float(np.mean(gray))
        contrast = float(np.std(gray))
        
        # Noise Estimation
        blur_img = cv2.GaussianBlur(gray, (5, 5), 0)
        noise_diff = cv2.absdiff(gray, blur_img)
        noise_level = float(np.mean(noise_diff))
        
        # Overall Score calculation
        score_sharpness = min(100.0, sharpness / 10.0)
        score_contrast = min(100.0, contrast * 1.5)
        score_noise = max(0.0, 100.0 - (noise_level * 10.0))
        
        overall_score = (score_sharpness * 0.4) + (score_contrast * 0.4) + (score_noise * 0.2)
        
        return ImageQualityData(
            sharpness=sharpness,
            blur_score=blur_score,
            contrast=contrast,
            brightness=brightness,
            noise_level=noise_level,
            overall_score=overall_score
        )
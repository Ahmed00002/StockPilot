# image/intelligence/color_analyzer.py
import cv2
import numpy as np
from sklearn.cluster import KMeans
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ColorData:
    dominant_colors: list[tuple[int, int, int]]
    average_color: tuple[int, int, int]
    warm_cool_ratio: float
    saturation_mean: float
    brightness_mean: float

class ColorAnalyzer:
    @staticmethod
    def analyze(file_path: Path, num_colors: int = 5) -> ColorData:
        image = cv2.imread(str(file_path))
        if image is None:
            raise ValueError(f"Could not load image: {file_path}")
            
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pixels = image_rgb.reshape(-1, 3)
        
        # Average Color
        avg_color = tuple(map(int, pixels.mean(axis=0)))
        
        # Dominant Colors (KMeans)
        subsample = pixels[np.random.choice(pixels.shape[0], 10000, replace=False)]
        kmeans = KMeans(n_clusters=num_colors, n_init=10)
        kmeans.fit(subsample)
        dominant_colors = [tuple(map(int, color)) for color in kmeans.cluster_centers_]
        
        # HSV Analysis
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        
        saturation_mean = float(s.mean())
        brightness_mean = float(v.mean())
        
        # Warm/Cool Ratio
        warm_mask = ((h < 30) | (h > 150)) & (s > 20)
        cool_mask = (h >= 60) & (h <= 150) & (s > 20)
        
        warm_pixels = np.count_nonzero(warm_mask)
        cool_pixels = np.count_nonzero(cool_mask)
        
        total_colored = warm_pixels + cool_pixels
        warm_cool_ratio = float(warm_pixels / total_colored) if total_colored > 0 else 0.5
        
        return ColorData(
            dominant_colors=dominant_colors,
            average_color=avg_color,
            warm_cool_ratio=warm_cool_ratio,
            saturation_mean=saturation_mean,
            brightness_mean=brightness_mean
        )
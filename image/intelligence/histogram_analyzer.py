# image/intelligence/histogram_analyzer.py
import cv2
import numpy as np
from dataclasses import dataclass
from pathlib import Path

@dataclass
class HistogramData:
    red: np.ndarray
    green: np.ndarray
    blue: np.ndarray
    luminance: np.ndarray

class HistogramAnalyzer:
    @staticmethod
    def analyze(file_path: Path) -> HistogramData:
        image = cv2.imread(str(file_path))
        if image is None:
            raise ValueError(f"Could not load image: {file_path}")

        b, g, r = cv2.split(image)
        
        hist_b = cv2.calcHist([b], [0], None, [256], [0, 256]).flatten()
        hist_g = cv2.calcHist([g], [0], None, [256], [0, 256]).flatten()
        hist_r = cv2.calcHist([r], [0], None, [256], [0, 256]).flatten()
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        hist_luma = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()

        return HistogramData(
            red=hist_r,
            green=hist_g,
            blue=hist_b,
            luminance=hist_luma
        )
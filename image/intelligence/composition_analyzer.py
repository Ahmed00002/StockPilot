# image/intelligence/composition_analyzer.py
import cv2
import numpy as np
from dataclasses import dataclass
from pathlib import Path

@dataclass
class CompositionData:
    rule_of_thirds_score: float
    symmetry_score: float
    leading_lines_detected: bool
    focal_points: int
    balance_score: float
    composition_notes: list[str]

class CompositionAnalyzer:
    @staticmethod
    def analyze(file_path: Path) -> CompositionData:
        image = cv2.imread(str(file_path))
        if image is None:
            raise ValueError(f"Could not load image: {file_path}")
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape
        
        notes = []
        
        # Rule of Thirds Analysis
        thirds_h = height // 3
        thirds_w = width // 3
        
        regions = [
            gray[0:thirds_h, 0:thirds_w],
            gray[0:thirds_h, thirds_w*2:width],
            gray[thirds_h*2:height, 0:thirds_w],
            gray[thirds_h*2:height, thirds_w*2:width]
        ]
        
        edge_scores = []
        for region in regions:
            edges = cv2.Canny(region, 50, 150)
            edge_density = np.count_nonzero(edges) / edges.size
            edge_scores.append(edge_density)
        
        rule_of_thirds_score = min(100.0, (sum(edge_scores) / len(edge_scores)) * 100 * 1.5)
        if rule_of_thirds_score > 50:
            notes.append("Strong compositional elements at rule of thirds intersections")
        
        # Symmetry Analysis (vertical split)
        mid_x = width // 2
        left_half = gray[:, :mid_x]
        right_half_flipped = cv2.flip(gray[:, mid_x:], 1)
        
        if left_half.shape == right_half_flipped.shape:
            correlation = np.corrcoef(left_half.flatten(), right_half_flipped.flatten())[0, 1]
            symmetry_score = max(0, min(100, (correlation + 1) * 50))
        else:
            symmetry_score = 0
        
        if symmetry_score > 70:
            notes.append("High vertical symmetry detected")
        
        # Leading Lines Detection (using Hough Line Transform)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=100)
        
        leading_lines_detected = False
        if lines is not None:
            horizontal_count = 0
            vertical_count = 0
            diagonal_count = 0
            
            for rho, theta in lines[:20]:
                angle = np.degrees(theta)
                if angle < 10 or angle > 170:
                    horizontal_count += 1
                elif 80 < angle < 100:
                    vertical_count += 1
                else:
                    diagonal_count += 1
            
            if diagonal_count >= 2:
                leading_lines_detected = True
                notes.append("Diagonal leading lines detected")
        
        # Focal Points (high contrast areas)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        abs_laplacian = np.absolute(laplacian)
        normalized = cv2.normalize(abs_laplacian, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
        
        threshold = np.mean(normalized) + np.std(normalized)
        _, focal_mask = cv2.threshold(normalized, threshold, 255, cv2.THRESH_BINARY)
        
        contours, _ = cv2.findContours(focal_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        focal_points = len([c for c in contours if cv2.contourArea(c) > 100])
        
        if focal_points == 1:
            notes.append("Single strong focal point identified")
        elif focal_points > 1:
            notes.append(f"Multiple ({focal_points}) focal points detected")
        
        # Balance Score (distribution of visual weight)
        quadrants = [
            gray[0:height//2, 0:width//2],
            gray[0:height//2, width//2:],
            gray[height//2:, 0:width//2],
            gray[height//2:, width//2:]
        ]
        
        quadrant_weights = [np.mean(q) for q in quadrants]
        weight_variance = np.var(quadrant_weights)
        balance_score = max(0, 100 - (weight_variance / 10))
        
        if balance_score > 70:
            notes.append("Well-balanced composition")
        
        return CompositionData(
            rule_of_thirds_score=rule_of_thirds_score,
            symmetry_score=symmetry_score,
            leading_lines_detected=leading_lines_detected,
            focal_points=focal_points,
            balance_score=balance_score,
            composition_notes=notes
        )
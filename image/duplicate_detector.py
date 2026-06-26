# image/duplicate_detector.py
from typing import List, Dict, Tuple
from collections import defaultdict
from image.image_model import ImageModel

class DuplicateDetector:
    """Analyzes models to identify exact byte matches and perceptual near-matches."""

    @staticmethod
    def find_exact_duplicates(images: List[ImageModel]) -> Dict[str, List[ImageModel]]:
        """Groups images by exact SHA-256 hash match."""
        groups = defaultdict(list)
        for img in images:
            if img.sha256_hash:
                groups[img.sha256_hash].append(img)
                
        return {h: group for h, group in groups.items() if len(group) > 1}

    @staticmethod
    def find_near_duplicates(images: List[ImageModel], threshold: int = 5) -> List[Tuple[ImageModel, ImageModel, int]]:
        """Compares perceptual hashes using Hamming Distance."""
        def hamming_distance(h1: str, h2: str) -> int:
            if not h1 or not h2: return 999
            try:
                b1, b2 = int(h1, 16), int(h2, 16)
                return bin(b1 ^ b2).count('1')
            except ValueError:
                return 999

        matches = []
        img_count = len(images)
        for i in range(img_count):
            for j in range(i + 1, img_count):
                img1, img2 = images[i], images[j]
                dist = hamming_distance(img1.perceptual_hash, img2.perceptual_hash)
                if dist <= threshold:
                    matches.append((img1, img2, dist))
                    
        return sorted(matches, key=lambda x: x[2])
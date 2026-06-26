# image/intelligence/image_fingerprint.py
import hashlib
import cv2
import numpy as np
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ImageFingerprint:
    sha256_hash: str
    perceptual_hash: str
    visual_signature: np.ndarray

class ImageFingerprintGenerator:
    @staticmethod
    def generate_sha256(file_path: Path) -> str:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    @staticmethod
    def generate_phash(image: np.ndarray) -> str:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (32, 32), interpolation=cv2.INTER_AREA)
        dct = cv2.dct(np.float32(resized))
        dctlowfreq = dct[:8, :8]
        med = np.median(dctlowfreq)
        diff = dctlowfreq > med
        return "".join(str(int(b)) for b in diff.flatten())

    @staticmethod
    def generate_fingerprint(file_path: Path) -> ImageFingerprint:
        image = cv2.imread(str(file_path))
        if image is None:
            raise ValueError(f"Failed to read image at {file_path}")
            
        sha256_hash = ImageFingerprintGenerator.generate_sha256(file_path)
        phash = ImageFingerprintGenerator.generate_phash(image)
        
        hist = cv2.calcHist([image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        visual_signature = cv2.normalize(hist, hist).flatten()

        return ImageFingerprint(
            sha256_hash=sha256_hash,
            perceptual_hash=phash,
            visual_signature=visual_signature
        )
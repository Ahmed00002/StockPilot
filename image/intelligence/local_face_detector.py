# image/intelligence/local_face_detector.py
import cv2
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class FaceDetectionResult:
    faces_detected: int
    face_locations: list[tuple[int, int, int, int]]
    confidence_scores: list[float]
    primary_face_location: tuple[int, int, int, int] | None
    face_sizes: list[tuple[int, int]]

class LocalFaceDetector:
    def __init__(self):
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        eye_path = cv2.data.haarcascades + 'haarcascade_eye.xml'
        self.eye_cascade = cv2.CascadeClassifier(eye_path)

    def detect_faces(self, file_path: Path, min_neighbors: int = 5) -> FaceDetectionResult:
        image = cv2.imread(str(file_path))
        if image is None:
            raise ValueError(f"Could not load image: {file_path}")
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=min_neighbors,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        face_locations = []
        confidence_scores = []
        face_sizes = []
        
        for (x, y, w, h) in faces:
            face_locations.append((int(x), int(y), int(w), int(h)))
            face_sizes.append((int(w), int(h)))
            
            roi_gray = gray[y:y+h, x:x+w]
            eyes = self.eye_cascade.detectMultiScale(roi_gray, 1.1, 3)
            
            eye_confidence = min(1.0, len(eyes) / 2.0)
            size_factor = min(1.0, (w * h) / (image.shape[0] * image.shape[1]) * 10)
            confidence = (eye_confidence * 0.6 + size_factor * 0.4)
            confidence_scores.append(round(confidence, 2))
        
        primary_face = None
        if face_locations:
            largest_idx = 0
            largest_area = 0
            for i, (w, h) in enumerate(face_sizes):
                area = w * h
                if area > largest_area:
                    largest_area = area
                    largest_idx = i
            primary_face = face_locations[largest_idx]
        
        return FaceDetectionResult(
            faces_detected=len(face_locations),
            face_locations=face_locations,
            confidence_scores=confidence_scores,
            primary_face_location=primary_face,
            face_sizes=face_sizes
        )

    def has_faces(self, file_path: Path) -> bool:
        result = self.detect_faces(file_path)
        return result.faces_detected > 0
# image/intelligence/image_intelligence_manager.py
import concurrent.futures
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any
import logging

from .technical_analyzer import TechnicalAnalyzer, TechnicalData
from .color_analyzer import ColorAnalyzer, ColorData
from .histogram_analyzer import HistogramAnalyzer, HistogramData
from .image_quality_analyzer import ImageQualityAnalyzer, ImageQualityData
from .metadata_reader import MetadataReader, ImageMetadata
from .image_fingerprint import ImageFingerprintGenerator, ImageFingerprint

logger = logging.getLogger("ImageIntelligenceManager")

@dataclass
class IntelligenceReport:
    file_path: Path
    fingerprint: ImageFingerprint
    technical: TechnicalData
    quality: ImageQualityData
    color: ColorData
    metadata: ImageMetadata
    histogram: HistogramData

class ImageIntelligenceManager:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers)
        self.cache: Dict[str, IntelligenceReport] = {}

    def analyze_image(self, file_path: Path) -> IntelligenceReport:
        path_str = str(file_path)
        if path_str in self.cache:
            return self.cache[path_str]

        try:
            logger.info(f"Starting intelligence analysis for {file_path}")
            fingerprint = ImageFingerprintGenerator.generate_fingerprint(file_path)
            technical = TechnicalAnalyzer.analyze(file_path)
            quality = ImageQualityAnalyzer.analyze(file_path)
            color = ColorAnalyzer.analyze(file_path)
            metadata = MetadataReader.extract(file_path)
            histogram = HistogramAnalyzer.analyze(file_path)

            report = IntelligenceReport(
                file_path=file_path,
                fingerprint=fingerprint,
                technical=technical,
                quality=quality,
                color=color,
                metadata=metadata,
                histogram=histogram
            )
            
            self.cache[path_str] = report
            return report
        except Exception as e:
            logger.error(f"Error analyzing image {file_path}: {str(e)}")
            raise

    def analyze_batch(self, file_paths: list[Path]) -> list[IntelligenceReport]:
        reports = []
        futures = {self.executor.submit(self.analyze_image, path): path for path in file_paths}
        
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                reports.append(result)
            except Exception as e:
                logger.error(f"Batch analysis error: {str(e)}")
                
        return reports
        
    def shutdown(self):
        self.executor.shutdown(wait=True)
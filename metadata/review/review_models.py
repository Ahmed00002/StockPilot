# metadata/review/review_models.py
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum

class ReviewSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class ReviewRecommendation:
    category: str
    message: str
    severity: ReviewSeverity
    explanation: str
    actionable: bool = True

@dataclass
class ComponentScores:
    title: float = 0.0
    description: float = 0.0
    keywords: float = 0.0
    seo: float = 0.0
    commercial: float = 0.0
    grammar: float = 0.0
    readability: float = 0.0
    marketplace: float = 0.0
    confidence: float = 0.0

@dataclass
class MetadataPackage:
    title: str
    description: str
    keywords: List[str]
    subject: str = ""
    scene: str = ""
    objects: str = ""
    style: str = ""
    concepts: str = ""

@dataclass
class ReviewReport:
    is_approved: bool
    overall_score: float
    component_scores: ComponentScores
    recommendations: List[ReviewRecommendation]
    warnings: List[ReviewRecommendation]
    critical_errors: List[ReviewRecommendation]
    original_package: MetadataPackage
    improved_package: Optional[MetadataPackage] = None
    revision_count: int = 0
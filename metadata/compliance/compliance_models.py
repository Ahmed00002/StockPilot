# metadata/compliance/compliance_models.py
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any

class ComplianceStatus(Enum):
    READY = "Ready"
    NEEDS_REVIEW = "Needs Review"
    MAJOR_ISSUES = "Major Issues"
    NOT_READY = "Not Ready"

class Severity(Enum):
    INFO = "Info"
    WARNING = "Warning"
    CRITICAL = "Critical"

@dataclass
class ComplianceIssue:
    category: str
    message: str
    severity: Severity
    explanation: str
    actionable: bool = True

@dataclass
class UploadReadinessScore:
    overall: float = 0.0
    marketplace: float = 0.0
    metadata: float = 0.0
    seo: float = 0.0
    commercial: float = 0.0
    compliance: float = 0.0

@dataclass
class ComplianceReport:
    image_hash: str
    marketplace_name: str
    status: ComplianceStatus
    scores: UploadReadinessScore
    warnings: List[ComplianceIssue] = field(default_factory=list)
    recommendations: List[ComplianceIssue] = field(default_factory=list)
    critical_errors: List[ComplianceIssue] = field(default_factory=list)
    editorial_advisory: Optional[str] = None
    release_reminder: Optional[str] = None
    timestamp: str = ""
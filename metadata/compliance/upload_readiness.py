# metadata/compliance/upload_readiness.py
import logging
from typing import List
from metadata.compliance.compliance_models import UploadReadinessScore, ComplianceStatus, ComplianceIssue, Severity

logger = logging.getLogger(__name__)

class UploadReadinessCalculator:
    def __init__(self):
        pass

    def calculate(self, issues: List[ComplianceIssue], raw_seo: float, raw_comm: float) -> tuple[UploadReadinessScore, ComplianceStatus]:
        criticals = sum(1 for i in issues if i.severity == Severity.CRITICAL)
        warnings = sum(1 for i in issues if i.severity == Severity.WARNING)
        
        compliance_score = max(0.0, 100.0 - (criticals * 40.0) - (warnings * 10.0))
        metadata_score = max(0.0, 100.0 - (warnings * 5.0))
        marketplace_score = 100.0 if criticals == 0 else 0.0
        
        overall = (
            (compliance_score * 0.4) +
            (marketplace_score * 0.3) +
            (metadata_score * 0.1) +
            (raw_seo * 0.1) +
            (raw_comm * 0.1)
        )
        
        score_obj = UploadReadinessScore(
            overall=round(overall, 2),
            marketplace=round(marketplace_score, 2),
            metadata=round(metadata_score, 2),
            seo=round(raw_seo, 2),
            commercial=round(raw_comm, 2),
            compliance=round(compliance_score, 2)
        )
        
        if criticals > 0:
            status = ComplianceStatus.NOT_READY
        elif warnings > 2 or overall < 70.0:
            status = ComplianceStatus.MAJOR_ISSUES
        elif warnings > 0 or overall < 85.0:
            status = ComplianceStatus.NEEDS_REVIEW
        else:
            status = ComplianceStatus.READY
            
        return score_obj, status
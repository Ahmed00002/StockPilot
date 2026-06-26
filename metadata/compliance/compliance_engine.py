# metadata/compliance/compliance_engine.py
import logging
from datetime import datetime
from typing import List, Dict, Any

from metadata.compliance.compliance_models import ComplianceReport, ComplianceIssue, Severity, ComplianceStatus
from metadata.compliance.marketplace_registry import MarketplaceRegistry
from metadata.compliance.title_compliance import TitleComplianceValidator
from metadata.compliance.description_compliance import DescriptionComplianceValidator
from metadata.compliance.keyword_compliance import KeywordComplianceValidator
from metadata.compliance.brand_detector import BrandDetector
from metadata.compliance.trademark_detector import TrademarkDetector
from metadata.compliance.editorial_detector import EditorialDetector
from metadata.compliance.commercial_detector import CommercialValueDetector
from metadata.compliance.release_checker import ReleaseChecker
from metadata.compliance.upload_readiness import UploadReadinessCalculator
from metadata.compliance.warning_engine import WarningEngine
from metadata.compliance.recommendation_engine import RecommendationEngine

logger = logging.getLogger(__name__)

class MarketplaceComplianceEngine:
    def __init__(self):
        self.registry = MarketplaceRegistry()
        self.title_validator = TitleComplianceValidator()
        self.desc_validator = DescriptionComplianceValidator()
        self.kw_validator = KeywordComplianceValidator()
        self.brand_detector = BrandDetector()
        self.trademark_detector = TrademarkDetector()
        self.editorial_detector = EditorialDetector()
        self.commercial_detector = CommercialValueDetector()
        self.release_checker = ReleaseChecker()
        self.readiness_calc = UploadReadinessCalculator()
        self.warning_engine = WarningEngine()
        self.recommendation_engine = RecommendationEngine()

    def run_compliance_check(self, image_hash: str, title: str, description: str, keywords: List[str], marketplace_key: str = "adobe_stock", raw_seo: float = 80.0, raw_comm: float = 80.0) -> ComplianceReport:
        logger.info(f"Running compliance check for {image_hash} against {marketplace_key}")
        
        marketplace = self.registry.get_marketplace(marketplace_key)
        rules = marketplace.get_rules()
        
        all_issues: List[ComplianceIssue] = []
        
        all_issues.extend(self.title_validator.validate(title, rules))
        all_issues.extend(self.desc_validator.validate(description, rules))
        all_issues.extend(self.kw_validator.validate(keywords, rules))
        
        for text, source in [(title, "Title"), (description, "Description")] + [(kw, "Keyword") for kw in keywords]:
            for brand, msg in self.brand_detector.detect(text):
                all_issues.append(ComplianceIssue("Brand", f"[{source}] {msg}: '{brand}'", Severity.CRITICAL, "Remove brand names to avoid rejection.", True))
            for tm, msg in self.trademark_detector.detect(text):
                all_issues.append(ComplianceIssue("Trademark", f"[{source}] {msg}: '{tm}'", Severity.CRITICAL, "Remove trademarks to avoid rejection.", True))

        edit_issue = self.editorial_detector.detect(title, description, keywords)
        if edit_issue:
            all_issues.append(edit_issue)

        comm_issue = self.commercial_detector.detect(keywords)
        if comm_issue:
            all_issues.append(comm_issue)

        all_issues.extend(self.release_checker.check(keywords))

        scores, status = self.readiness_calc.calculate(all_issues, raw_seo, raw_comm)
        
        criticals = [i for i in all_issues if i.severity == Severity.CRITICAL]
        warnings = self.warning_engine.filter_warnings(all_issues)
        recommendations = self.recommendation_engine.filter_actionable(all_issues)

        report = ComplianceReport(
            image_hash=image_hash,
            marketplace_name=marketplace.name,
            status=status,
            scores=scores,
            warnings=warnings,
            recommendations=recommendations,
            critical_errors=criticals,
            editorial_advisory=edit_issue.message if edit_issue else None,
            release_reminder="Review image for identifiable people/property." if any(i.category == "Legal" for i in all_issues) else None,
            timestamp=datetime.utcnow().isoformat()
        )
        
        logger.info(f"Compliance check completed. Status: {status.value}")
        return report
# metadata/review/self_improvement.py
import json
import logging
from typing import Any, Optional

from metadata.review.review_models import MetadataPackage, ReviewReport, ReviewRecommendation

logger = logging.getLogger(__name__)

class SelfImprovementEngine:
    def __init__(self, ai_manager: Any):
        self.ai_manager = ai_manager

    def refine(self, package: MetadataPackage, report: ReviewReport) -> Optional[MetadataPackage]:
        if report.revision_count >= 1:
            logger.info("Maximum revision count reached. Skipping self-improvement.")
            return None
            
        critical_issues = [r.message for r in report.critical_errors]
        warnings = [r.message for r in report.warnings]
        recommendations = [r.message for r in report.recommendations if r.actionable]
        
        if not critical_issues and not recommendations:
            logger.info("No actionable issues found for self-improvement.")
            return None

        system_prompt = (
            "You are an expert Metadata Optimizer for Commercial Stock Photography. "
            "Your task is to refine the provided metadata package based strictly on the review feedback. "
            "Fix grammar, remove trademarks, eliminate duplicates, and improve SEO/Commercial value. "
            "Respond strictly with a JSON object containing 'title', 'description', and 'keywords' (list of strings)."
        )
        
        user_prompt = (
            f"Original Title: {package.title}\n"
            f"Original Description: {package.description}\n"
            f"Original Keywords: {json.dumps(package.keywords)}\n\n"
            "Review Feedback:\n"
            f"Critical Issues: {json.dumps(critical_issues)}\n"
            f"Warnings: {json.dumps(warnings)}\n"
            f"Recommendations: {json.dumps(recommendations)}\n\n"
            "Generate the improved metadata package."
        )

        try:
            schema = {
                "type": "object", 
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "keywords": {"type": "array", "items": {"type": "string"}}
                }
            }
            
            response = self.ai_manager.generate_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                schema=schema
            )
            
            data = json.loads(response)
            
            improved = MetadataPackage(
                title=data.get('title', package.title),
                description=data.get('description', package.description),
                keywords=data.get('keywords', package.keywords),
                subject=package.subject,
                scene=package.scene,
                objects=package.objects,
                style=package.style,
                concepts=package.concepts
            )
            
            logger.info("Self-improvement refinement completed.")
            return improved
            
        except Exception as e:
            logger.error(f"Self-improvement failed: {e}")
            return None
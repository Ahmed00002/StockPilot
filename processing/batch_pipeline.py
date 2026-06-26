# processing/batch_pipeline.py
import logging
from typing import Any

from processing.batch_context import BatchContext
from processing.job_result import JobResult

logger = logging.getLogger(__name__)

class BatchPipeline:
    def __init__(self, ai_manager: Any, metadata_engine: Any, review_engine: Any, compliance_engine: Any, workspace_manager: Any):
        self.ai_manager = ai_manager
        self.metadata = metadata_engine
        self.review = review_engine
        self.compliance = compliance_engine
        self.workspace = workspace_manager

    def execute(self, context: BatchContext) -> JobResult:
        try:
            logger.debug(f"Pipeline started for {context.job.job_id}")
            
            vision_data = self.metadata.vision_pipeline.process(context.job.image_path)
            context.set_vision_data(vision_data)

            metadata_package = self.metadata.generate_full_package(
                image_path=context.job.image_path,
                vision_data=vision_data
            )
            context.set_metadata(metadata_package)

            review_report = self.review.review(metadata_package)
            context.set_review_report(review_report)

            if not review_report.is_approved:
                metadata_package = self.review.request_improvement(review_report).improved_package or metadata_package
                context.set_metadata(metadata_package)

            compliance_report = self.compliance.run_compliance_check(
                image_hash=vision_data.get('hash', 'unknown'),
                title=metadata_package.title,
                description=metadata_package.description,
                keywords=metadata_package.keywords
            )
            context.set_compliance_report(compliance_report)

            # INTEGRATION FIX: Prevented fatal crash by safely handling orchestrator-managed AI provider state
            provider_name = getattr(self.ai_manager, 'default_provider', 'Auto-Routed')

            snapshot = self.workspace.save_current(
                image_hash=vision_data.get('hash', 'unknown'),
                title=metadata_package.title,
                description=metadata_package.description,
                keywords=metadata_package.keywords,
                provider=provider_name,
                reason="batch_generation",
                scores={"overall": review_report.overall_score}
            )
            
            logger.debug(f"Pipeline completed for {context.job.job_id}")
            return JobResult(success=True, context=context, snapshot=snapshot)
            
        except Exception as e:
            logger.exception(f"Pipeline failed for {context.job.job_id}")
            return JobResult(success=False, error_message=str(e), context=context)
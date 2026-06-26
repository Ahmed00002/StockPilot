# integration/integration_manager.py
import logging
import time
from typing import Any, Dict, Optional

from integration.metadata_pipeline_events import PipelineEventManager, PipelineEvent
from integration.pipeline_health_monitor import PipelineHealthMonitor
from integration.dependency_checker import DependencyChecker
from integration.performance_profiler import PerformanceProfiler
from integration.pipeline_diagnostics import PipelineDiagnostics
from integration.cache_validator import CacheValidator

# INTEGRATION FIX: Moved inline imports to module level
from metadata.keywords.keyword_generator import KeywordGenerationContext
from metadata.review.review_models import MetadataPackage

logger = logging.getLogger(__name__)

class PipelineIntegrationManager:
    def __init__(self, ai_manager: Any, vision_engine: Any, title_engine: Any, desc_engine: Any, kw_engine: Any, review_engine: Any, compliance_engine: Any, workspace_manager: Any):
        self.ai = ai_manager
        self.vision = vision_engine
        self.title = title_engine
        self.desc = desc_engine
        self.kw = kw_engine
        self.review = review_engine
        self.compliance = compliance_engine
        self.workspace = workspace_manager
        
        self.events = PipelineEventManager()
        self.health = PipelineHealthMonitor(self.ai, self.vision, self.workspace, self.events)
        self.deps = DependencyChecker()
        self.profiler = PerformanceProfiler()
        self.diagnostics = PipelineDiagnostics(self.health, self.deps, self.profiler)
        self.cache_validator = CacheValidator(self.title, self.desc, self.kw)

    def initialize_pipeline(self) -> bool:
        logger.info("Initializing integrated metadata pipeline...")
        dep_ok, _ = self.deps.check_dependencies()
        if not dep_ok:
            logger.critical("Dependency check failed. Pipeline cannot start.")
            return False
            
        if not self.health.is_pipeline_healthy():
            logger.critical("Health check failed. Pipeline cannot start.")
            return False
            
        logger.info("Pipeline initialized successfully.")
        return True

    def process_image(self, image_path: str, job_id: str, marketplace: str = "adobe_stock") -> Dict[str, Any]:
        self.events.emit(PipelineEvent.PIPELINE_START, job_id=job_id, image_path=image_path)
        
        try:
            self.profiler.start_stage(job_id, "vision")
            vision_data = self.vision.process(image_path)
            image_hash = vision_data.get('hash', 'unknown')
            self.profiler.end_stage(job_id, "vision")

            # INTEGRATION FIX: Safe provider lookup
            provider = getattr(self.ai, 'default_provider', 'Auto-Routed')
            prompt_version = "v1.0"
            language = "en"
            
            if self.cache_validator.validate_cache_integrity(image_hash, marketplace, language, provider, prompt_version):
                self.events.emit(PipelineEvent.CACHE_HIT, job_id=job_id, image_hash=image_hash)
            
            subject = vision_data.get('subject', '')
            scene = vision_data.get('scene', '')
            objects = vision_data.get('objects', '')
            style = vision_data.get('style', '')
            concepts = vision_data.get('concepts', '')
            v_keywords = vision_data.get('keywords', '')

            self.profiler.start_stage(job_id, "title")
            title_res = self.title.process_asset(image_hash, subject, concepts, v_keywords, marketplace, language)
            self.profiler.end_stage(job_id, "title")
            
            self.profiler.start_stage(job_id, "description")
            desc_res = self.desc.process_asset(image_hash, subject, scene, objects, style, concepts, v_keywords, marketplace, language)
            self.profiler.end_stage(job_id, "description")

            self.profiler.start_stage(job_id, "keywords")
            kw_ctx = KeywordGenerationContext(subject, scene, objects, style, concepts, marketplace, language)
            kw_pool = self.kw.generator.generate_candidate_pool(kw_ctx)
            kw_res = self.kw.process_pipeline(image_hash, kw_pool, marketplace, language)
            self.profiler.end_stage(job_id, "keywords")

            package = MetadataPackage(
                title=title_res.get('title', ''),
                description=desc_res.get('description', ''),
                keywords=kw_res.get('final_keywords', []),
                subject=subject, scene=scene, objects=objects, style=style, concepts=concepts
            )

            self.profiler.start_stage(job_id, "review")
            review_report = self.review.review(package)
            if not review_report.is_approved:
                review_report = self.review.request_improvement(review_report)
                if review_report.improved_package:
                    package = review_report.improved_package
            self.profiler.end_stage(job_id, "review")

            self.profiler.start_stage(job_id, "compliance")
            comp_report = self.compliance.run_compliance_check(
                image_hash, package.title, package.description, package.keywords, marketplace, 
                review_report.component_scores.seo, review_report.component_scores.commercial
            )
            self.profiler.end_stage(job_id, "compliance")

            self.profiler.start_stage(job_id, "workspace")
            snapshot = self.workspace.save_current(
                image_hash=image_hash,
                title=package.title,
                description=package.description,
                keywords=package.keywords,
                provider=provider,
                reason="pipeline_generation",
                scores={"overall": review_report.overall_score, "compliance": comp_report.scores.compliance}
            )
            self.profiler.end_stage(job_id, "workspace")

            result = {
                "success": True,
                "image_hash": image_hash,
                "snapshot_id": snapshot.snapshot_id,
                "metadata": package,
                "review_score": review_report.overall_score,
                "compliance_status": comp_report.status.value
            }
            
            self.events.emit(PipelineEvent.PIPELINE_COMPLETE, job_id=job_id, result=result)
            return result

        except Exception as e:
            logger.exception(f"Pipeline execution failed for job {job_id}")
            self.events.emit(PipelineEvent.PIPELINE_ERROR, job_id=job_id, error=str(e))
            return {"success": False, "error": str(e)}
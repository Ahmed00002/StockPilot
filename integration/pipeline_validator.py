# integration/pipeline_validator.py
import logging
from typing import Any

from integration.integration_manager import PipelineIntegrationManager

logger = logging.getLogger(__name__)

class PipelineValidator:
    def __init__(self, integration_manager: PipelineIntegrationManager):
        self.manager = integration_manager

    def validate_end_to_end(self, test_image_path: str) -> bool:
        logger.info("Starting End-to-End Pipeline Validation...")
        
        if not self.manager.initialize_pipeline():
            logger.error("Validation Failed: Pipeline initialization failed.")
            return False
            
        diag = self.manager.diagnostics.run_full_diagnostics()
        if diag["status"] != "Healthy":
            logger.error(f"Validation Failed: Diagnostics indicate critical issues: {diag}")
            return False

        logger.info(f"Running test image through pipeline: {test_image_path}")
        result = self.manager.process_image(test_image_path, job_id="validation_job_001")
        
        if not result.get("success"):
            logger.error(f"Validation Failed: Processing error - {result.get('error')}")
            return False
            
        if not result.get("metadata"):
            logger.error("Validation Failed: No metadata package returned.")
            return False
            
        logger.info(f"End-to-End Validation Successful. Review Score: {result.get('review_score')}")
        return True
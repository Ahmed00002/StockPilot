# ai/prompt/template_loader.py
import json
import logging
from pathlib import Path
from typing import List, Optional

from .prompt_template import PromptTemplate

logger = logging.getLogger("TemplateLoader")

class TemplateLoader:
    """Handles persistence and retrieval of templates from local filesystem boundaries."""

    def __init__(self, storage_directory: Path):
        self.storage_directory = storage_directory
        self.storage_directory.mkdir(parents=True, exist_ok=True)

    def load_all(self) -> List[PromptTemplate]:
        templates = []
        for file_path in self.storage_directory.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    templates.append(PromptTemplate(**data))
            except Exception as e:
                logger.error(f"Failed to load prompt template from {file_path}: {str(e)}")
        return templates

    def save(self, template: PromptTemplate) -> bool:
        file_path = self.storage_directory / f"{template.id}.json"
        try:
            # Handle datetime serialization cleanly
            data = template.__dict__.copy()
            data['created_at'] = template.created_at.isoformat()
            data['updated_at'] = template.updated_at.isoformat()
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Failed to save prompt template {template.id}: {str(e)}")
            return False

    def delete(self, template_id: str) -> bool:
        file_path = self.storage_directory / f"{template_id}.json"
        try:
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete prompt template {template_id}: {str(e)}")
            return False
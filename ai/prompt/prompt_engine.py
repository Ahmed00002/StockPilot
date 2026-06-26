# ai/prompt/prompt_engine.py
from pathlib import Path

from .prompt_manager import PromptManager

class PromptEngine:
    """Core entrypoint instance wrapping the Prompt Intelligence subsystem."""
    
    def __init__(self, root_storage_path: Path):
        self.templates_dir = root_storage_path / "templates"
        self.manager = PromptManager(self.templates_dir)
        
    def startup(self) -> None:
        self.manager.initialize()
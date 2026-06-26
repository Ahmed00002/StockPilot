# workspace/workspace.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import uuid
from workspace.workspace_paths import WorkspacePaths

@dataclass
class WorkspaceSettings:
    """User-configurable settings bound to a specific workspace."""
    theme: str = "dark"
    marketplace: str = "Default"
    language: str = "en"
    keyword_limit: int = 50
    default_provider: str = ""
    default_prompt: str = ""
    auto_save: bool = True
    auto_backup: bool = True
    thumbnail_size: int = 256

@dataclass
class WorkspaceState:
    """Transient state data restored upon workspace load."""
    last_page: str = "dashboard"
    sidebar_collapsed: bool = False
    window_maximized: bool = False
    window_width: int = 1280
    window_height: int = 720

@dataclass
class Workspace:
    """Domain entity representing an isolated StockPilot project environment."""
    name: str
    root_path: str
    
    workspace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    author: str = ""
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    modified_date: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = "1.0.0"
    
    workspace_icon: str = "folder"
    marketplace_profile: str = "Generic"
    status: str = "Active"
    tags: List[str] = field(default_factory=list)
    color_label: str = "#007acc"
    is_pinned: bool = False
    is_favorite: bool = False
    
    settings: WorkspaceSettings = field(default_factory=WorkspaceSettings)
    state: WorkspaceState = field(default_factory=WorkspaceState)

    @property
    def paths(self) -> WorkspacePaths:
        from pathlib import Path
        return WorkspacePaths(Path(self.root_path))
        
    def touch(self) -> None:
        self.modified_date = datetime.now().isoformat()
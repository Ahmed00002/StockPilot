# workspace/workspace_paths.py
from pathlib import Path
from dataclasses import dataclass

@dataclass(frozen=True)
class WorkspacePaths:
    """Immutable structural mapping of a workspace's internal directories."""
    root: Path
    
    @property
    def images(self) -> Path: return self.root / "images"
    @property
    def metadata(self) -> Path: return self.root / "metadata"
    @property
    def exports(self) -> Path: return self.root / "exports"
    @property
    def history(self) -> Path: return self.root / "history"
    @property
    def cache(self) -> Path: return self.root / "cache"
    @property
    def logs(self) -> Path: return self.root / "logs"
    @property
    def prompts(self) -> Path: return self.root / "prompts"
    @property
    def thumbnails(self) -> Path: return self.root / "thumbnails"
    @property
    def backups(self) -> Path: return self.root / "backups"
    @property
    def settings(self) -> Path: return self.root / "settings"
    @property
    def reports(self) -> Path: return self.root / "reports"
    @property
    def templates(self) -> Path: return self.root / "templates"
    @property
    def temp(self) -> Path: return self.root / "temp"
    
    @property
    def config_file(self) -> Path: return self.root / "workspace.json"

    def get_all_directories(self) -> list[Path]:
        return [
            self.images, self.metadata, self.exports, self.history,
            self.cache, self.logs, self.prompts, self.thumbnails,
            self.backups, self.settings, self.reports, self.templates, self.temp
        ]
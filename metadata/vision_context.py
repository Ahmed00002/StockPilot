# metadata/vision_context.py
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from image.intelligence.image_intelligence_manager import IntelligenceReport


@dataclass(frozen=True)
class VisionContext:
    """
    Domain payload for turning local image intelligence into a provider-ready vision request.
    """

    workspace: str
    image_path: Path
    intelligence_report: "IntelligenceReport"
    provider_name: str
    marketplace: str = "adobe_stock"
    language: str = "en"
    prompt_template_id: str = "stock_metadata_default"
    user_preferences: Dict[str, Any] = field(default_factory=dict)

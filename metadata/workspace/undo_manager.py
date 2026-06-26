# metadata/workspace/undo_manager.py
import logging
from typing import List, Dict, Optional

from metadata.workspace.metadata_snapshot import MetadataSnapshot

logger = logging.getLogger(__name__)

class UndoManager:
    def __init__(self, max_history: int = 50):
        self.max_history = max_history
        self._undo_stacks: Dict[str, List[MetadataSnapshot]] = {}
        self._redo_stacks: Dict[str, List[MetadataSnapshot]] = {}

    def push_state(self, image_hash: str, snapshot: MetadataSnapshot) -> None:
        if image_hash not in self._undo_stacks:
            self._undo_stacks[image_hash] = []
            
        self._undo_stacks[image_hash].append(snapshot)
        if len(self._undo_stacks[image_hash]) > self.max_history:
            self._undo_stacks[image_hash].pop(0)
            
        self._redo_stacks[image_hash] = []
        logger.debug(f"Pushed state to undo stack for {image_hash}")

    def undo(self, image_hash: str, current_state: MetadataSnapshot) -> Optional[MetadataSnapshot]:
        if image_hash not in self._undo_stacks or not self._undo_stacks[image_hash]:
            return None
            
        if image_hash not in self._redo_stacks:
            self._redo_stacks[image_hash] = []
            
        self._redo_stacks[image_hash].append(current_state)
        previous_state = self._undo_stacks[image_hash].pop()
        logger.info(f"Undo performed for {image_hash}")
        
        return previous_state

    def redo(self, image_hash: str, current_state: MetadataSnapshot) -> Optional[MetadataSnapshot]:
        if image_hash not in self._redo_stacks or not self._redo_stacks[image_hash]:
            return None
            
        if image_hash not in self._undo_stacks:
            self._undo_stacks[image_hash] = []
            
        self._undo_stacks[image_hash].append(current_state)
        next_state = self._redo_stacks[image_hash].pop()
        logger.info(f"Redo performed for {image_hash}")
        
        return next_state

    def can_undo(self, image_hash: str) -> bool:
        return bool(self._undo_stacks.get(image_hash))

    def can_redo(self, image_hash: str) -> bool:
        return bool(self._redo_stacks.get(image_hash))
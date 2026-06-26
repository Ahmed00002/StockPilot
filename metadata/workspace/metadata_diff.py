# metadata/workspace/metadata_diff.py
import difflib
import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

from metadata.workspace.metadata_snapshot import MetadataSnapshot

logger = logging.getLogger(__name__)

@dataclass
class DiffResult:
    is_different: bool
    title_diff: List[Tuple[str, str]] 
    desc_diff: List[Tuple[str, str]]
    added_keywords: List[str]
    removed_keywords: List[str]
    shared_keywords: List[str]

class MetadataDiffEngine:
    def __init__(self):
        pass

    def _diff_text(self, text1: str, text2: str) -> List[Tuple[str, str]]:
        words1 = text1.split()
        words2 = text2.split()
        
        diff = []
        matcher = difflib.SequenceMatcher(None, words1, words2)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                diff.append(('equal', ' '.join(words1[i1:i2])))
            elif tag == 'replace':
                diff.append(('delete', ' '.join(words1[i1:i2])))
                diff.append(('insert', ' '.join(words2[j1:j2])))
            elif tag == 'delete':
                diff.append(('delete', ' '.join(words1[i1:i2])))
            elif tag == 'insert':
                diff.append(('insert', ' '.join(words2[j1:j2])))
        return diff

    def compare(self, v1: MetadataSnapshot, v2: MetadataSnapshot) -> DiffResult:
        title_diff = self._diff_text(v1.title, v2.title)
        desc_diff = self._diff_text(v1.description, v2.description)
        
        kws1 = set(v1.keywords)
        kws2 = set(v2.keywords)
        
        added = list(kws2 - kws1)
        removed = list(kws1 - kws2)
        shared = list(kws1.intersection(kws2))
        
        is_different = bool(
            any(op != 'equal' for op, _ in title_diff) or
            any(op != 'equal' for op, _ in desc_diff) or
            added or removed
        )
        
        return DiffResult(
            is_different=is_different,
            title_diff=title_diff,
            desc_diff=desc_diff,
            added_keywords=added,
            removed_keywords=removed,
            shared_keywords=shared
        )
# metadata/review/metadata_consistency.py
import logging
from typing import List, Tuple, Set

from metadata.review.review_models import MetadataPackage

logger = logging.getLogger(__name__)

class ConsistencyChecker:
    def __init__(self):
        pass

    def check(self, package: MetadataPackage) -> List[Tuple[str, str]]:
        issues = []
        
        title_words = set(package.title.lower().split())
        desc_words = set(package.description.lower().split())
        keywords_set = set(k.lower() for k in package.keywords)
        
        important_title_words = {w for w in title_words if len(w) > 4}
        if important_title_words and not important_title_words.intersection(keywords_set):
            issues.append(("consistency_title_kw", "Key title words are missing from keywords."))
            
        if package.subject:
            subject_parts = set(package.subject.lower().split())
            if not subject_parts.intersection(keywords_set):
                issues.append(("consistency_subject", "Main subject is missing from keywords."))
                
        return issues
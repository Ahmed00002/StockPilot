# utils/string_utils.py
import re

class StringUtils:
    """Utility methods for string manipulation and normalization."""

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Removes invalid characters from a string to make it safe for file systems."""
        return re.sub(r'(?u)[^-\w.]', '', filename.strip().replace(' ', '_'))

    @staticmethod
    def truncate(text: str, max_length: int) -> str:
        """Truncates a string to a maximum length, appending an ellipsis."""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."
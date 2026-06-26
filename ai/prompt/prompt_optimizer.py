# ai/prompt/prompt_optimizer.py
import re
import logging

logger = logging.getLogger("PromptOptimizer")

class PromptOptimizer:
    """Cleans and compacts resolved prompt strings to lower token overhead without altering intent."""

    @staticmethod
    def optimize(prompt: str) -> str:
        """
        Removes redundant spacing, normalizes line breaks, and strips whitespace artifacts.
        """
        original_length = len(prompt)
        
        # Normalize carriage returns
        optimized = prompt.replace("\r\n", "\n")
        
        # Remove consecutive blank lines (more than 2 down to 2)
        optimized = re.sub(r'\n{3,}', '\n\n', optimized)
        
        # Remove trailing and leading whitespace from each line
        lines = [line.strip() for line in optimized.split('\n')]
        
        # Rejoin optimized lines
        optimized = '\n'.join(lines).strip()
        
        savings = original_length - len(optimized)
        if savings > 0:
            logger.debug(f"Prompt optimization compacted payload by {savings} characters.")
            
        return optimized
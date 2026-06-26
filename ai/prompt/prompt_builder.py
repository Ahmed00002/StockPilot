# ai/prompt/prompt_builder.py
import logging
from dataclasses import dataclass
from typing import Optional, Dict

from .prompt_template import PromptTemplate
from .context_builder import PromptContext
from .variable_resolver import VariableResolver
from .marketplace_rules import MarketplaceRulesEngine
from .language_rules import LanguageRulesEngine
from .provider_rules import ProviderRulesEngine
from .prompt_optimizer import PromptOptimizer

logger = logging.getLogger("PromptBuilder")

@dataclass
class BuildResult:
    final_prompt: str
    system_prompt: Optional[str]
    optimization_savings_chars: int

class PromptBuilder:
    """Orchestrates the assembly pipeline, injecting business rules and logic into raw templates."""

    @staticmethod
    def build(template: PromptTemplate, context: PromptContext) -> BuildResult:
        logger.debug(f"Building prompt from template: {template.name}")
        
        # 1. Base Variables Resolution
        variables = context.to_dict()
        base_content = VariableResolver.resolve(template.content, variables)
        
        # 2. Append Marketplace Formatting Rules
        marketplace_rules = MarketplaceRulesEngine.get_rules(context.marketplace)
        if marketplace_rules:
            base_content += f"\n\nMarketplace Constraints ({context.marketplace}):\n{marketplace_rules.formatting_instructions}"
            if marketplace_rules.restricted_terms:
                base_content += f"\nNever output these restricted terms: {', '.join(marketplace_rules.restricted_terms)}"
                
        # 3. Construct System Prompt (Language + Provider Adjusments)
        system_directives = []
        
        language_rule = LanguageRulesEngine.get_directive(context.language)
        system_directives.append(language_rule)
        
        provider_adjustment = ProviderRulesEngine.get_adjustment(context.provider_name)
        if provider_adjustment:
            for addition in provider_adjustment.instruction_additions:
                system_directives.append(addition)
                
        system_prompt = " ".join(system_directives) if system_directives else None
        
        # 4. Optimize the final string payload
        pre_optimize_len = len(base_content)
        optimized_content = PromptOptimizer.optimize(base_content)
        savings = pre_optimize_len - len(optimized_content)
        
        return BuildResult(
            final_prompt=optimized_content,
            system_prompt=system_prompt,
            optimization_savings_chars=savings
        )

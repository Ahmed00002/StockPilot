# ai/orchestration/orchestrator.py
import logging
from typing import Optional, Dict, Any, Callable
from concurrent.futures import Future

from ai.models import AIRequest, AIResponse
from ai.request_context import RequestContext

from .provider_selector import ProviderSelector
from .request_executor import RequestExecutor
from .retry_manager import RetryManager
from .failover_manager import FailoverManager
from .token_accountant import TokenAccountant
from .cost_tracker import CostTracker
from .usage_analytics import UsageAnalytics
from .response_dispatcher import ResponseDispatcher
from .orchestration_events import OrchestrationEventPublisher

logger = logging.getLogger("AIOrchestrator")

class AIOrchestrator:
    """
    Central command and control facade for AI request execution.
    Coordinates routing, execution, retries, failovers, and analytics tracking.
    """

    def __init__(
        self,
        provider_selector: ProviderSelector,
        request_executor: RequestExecutor,
        retry_manager: RetryManager,
        failover_manager: FailoverManager,
        token_accountant: TokenAccountant,
        cost_tracker: CostTracker,
        usage_analytics: UsageAnalytics,
        response_dispatcher: ResponseDispatcher,
        event_publisher: OrchestrationEventPublisher
    ):
        self._provider_selector = provider_selector
        self._executor = request_executor
        self._retry_manager = retry_manager
        self._failover_manager = failover_manager
        self._token_accountant = token_accountant
        self._cost_tracker = cost_tracker
        self._usage_analytics = usage_analytics
        self._response_dispatcher = response_dispatcher
        self._events = event_publisher

    def submit_request(
        self, 
        request: AIRequest, 
        context: RequestContext, 
        callback: Optional[Callable[[AIResponse], None]] = None,
        error_callback: Optional[Callable[[Exception], None]] = None
    ) -> Future:
        """
        Submits an AI request to the orchestration pipeline asynchronously.
        """
        logger.info(f"Orchestrator received new request for workspace: {context.workspace}")
        self._events.publish_request_received(request, context)
        
        def _pipeline_task():
            try:
                response = self._execute_pipeline(request, context)
                self._post_process_success(response, context)
                if callback:
                    callback(response)
                self._response_dispatcher.dispatch(response, context)
                return response
            except Exception as e:
                self._post_process_failure(e, context)
                if error_callback:
                    error_callback(e)
                raise e

        return self._executor.submit_task(_pipeline_task)

    def _execute_pipeline(self, request: AIRequest, context: RequestContext) -> AIResponse:
        excluded_providers = set()
        
        while True:
            provider_name = self._provider_selector.select_provider(request, context, excluded_providers)
            if not provider_name:
                raise RuntimeError("Orchestration failed: No available providers to handle the request.")

            self._events.publish_provider_selected(provider_name, request)
            
            try:
                # Attempt execution with localized retries
                response = self._retry_manager.execute_with_retries(
                    provider_name=provider_name,
                    request=request,
                    executor_func=self._executor.execute_direct
                )
                return response
                
            except Exception as e:
                logger.warning(f"Provider {provider_name} failed completely. Evaluating failover. Error: {str(e)}")
                
                if self._failover_manager.should_failover(e, provider_name):
                    excluded_providers.add(provider_name)
                    self._events.publish_failover_triggered(provider_name, e)
                    continue
                else:
                    logger.error(f"Failover criteria not met or exhausted for error: {str(e)}")
                    raise e

    def _post_process_success(self, response: AIResponse, context: RequestContext) -> None:
        self._token_accountant.record_usage(context.workspace, response.provider_name, response.token_usage)
        
        cost = self._cost_tracker.calculate_and_record(
            context.workspace, 
            response.provider_name, 
            response.model_used, 
            response.token_usage
        )
        response.cost_estimate = cost
        
        self._usage_analytics.record_success(
            provider_name=response.provider_name,
            execution_time_ms=response.execution_time_ms,
            cost=cost.amount,
            tokens=response.token_usage.total_tokens
        )
        self._events.publish_request_succeeded(response)

    def _post_process_failure(self, error: Exception, context: RequestContext) -> None:
        self._usage_analytics.record_failure()
        self._events.publish_request_failed(error, context)
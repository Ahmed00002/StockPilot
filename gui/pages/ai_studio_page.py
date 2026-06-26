from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QFrame,
    QLabel, QTextEdit, QListWidget, QListWidgetItem, QPushButton,
    QComboBox, QToolBar, QStatusBar, QSizePolicy
)
from PySide6.QtCore import Signal, QObject, Qt
from PySide6.QtGui import QAction, QFont
from typing import Optional
import logging
from datetime import datetime

# Assuming these are available from the existing project structure
from core.container import Container
from core.interfaces import AIProvider
from core.models import ChatMessage
from core.managers.ai_orchestrator import AIOrchestrator
from core.events.event_bus import EventBus


class AIStudioPage(QWidget):
    """
    Main AI Studio page with all required components.
    """
    # Signals
    prompt_sent = Signal(str, str)  # prompt, response
    model_changed = Signal(str, str)  # provider, model

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Dependency injection
        self.container = Container()
        self.ai_orchestrator: AIOrchestrator = self.container.resolve(AIOrchestrator)
        self.event_bus: EventBus = self.container.resolve(EventBus)
        
        self.logger = logging.getLogger(__name__)
        
        # State variables
        self.current_provider = None
        self.current_model = None
        
        self._setup_ui()
        self._connect_signals()
        self._load_initial_data()
    
    def _setup_ui(self):
        """Set up the user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create toolbar
        self.toolbar = QToolBar("AI Studio Toolbar")
        self.toolbar.setMovable(False)
        self.toolbar.addAction("Run Prompt", self._run_prompt)
        self.toolbar.addAction("Clear History", self._clear_history)
        main_layout.addWidget(self.toolbar)
        
        # Create main splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        
        # Left sidebar - Provider and Model selection
        self.sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(self.sidebar_widget)
        sidebar_layout.setContentsMargins(5, 5, 5, 5)
        
        # Provider selection
        provider_label = QLabel("AI Provider:")
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["Select Provider..."])
        
        # Model selection
        model_label = QLabel("Model:")
        self.model_combo = QComboBox()
        self.model_combo.addItems(["Select Model..."])
        self.model_combo.setEnabled(False)
        
        sidebar_layout.addWidget(provider_label)
        sidebar_layout.addWidget(self.provider_combo)
        sidebar_layout.addWidget(model_label)
        sidebar_layout.addWidget(self.model_combo)
        
        # Add some stretch to push items to top
        sidebar_layout.addStretch()
        
        # Right side - Main content area
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Create top splitter for prompt and response
        top_splitter = QSplitter(Qt.Vertical)
        
        # Prompt editor
        prompt_label = QLabel("Prompt:")
        self.prompt_editor = QTextEdit()
        self.prompt_editor.setFont(QFont("Courier New", 10))
        self.prompt_editor.setMaximumHeight(200)
        
        # Response panel
        response_label = QLabel("Response:")
        self.response_panel = QTextEdit()
        self.response_panel.setFont(QFont("Courier New", 10))
        self.response_panel.setReadOnly(True)
        
        # Add to top splitter
        prompt_container = QWidget()
        prompt_container_layout = QVBoxLayout(prompt_container)
        prompt_container_layout.setContentsMargins(0, 0, 0, 0)
        prompt_container_layout.addWidget(prompt_label)
        prompt_container_layout.addWidget(self.prompt_editor)
        
        response_container = QWidget()
        response_container_layout = QVBoxLayout(response_container)
        response_container_layout.setContentsMargins(0, 0, 0, 0)
        response_container_layout.addWidget(response_label)
        response_container_layout.addWidget(self.response_panel)
        
        top_splitter.addWidget(prompt_container)
        top_splitter.addWidget(response_container)
        top_splitter.setSizes([150, 300])
        
        # Bottom splitter for history and logs
        bottom_splitter = QSplitter(Qt.Horizontal)
        
        # Request history
        history_label = QLabel("Request History:")
        self.history_list = QListWidget()
        
        history_container = QWidget()
        history_container_layout = QVBoxLayout(history_container)
        history_container_layout.setContentsMargins(0, 0, 0, 0)
        history_container_layout.addWidget(history_label)
        history_container_layout.addWidget(self.history_list)
        
        # Logs panel
        logs_label = QLabel("Logs:")
        self.logs_panel = QTextEdit()
        self.logs_panel.setFont(QFont("Courier New", 9))
        self.logs_panel.setMaximumWidth(300)
        self.logs_panel.setReadOnly(True)
        
        logs_container = QWidget()
        logs_container_layout = QVBoxLayout(logs_container)
        logs_container_layout.setContentsMargins(0, 0, 0, 0)
        logs_container_layout.addWidget(logs_label)
        logs_container_layout.addWidget(self.logs_panel)
        
        bottom_splitter.addWidget(history_container)
        bottom_splitter.addWidget(logs_container)
        bottom_splitter.setSizes([400, 300])
        
        # Add top and bottom to right layout
        right_layout.addWidget(top_splitter)
        right_layout.addWidget(bottom_splitter)
        right_layout.setStretch(0, 2)
        right_layout.setStretch(1, 1)
        
        # Add to main splitter
        self.main_splitter.addWidget(self.sidebar_widget)
        self.main_splitter.addWidget(right_widget)
        self.main_splitter.setSizes([200, 800])
        
        main_layout.addWidget(self.main_splitter)
        
        # Status bar area at bottom
        self.status_frame = QFrame()
        self.status_frame.setFrameShape(QFrame.HLine)
        self.status_frame.setLineWidth(1)
        
        status_layout = QHBoxLayout(self.status_frame)
        status_layout.setContentsMargins(5, 2, 5, 2)
        
        # Token usage
        self.token_usage_label = QLabel("Tokens: Input: 0, Output: 0")
        self.token_usage_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        # Cost panel
        self.cost_label = QLabel("Cost: $0.00")
        self.cost_label.setAlignment(Qt.AlignRight)
        
        status_layout.addWidget(self.token_usage_label)
        status_layout.addWidget(self.cost_label)
        
        main_layout.addWidget(self.status_frame)
    
    def _connect_signals(self):
        """Connect internal signals."""
        self.provider_combo.currentTextChanged.connect(self._on_provider_changed)
        self.model_combo.currentTextChanged.connect(self._on_model_changed)
        self.history_list.itemClicked.connect(self._on_history_item_clicked)
    
    def _load_initial_data(self):
        """Load initial data like providers and models."""
        try:
            providers = self.ai_orchestrator.get_available_providers()
            self.provider_combo.clear()
            self.provider_combo.addItem("Select Provider...")
            self.provider_combo.addItems(providers)
        except Exception as e:
            self.logger.error(f"Error loading providers: {e}")
            self.logs_panel.append(f"[{datetime.now().strftime('%H:%M:%S')}] Error loading providers: {e}")
    
    def _on_provider_changed(self, provider_name: str):
        """Handle provider selection change."""
        if provider_name == "Select Provider...":
            self.current_provider = None
            self.model_combo.clear()
            self.model_combo.addItem("Select Model...")
            self.model_combo.setEnabled(False)
            return
        
        self.current_provider = provider_name
        self.model_combo.setEnabled(True)
        
        try:
            models = self.ai_orchestrator.get_available_models(provider_name)
            self.model_combo.clear()
            self.model_combo.addItem("Select Model...")
            self.model_combo.addItems(models)
        except Exception as e:
            self.logger.error(f"Error loading models for {provider_name}: {e}")
            self.logs_panel.append(f"[{datetime.now().strftime('%H:%M:%S')}] Error loading models for {provider_name}: {e}")
    
    def _on_model_changed(self, model_name: str):
        """Handle model selection change."""
        if model_name == "Select Model...":
            self.current_model = None
            return
        
        self.current_model = model_name
        self.model_changed.emit(self.current_provider, model_name)
    
    def _run_prompt(self):
        """Execute the current prompt."""
        if not self.current_provider or not self.current_model:
            self.logs_panel.append(f"[{datetime.now().strftime('%H:%M:%S')}] Please select both provider and model")
            return
        
        prompt_text = self.prompt_editor.toPlainText().strip()
        if not prompt_text:
            self.logs_panel.append(f"[{datetime.now().strftime('%H:%M:%S')}] Empty prompt")
            return
        
        try:
            # Show processing status
            self.logs_panel.append(f"[{datetime.now().strftime('%H:%M:%S')}] Sending request to {self.current_provider} ({self.current_model})...")
            
            # Create message object
            message = ChatMessage(role="user", content=prompt_text)
            
            # Send to orchestrator
            response = self.ai_orchestrator.send_message(
                messages=[message],
                provider=self.current_provider,
                model=self.current_model
            )
            
            # Update UI with response
            self.response_panel.setPlainText(response.content)
            
            # Update history
            history_item = QListWidgetItem(f"{self.current_provider}/{self.current_model}: {prompt_text[:50]}...")
            history_item.setData(Qt.UserRole, {"prompt": prompt_text, "response": response.content})
            self.history_list.insertItem(0, history_item)
            
            # Update tokens and cost
            self._update_token_usage(response.input_tokens, response.output_tokens)
            self._update_cost(response.input_tokens, response.output_tokens)
            
            # Emit signal
            self.prompt_sent.emit(prompt_text, response.content)
            
            self.logs_panel.append(f"[{datetime.now().strftime('%H:%M:%S')}] Request completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error running prompt: {e}")
            self.logs_panel.append(f"[{datetime.now().strftime('%H:%M:%S')}] Error: {e}")
            self.response_panel.setPlainText(f"Error: {e}")
    
    def _update_token_usage(self, input_tokens: int, output_tokens: int):
        """Update the token usage display."""
        self.token_usage_label.setText(f"Tokens: Input: {input_tokens}, Output: {output_tokens}")
    
    def _update_cost(self, input_tokens: int, output_tokens: int):
        """Calculate and update the cost display."""
        try:
            # Get pricing info from orchestrator
            pricing_info = self.ai_orchestrator.get_pricing_for_model(self.current_provider, self.current_model)
            
            if pricing_info:
                input_cost = (input_tokens / 1000) * pricing_info.get('input_price_per_1k', 0)
                output_cost = (output_tokens / 1000) * pricing_info.get('output_price_per_1k', 0)
                total_cost = input_cost + output_cost
                
                self.cost_label.setText(f"Cost: ${total_cost:.4f}")
            else:
                self.cost_label.setText("Cost: N/A")
        except Exception as e:
            self.logger.warning(f"Could not calculate cost: {e}")
            self.cost_label.setText("Cost: Error")
    
    def _on_history_item_clicked(self, item: QListWidgetItem):
        """Restore prompt when history item is clicked."""
        data = item.data(Qt.UserRole)
        if data and 'prompt' in data:
            self.prompt_editor.setPlainText(data['prompt'])
            if 'response' in data:
                self.response_panel.setPlainText(data['response'])
    
    def _clear_history(self):
        """Clear the request history."""
        self.history_list.clear()
        self.logs_panel.append(f"[{datetime.now().strftime('%H:%M:%S')}] History cleared")
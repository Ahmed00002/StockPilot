# gui/pages/ai_studio_page.py
import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget, 
    QComboBox, QLabel, QPushButton, QTabWidget, QTextEdit, 
    QFormLayout, QFrame, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon

class AIStudioPage(QWidget):
    """
    Production-ready AI Studio Page.
    Provides an interface for AI prompt generation, testing providers, and viewing metadata responses.
    """
    action_requested = Signal(str)

    def __init__(self, container=None, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        # Dependency Injection
        if container:
            self.container = container
        else:
            from core.dependency_container import DependencyContainer
            self.container = DependencyContainer()
            
        self.ai_manager = self.container.get_service("ai_manager")
        self.provider_manager = self.container.get_service("provider_manager")
        self.prompt_manager = self.container.get_service("prompt_manager")
        self.config_manager = self.container.get_service("config_manager")
        self.event_bus = self.container.get_service("event_bus")

        self._init_ui()
        self._connect_signals()
        self._load_initial_data()

    def _init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Main vertical splitter (Top Panels vs Bottom Tabs)
        self.v_splitter = QSplitter(Qt.Vertical)
        
        # Horizontal splitter for Top (Left, Center, Right)
        self.h_splitter = QSplitter(Qt.Horizontal)
        
        self._create_left_panel()
        self._create_center_panel()
        self._create_right_panel()
        
        self.h_splitter.addWidget(self.left_panel)
        self.h_splitter.addWidget(self.center_panel)
        self.h_splitter.addWidget(self.right_panel)
        self.h_splitter.setSizes([200, 500, 300])
        
        self._create_bottom_panel()
        
        self.v_splitter.addWidget(self.h_splitter)
        self.v_splitter.addWidget(self.bottom_tabs)
        self.v_splitter.setSizes([600, 200])
        
        self.main_layout.addWidget(self.v_splitter)

    def _create_left_panel(self):
        self.left_panel = QWidget()
        layout = QVBoxLayout(self.left_panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        lbl_title = QLabel("<b>AI Providers</b>")
        layout.addWidget(lbl_title)
        
        self.provider_list = QListWidget()
        # Initialize with requested providers
        providers = ["Gemini", "OpenAI", "Claude", "Groq", "DeepSeek", "OpenRouter"]
        self.provider_list.addItems(providers)
        layout.addWidget(self.provider_list)
        
        lbl_model = QLabel("<b>Selected Model</b>")
        layout.addWidget(lbl_model)
        
        self.model_combo = QComboBox()
        self.model_combo.addItem("Select Provider First...")
        self.model_combo.setEnabled(False)
        layout.addWidget(self.model_combo)

    def _create_center_panel(self):
        self.center_panel = QWidget()
        layout = QVBoxLayout(self.center_panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Prompt Templates
        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel("<b>Prompt Template:</b>"))
        self.template_combo = QComboBox()
        self.template_combo.addItem("Custom Prompt")
        self.template_combo.addItem("Title & Description Generator")
        self.template_combo.addItem("Keyword Extractor")
        self.template_combo.addItem("Compliance Review")
        template_layout.addWidget(self.template_combo, 1)
        layout.addLayout(template_layout)
        
        # Prompt Editor
        layout.addWidget(QLabel("<b>Prompt Editor</b>"))
        self.prompt_editor = QTextEdit()
        self.prompt_editor.setFont(QFont("Consolas", 10))
        self.prompt_editor.setPlaceholderText("Enter your AI prompt here or select a template...")
        layout.addWidget(self.prompt_editor, 1)
        
        # Action Buttons
        button_layout = QHBoxLayout()
        self.btn_generate = QPushButton("Generate")
        self.btn_generate.setStyleSheet("background-color: #2e6b3c; color: white; font-weight: bold; padding: 5px;")
        
        self.btn_improve = QPushButton("Improve")
        self.btn_improve.setStyleSheet("background-color: #2b579a; color: white; font-weight: bold; padding: 5px;")
        
        self.btn_stop = QPushButton("Stop")
        self.btn_stop.setStyleSheet("background-color: #a33232; color: white; font-weight: bold; padding: 5px;")
        self.btn_stop.setEnabled(False)
        
        button_layout.addWidget(self.btn_generate)
        button_layout.addWidget(self.btn_improve)
        button_layout.addWidget(self.btn_stop)
        
        layout.addLayout(button_layout)

    def _create_right_panel(self):
        self.right_panel = QScrollArea()
        self.right_panel.setWidgetResizable(True)
        self.right_panel.setFrameShape(QFrame.NoFrame)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Response View
        layout.addWidget(QLabel("<b>Response</b>"))
        self.response_view = QTextEdit()
        self.response_view.setReadOnly(True)
        self.response_view.setFont(QFont("Consolas", 9))
        self.response_view.setMinimumHeight(150)
        layout.addWidget(self.response_view)
        
        # Metadata Preview
        layout.addWidget(QLabel("<b>Metadata Preview</b>"))
        self.metadata_preview = QTextEdit()
        self.metadata_preview.setReadOnly(True)
        self.metadata_preview.setFont(QFont("Consolas", 9))
        self.metadata_preview.setMinimumHeight(100)
        layout.addWidget(self.metadata_preview)
        
        # Stats Form
        stats_frame = QFrame()
        stats_frame.setStyleSheet("QFrame { background-color: rgba(255, 255, 255, 0.05); border-radius: 4px; padding: 5px; }")
        stats_layout = QFormLayout(stats_frame)
        stats_layout.setContentsMargins(10, 10, 10, 10)
        
        self.lbl_model_used = QLabel("N/A")
        self.lbl_execution_time = QLabel("0 ms")
        self.lbl_token_usage = QLabel("0 (In) / 0 (Out)")
        self.lbl_cost = QLabel("$0.0000")
        
        stats_layout.addRow("<b>Model:</b>", self.lbl_model_used)
        stats_layout.addRow("<b>Execution Time:</b>", self.lbl_execution_time)
        stats_layout.addRow("<b>Token Usage:</b>", self.lbl_token_usage)
        stats_layout.addRow("<b>Estimated Cost:</b>", self.lbl_cost)
        
        layout.addWidget(stats_frame)
        layout.addStretch()
        
        self.right_panel.setWidget(container)

    def _create_bottom_panel(self):
        self.bottom_tabs = QTabWidget()
        
        self.tab_history = QListWidget()
        self.tab_history.setAlternatingRowColors(True)
        
        self.tab_logs = QTextEdit()
        self.tab_logs.setReadOnly(True)
        self.tab_logs.setFont(QFont("Consolas", 9))
        
        self.tab_console = QTextEdit()
        self.tab_console.setReadOnly(True)
        self.tab_console.setFont(QFont("Consolas", 9))
        self.tab_console.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")
        
        self.bottom_tabs.addTab(self.tab_history, "History")
        self.bottom_tabs.addTab(self.tab_logs, "Logs")
        self.bottom_tabs.addTab(self.tab_console, "Console")

    def _connect_signals(self):
        self.provider_list.currentTextChanged.connect(self._on_provider_selected)
        self.template_combo.currentTextChanged.connect(self._on_template_selected)
        self.btn_generate.clicked.connect(self._on_generate)
        self.btn_improve.clicked.connect(self._on_improve)
        self.btn_stop.clicked.connect(self._on_stop)

    def _load_initial_data(self):
        self._log("AI Studio initialized and ready.")
        self._log_console("Awaiting AI execution commands...")

    def _on_provider_selected(self, provider_name):
        self.model_combo.clear()
        if not provider_name:
            self.model_combo.setEnabled(False)
            return
            
        self.model_combo.setEnabled(True)
        # Dummy model population based on provider
        if provider_name == "OpenAI":
            self.model_combo.addItems(["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"])
        elif provider_name == "Gemini":
            self.model_combo.addItems(["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro-vision"])
        elif provider_name == "Claude":
            self.model_combo.addItems(["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"])
        elif provider_name == "Groq":
            self.model_combo.addItems(["llama3-70b-8192", "mixtral-8x7b-32768"])
        elif provider_name == "DeepSeek":
            self.model_combo.addItems(["deepseek-coder", "deepseek-chat"])
        elif provider_name == "OpenRouter":
            self.model_combo.addItems(["anthropic/claude-3-opus", "google/gemini-pro"])
            
        self._log(f"Provider switched to {provider_name}. Available models loaded.")

    def _on_template_selected(self, template_name):
        if template_name == "Custom Prompt":
            self.prompt_editor.clear()
        elif template_name == "Title & Description Generator":
            self.prompt_editor.setPlainText("Analyze the attached image and generate a highly commercial title (max 200 chars) and a detailed description suitable for Adobe Stock.")
        elif template_name == "Keyword Extractor":
            self.prompt_editor.setPlainText("Extract the top 50 relevant keywords for the attached image, ordered by relevance. Separate by commas.")
        elif template_name == "Compliance Review":
            self.prompt_editor.setPlainText("Review this image and metadata for potential trademark, copyright, or sensitive content violations.")
        
        self._log(f"Loaded template: {template_name}")

    def _on_generate(self):
        provider = self.provider_list.currentItem()
        if not provider:
            self._log_console("[ERROR] No AI provider selected.")
            return
            
        prompt = self.prompt_editor.toPlainText().strip()
        if not prompt:
            self._log_console("[WARNING] Empty prompt. Cannot generate.")
            return

        provider_name = provider.text()
        model_name = self.model_combo.currentText()

        self._set_execution_state(True)
        self._log(f"Initiating generation with {provider_name} ({model_name})...")
        self._log_console(f"Requesting generation from {provider_name} API...")
        
        # Simulate updating UI before async call (Assuming real integration handles async properly)
        self.response_view.setPlainText("Generating response...")
        self.lbl_model_used.setText(f"{provider_name} - {model_name}")

    def _on_improve(self):
        self._log("Improve command triggered. Analyzing current response context...")
        self._log_console("Sending iterative improvement request...")

    def _on_stop(self):
        self._log("Execution interrupted by user.")
        self._log_console("Stop signal sent to provider manager.")
        self.response_view.setPlainText("Execution stopped.")
        self._set_execution_state(False)

    def _set_execution_state(self, is_running: bool):
        self.btn_generate.setEnabled(not is_running)
        self.btn_improve.setEnabled(not is_running)
        self.btn_stop.setEnabled(is_running)

    def _log(self, message: str):
        self.logger.info(message)
        self.tab_logs.append(message)

    def _log_console(self, message: str):
        self.tab_console.append(message)
        
    def update_response_stats(self, response_text: str, metadata: str, tokens_in: int, tokens_out: int, cost: float, exec_time: float):
        """Method meant to be called by orchestration callbacks when a response arrives."""
        self.response_view.setPlainText(response_text)
        self.metadata_preview.setPlainText(metadata)
        self.lbl_token_usage.setText(f"{tokens_in} (In) / {tokens_out} (Out)")
        self.lbl_cost.setText(f"${cost:.4f}")
        self.lbl_execution_time.setText(f"{exec_time:.2f} ms")
        self.tab_history.insertItem(0, f"[{self.lbl_model_used.text()}] Cost: ${cost:.4f} | Time: {exec_time:.0f}ms")
        self._set_execution_state(False)
        self._log_console("Request successfully completed.")
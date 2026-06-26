# gui/ai/gemini_settings_widget.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QLineEdit, QComboBox, QPushButton, QSpinBox, 
    QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt, Signal
import logging

from ai.providers.gemini_config import GeminiConfig
from ai.providers.gemini_provider import GeminiProvider

logger = logging.getLogger("GeminiSettingsWidget")

class GeminiSettingsWidget(QWidget):
    """UI Widget for configuring the Google Gemini AI Provider."""
    
    settings_saved = Signal(GeminiConfig)

    def __init__(self, current_config: GeminiConfig = None, parent=None):
        super().__init__(parent)
        self.config = current_config or GeminiConfig()
        self._setup_ui()
        self._load_config()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignTop)

        # Provider Status Group
        status_group = QGroupBox("Provider Status")
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Status: Unchecked")
        self.btn_test_conn = QPushButton("Test Connection")
        self.btn_test_conn.clicked.connect(self._on_test_connection)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.btn_test_conn)
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)

        # Configuration Group
        config_group = QGroupBox("Gemini Configuration")
        form_layout = QFormLayout()

        self.input_api_key = QLineEdit()
        self.input_api_key.setEchoMode(QLineEdit.Password)
        self.input_api_key.setPlaceholderText("Enter Google Gemini API Key")
        
        self.combo_text_model = QComboBox()
        self.combo_vision_model = QComboBox()
        self.combo_text_model.addItems(self.config.supported_models)
        self.combo_vision_model.addItems(self.config.supported_models)

        self.spin_timeout = QSpinBox()
        self.spin_timeout.setRange(5, 120)
        self.spin_timeout.setSuffix(" sec")
        
        self.spin_retries = QSpinBox()
        self.spin_retries.setRange(0, 5)

        form_layout.addRow("API Key:", self.input_api_key)
        form_layout.addRow("Default Text Model:", self.combo_text_model)
        form_layout.addRow("Default Vision Model:", self.combo_vision_model)
        form_layout.addRow("Timeout:", self.spin_timeout)
        form_layout.addRow("Max Retries:", self.spin_retries)

        config_group.setLayout(form_layout)
        main_layout.addWidget(config_group)

        # Action Buttons
        btn_layout = QHBoxLayout()
        self.btn_reset = QPushButton("Reset")
        self.btn_save = QPushButton("Save Settings")
        
        self.btn_reset.clicked.connect(self._load_config)
        self.btn_save.clicked.connect(self._on_save)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_reset)
        btn_layout.addWidget(self.btn_save)
        
        main_layout.addLayout(btn_layout)

    def _load_config(self):
        """Populates UI fields from the current configuration."""
        self.input_api_key.setText(self.config.api_key)
        self.combo_text_model.setCurrentText(self.config.default_text_model)
        self.combo_vision_model.setCurrentText(self.config.default_vision_model)
        self.spin_timeout.setValue(self.config.timeout_seconds)
        self.spin_retries.setValue(self.config.max_retries)
        self.status_label.setText("Status: Unchecked")

    def _build_config_from_ui(self) -> GeminiConfig:
        """Constructs a new config object based on UI input."""
        config = GeminiConfig()
        config.api_key = self.input_api_key.text().strip()
        config.default_text_model = self.combo_text_model.currentText()
        config.default_vision_model = self.combo_vision_model.currentText()
        config.timeout_seconds = self.spin_timeout.value()
        config.max_retries = self.spin_retries.value()
        return config

    def _on_test_connection(self):
        self.status_label.setText("Status: Testing...")
        self.btn_test_conn.setEnabled(False)
        
        temp_config = self._build_config_from_ui()
        provider = GeminiProvider(temp_config)
        
        try:
            health = provider.health_check()
            if health.is_healthy:
                self.status_label.setText(f"Status: Connected ({health.latency_ms:.0f}ms)")
                self.status_label.setStyleSheet("color: green;")
                QMessageBox.information(self, "Success", "Successfully connected to Gemini API.")
            else:
                self._handle_conn_error(health.error_message)
        except Exception as e:
            self._handle_conn_error(str(e))
        finally:
            self.btn_test_conn.setEnabled(True)

    def _handle_conn_error(self, message: str):
        self.status_label.setText("Status: Connection Failed")
        self.status_label.setStyleSheet("color: red;")
        QMessageBox.critical(self, "Connection Error", f"Failed to connect to Gemini API:\n\n{message}")
        logger.error(f"Gemini connection test failed: {message}")

    def _on_save(self):
        self.config = self._build_config_from_ui()
        self.settings_saved.emit(self.config)
        logger.info("Gemini provider settings saved.")
        QMessageBox.information(self, "Saved", "Gemini settings have been saved successfully.")
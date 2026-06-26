# gui/ai/groq_settings_widget.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QLineEdit, QComboBox, QPushButton, QSpinBox, 
    QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt, Signal
import logging

from ai.providers.groq_config import GroqConfig
from ai.providers.groq_provider import GroqProvider

logger = logging.getLogger("GroqSettingsWidget")

class GroqSettingsWidget(QWidget):
    """Integrated dashboard UI and operations panel configuration component for the Groq infrastructure."""
    
    settings_saved = Signal(GroqConfig)

    def __init__(self, current_config: GroqConfig = None, parent=None):
        super().__init__(parent)
        self.config = current_config or GroqConfig()
        self._setup_ui_components()
        self._hydrate_fields()

    def _setup_ui_components(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # Status and Health Component Panel
        status_box = QGroupBox("Engine Connectivity Context")
        status_layout = QHBoxLayout()
        self.lbl_status = QLabel("State Monitor: Awaiting Verification")
        self.btn_verify = QPushButton("Test API Link")
        self.btn_verify.clicked.connect(self._perform_link_test)
        
        status_layout.addWidget(self.lbl_status)
        status_layout.addStretch()
        status_layout.addWidget(self.btn_verify)
        status_box.setLayout(status_layout)
        layout.addWidget(status_box)

        # Core Parameter Fields
        settings_box = QGroupBox("Configuration Options")
        form = QFormLayout()

        self.txt_api_key = QLineEdit()
        self.txt_api_key.setEchoMode(QLineEdit.Password)
        self.txt_api_key.setPlaceholderText("Paste secret Groq API token (gsk_...)")

        self.cb_text_model = QComboBox()
        self.cb_vision_model = QComboBox()
        self.cb_text_model.addItems(self.config.supported_models)
        self.cb_vision_model.addItems(self.config.supported_models)

        self.sb_timeout = QSpinBox()
        self.sb_timeout.setRange(5, 180)
        self.sb_timeout.setSuffix(" seconds")

        self.sb_retries = QSpinBox()
        self.sb_retries.setRange(0, 10)

        form.addRow("API Secret Key:", self.txt_api_key)
        form.addRow("Standard Text Core:", self.cb_text_model)
        form.addRow("Vision Array Target:", self.cb_vision_model)
        form.addRow("Connection Timeout:", self.sb_timeout)
        form.addRow("Max Retry Attempts:", self.sb_retries)

        settings_box.setLayout(form)
        layout.addWidget(settings_box)

        # Commit Bar
        actions_layout = QHBoxLayout()
        self.btn_rollback = QPushButton("Discard Changes")
        self.btn_commit = QPushButton("Apply Configuration")

        self.btn_rollback.clicked.connect(self._hydrate_fields)
        self.btn_commit.clicked.connect(self._save_ui_state)

        actions_layout.addStretch()
        actions_layout.addWidget(self.btn_rollback)
        actions_layout.addWidget(self.btn_commit)
        layout.addLayout(actions_layout)

    def _hydrate_fields(self):
        """Pulls internal config parameter state into visible input controls."""
        self.txt_api_key.setText(self.config.api_key)
        self.cb_text_model.setCurrentText(self.config.default_text_model)
        self.cb_vision_model.setCurrentText(self.config.default_vision_model)
        self.sb_timeout.setValue(self.config.timeout_seconds)
        self.sb_retries.setValue(self.config.max_retries)
        self.lbl_status.setText("State Monitor: Unverified")
        self.lbl_status.setStyleSheet("")

    def _extract_config_state(self) -> GroqConfig:
        """Harvests variable structures from active UI entry values to compile an operational config object."""
        extracted = GroqConfig()
        extracted.api_key = self.txt_api_key.text().strip()
        extracted.default_text_model = self.cb_text_model.currentText()
        extracted.default_vision_model = self.cb_vision_model.currentText()
        extracted.timeout_seconds = self.sb_timeout.value()
        extracted.max_retries = self.sb_retries.value()
        return extracted

    def _perform_link_test(self):
        self.lbl_status.setText("State Monitor: Probing Target Interface...")
        self.btn_verify.setEnabled(False)
        
        provisional_config = self._extract_config_state()
        tester_provider = GroqProvider(provisional_config)
        
        try:
            health = tester_provider.health_check()
            if health.is_healthy:
                self.lbl_status.setText(f"State Monitor: Online Response Confirmed ({health.latency_ms:.0f}ms)")
                self.lbl_status.setStyleSheet("color: #2ecc71; font-weight: bold;")
                QMessageBox.information(self, "Link Test Success", "Secure handshaking established with Groq cloud servers.")
            else:
                self._render_failed_test(health.error_message or "API validation failure.")
        except Exception as e:
            self._render_failed_test(str(e))
        finally:
            self.btn_verify.setEnabled(True)

    def _render_failed_test(self, explanation: str):
        self.lbl_status.setText("State Monitor: Remote Access Denied")
        self.lbl_status.setStyleSheet("color: #e74c3c; font-weight: bold;")
        QMessageBox.critical(self, "Interface Access Deficit", f"The connection sequence could not be completed:\n\n{explanation}")
        logger.error(f"Groq infrastructure connection attempt failed: {explanation}")

    def _save_ui_state(self):
        self.config = self._extract_config_state()
        self.settings_saved.emit(self.config)
        logger.info("Groq configuration state locked and broadcasted.")
        QMessageBox.information(self, "Success", "Groq provider parameters committed to application environment storage.")
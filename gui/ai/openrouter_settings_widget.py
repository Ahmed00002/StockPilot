# gui/ai/openrouter_settings_widget.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QSpinBox,
    QMessageBox, QGroupBox, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Signal
import logging

from ai.providers.openrouter_config import OpenRouterConfig

logger = logging.getLogger("OpenRouterSettingsWidget")


def _get_provider(config):
    from ai.providers.openrouter_provider import OpenRouterProvider
    return OpenRouterProvider(config)


class OpenRouterSettingsWidget(QWidget):
    """Configuration panel for the OpenRouter AI Gateway."""

    settings_saved = Signal(OpenRouterConfig)

    def __init__(self, current_config: OpenRouterConfig = None, parent=None):
        super().__init__(parent)
        self.config = current_config or OpenRouterConfig()
        self._setup_ui()
        self._hydrate_fields()

    def _setup_ui(self):
        outer = QWidget()
        layout = QVBoxLayout(outer)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        status_box = QGroupBox("Connection Status")
        sl = QHBoxLayout(status_box)
        self.lbl_status = QLabel("● Not verified")
        self.lbl_status.setStyleSheet("color: #858585;")
        self.btn_test = QPushButton("Test Connection")
        self.btn_test.setFixedWidth(140)
        self.btn_test.clicked.connect(self._test_connection)
        sl.addWidget(self.lbl_status)
        sl.addStretch()
        sl.addWidget(self.btn_test)
        layout.addWidget(status_box)

        self.lbl_install_hint = QLabel(
            "⚠  SDK not installed — run:  <b>pip install openai</b>  (OpenRouter uses the OpenAI SDK)<br>"
            "The settings form below can still be filled and saved."
        )
        self.lbl_install_hint.setTextFormat(Qt.TextFormat.RichText)
        self.lbl_install_hint.setWordWrap(True)
        self.lbl_install_hint.setStyleSheet(
            "color: #d4a017; background: #332b00; border: 1px solid #665500;"
            "border-radius: 4px; padding: 8px;"
        )
        self.lbl_install_hint.setVisible(not self._sdk_available())
        layout.addWidget(self.lbl_install_hint)

        config_box = QGroupBox("OpenRouter Configuration")
        form = QFormLayout(config_box)
        form.setContentsMargins(12, 16, 12, 12)
        form.setSpacing(10)

        self.txt_api_key = QLineEdit()
        self.txt_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_api_key.setPlaceholderText("sk-or-...")

        self.cb_default_model = QComboBox()
        self.cb_fallback_model = QComboBox()
        self.cb_default_model.addItems(self.config.pinned_models)
        self.cb_fallback_model.addItems(self.config.pinned_models)

        self.sb_timeout = QSpinBox()
        self.sb_timeout.setRange(5, 180)
        self.sb_timeout.setSuffix(" seconds")

        self.sb_retries = QSpinBox()
        self.sb_retries.setRange(0, 10)

        self.cb_routing = QComboBox()
        self.cb_routing.addItems(["manual", "cheapest", "fastest", "highest_context"])

        form.addRow("API Key:", self.txt_api_key)
        form.addRow("Default Model:", self.cb_default_model)
        form.addRow("Fallback Model:", self.cb_fallback_model)
        form.addRow("Timeout:", self.sb_timeout)
        form.addRow("Max Retries:", self.sb_retries)
        form.addRow("Routing Preference:", self.cb_routing)
        layout.addWidget(config_box)

        btn_row = QHBoxLayout()
        self.btn_discard = QPushButton("Discard Changes")
        self.btn_save = QPushButton("Save Configuration")
        self.btn_save.setStyleSheet("background: #007acc; color: white; font-weight: bold; padding: 5px 16px;")
        self.btn_discard.clicked.connect(self._hydrate_fields)
        self.btn_save.clicked.connect(self._save)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_discard)
        btn_row.addWidget(self.btn_save)
        layout.addLayout(btn_row)
        layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(outer)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(scroll)

    def _sdk_available(self) -> bool:
        try:
            import openai  # noqa: F401
            return True
        except ImportError:
            return False

    def _hydrate_fields(self):
        self.txt_api_key.setText(self.config.api_key)
        self.cb_default_model.setCurrentText(self.config.default_model)
        self.cb_fallback_model.setCurrentText(self.config.fallback_model)
        self.sb_timeout.setValue(self.config.timeout_seconds)
        self.sb_retries.setValue(self.config.max_retries)
        self.cb_routing.setCurrentText(self.config.routing_preference)
        self.lbl_status.setText("● Not verified")
        self.lbl_status.setStyleSheet("color: #858585;")

    def _build_config(self) -> OpenRouterConfig:
        c = OpenRouterConfig()
        c.api_key = self.txt_api_key.text().strip()
        c.default_model = self.cb_default_model.currentText()
        c.fallback_model = self.cb_fallback_model.currentText()
        c.timeout_seconds = self.sb_timeout.value()
        c.max_retries = self.sb_retries.value()
        c.routing_preference = self.cb_routing.currentText()
        return c

    def _test_connection(self):
        if not self._sdk_available():
            QMessageBox.warning(self, "SDK Missing",
                                "The 'openai' package is not installed.\n\nRun:  pip install openai")
            return
        self.lbl_status.setText("● Testing…")
        self.lbl_status.setStyleSheet("color: #cccccc;")
        self.btn_test.setEnabled(False)
        try:
            provider = _get_provider(self._build_config())
            health = provider.health_check()
            if health.is_healthy:
                self.lbl_status.setText(f"● Connected  ({health.latency_ms:.0f} ms)")
                self.lbl_status.setStyleSheet("color: #3fb950; font-weight: bold;")
                QMessageBox.information(self, "Success", "OpenRouter connection verified successfully.")
            else:
                self._show_error(health.error_message or "Validation failed.")
        except Exception as e:
            self._show_error(str(e))
        finally:
            self.btn_test.setEnabled(True)

    def _show_error(self, msg: str):
        self.lbl_status.setText("● Connection failed")
        self.lbl_status.setStyleSheet("color: #f48771; font-weight: bold;")
        QMessageBox.critical(self, "Connection Error", msg)

    def _save(self):
        self.config = self._build_config()
        self.settings_saved.emit(self.config)
        QMessageBox.information(self, "Saved", "OpenRouter settings saved successfully.")

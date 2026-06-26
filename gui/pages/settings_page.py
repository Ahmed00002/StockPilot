# gui/pages/settings_page.py
"""
Production-ready Settings Page for StockPilot AI.
Implements all settings sections with full DI wiring, signal connections,
and integration with existing SettingsManager / ThemeManager / ConfigManager.
"""

import json
import logging
import shutil
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget,
    QListWidgetItem, QStackedWidget, QLabel, QPushButton, QLineEdit,
    QComboBox, QCheckBox, QSpinBox, QDoubleSpinBox, QGroupBox,
    QFormLayout, QTextEdit, QScrollArea, QFrame, QFileDialog,
    QMessageBox, QSlider, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QSizePolicy, QToolBar, QStatusBar, QProgressBar,
    QAbstractItemView
)
from PySide6.QtCore import Qt, Signal, QSize, QTimer
from PySide6.QtGui import QFont, QIcon, QColor

from core.constants import AppConstants

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _section_title(text: str) -> QLabel:
    lbl = QLabel(text)
    font = QFont()
    font.setPointSize(13)
    font.setBold(True)
    lbl.setFont(font)
    lbl.setStyleSheet("color: #007acc; padding-bottom: 4px;")
    return lbl


def _divider() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFrameShadow(QFrame.Shadow.Sunken)
    line.setStyleSheet("color: #3f3f46;")
    return line


def _card(title: str = "") -> QGroupBox:
    box = QGroupBox(title)
    box.setStyleSheet("""
        QGroupBox {
            border: 1px solid #3f3f46;
            border-radius: 6px;
            margin-top: 8px;
            padding-top: 12px;
            background: #2d2d30;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            color: #cccccc;
            font-weight: 600;
        }
    """)
    return box


def _build_scroll(inner: QWidget) -> QScrollArea:
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    scroll.setWidget(inner)
    return scroll


# ─────────────────────────────────────────────────────────────────────────────
# Section panels
# ─────────────────────────────────────────────────────────────────────────────

class GeneralPanel(QWidget):
    """General application preferences."""

    changed = Signal()

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.cfg = config_manager
        self._build()
        self._load()

    def _build(self):
        outer = QWidget()
        layout = QVBoxLayout(outer)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        layout.addWidget(_section_title("General Settings"))
        layout.addWidget(_divider())

        # Startup
        startup_box = _card("Startup Behaviour")
        sf = QFormLayout(startup_box)
        sf.setContentsMargins(16, 20, 16, 16)
        sf.setSpacing(10)
        self.chk_restore_workspace = QCheckBox("Restore last workspace on launch")
        self.chk_show_welcome = QCheckBox("Show Welcome screen on startup")
        self.chk_check_updates = QCheckBox("Check for updates automatically")
        sf.addRow(self.chk_restore_workspace)
        sf.addRow(self.chk_show_welcome)
        sf.addRow(self.chk_check_updates)
        layout.addWidget(startup_box)

        # Performance
        perf_box = _card("Performance")
        pf = QFormLayout(perf_box)
        pf.setContentsMargins(16, 20, 16, 16)
        pf.setSpacing(10)
        self.sb_threads = QSpinBox()
        self.sb_threads.setRange(1, 64)
        self.sb_threads.setSuffix("  threads")
        self.sb_cache_mb = QSpinBox()
        self.sb_cache_mb.setRange(128, 8192)
        self.sb_cache_mb.setSuffix("  MB")
        self.sb_cache_mb.setSingleStep(128)
        self.chk_hw_accel = QCheckBox("Enable hardware acceleration (GPU)")
        pf.addRow("Worker threads:", self.sb_threads)
        pf.addRow("In-memory cache limit:", self.sb_cache_mb)
        pf.addRow(self.chk_hw_accel)
        layout.addWidget(perf_box)

        # Debug
        debug_box = _card("Developer")
        df = QFormLayout(debug_box)
        df.setContentsMargins(16, 20, 16, 16)
        df.setSpacing(10)
        self.chk_debug = QCheckBox("Enable debug mode")
        self.chk_verbose = QCheckBox("Verbose console output")
        df.addRow(self.chk_debug)
        df.addRow(self.chk_verbose)
        layout.addWidget(debug_box)

        layout.addStretch()
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(_build_scroll(outer))

        for w in [self.chk_restore_workspace, self.chk_show_welcome,
                  self.chk_check_updates, self.chk_hw_accel,
                  self.chk_debug, self.chk_verbose]:
            w.stateChanged.connect(lambda _: self.changed.emit())
        for w in [self.sb_threads, self.sb_cache_mb]:
            w.valueChanged.connect(lambda _: self.changed.emit())

    def _load(self):
        if not self.cfg:
            return
        self.chk_restore_workspace.setChecked(self.cfg.get("restore_workspace", True))
        self.chk_show_welcome.setChecked(self.cfg.get("show_welcome", True))
        self.chk_check_updates.setChecked(self.cfg.get("check_updates", True))
        self.sb_threads.setValue(self.cfg.get("max_threads", 8))
        self.sb_cache_mb.setValue(self.cfg.get("cache_mb", 512))
        self.chk_hw_accel.setChecked(self.cfg.get("hw_accel", False))
        self.chk_debug.setChecked(self.cfg.get("debug_mode", False))
        self.chk_verbose.setChecked(self.cfg.get("verbose_logging", False))

    def apply(self):
        if not self.cfg:
            return
        self.cfg.set("restore_workspace", self.chk_restore_workspace.isChecked())
        self.cfg.set("show_welcome", self.chk_show_welcome.isChecked())
        self.cfg.set("check_updates", self.chk_check_updates.isChecked())
        self.cfg.set("max_threads", self.sb_threads.value())
        self.cfg.set("cache_mb", self.sb_cache_mb.value())
        self.cfg.set("hw_accel", self.chk_hw_accel.isChecked())
        self.cfg.set("debug_mode", self.chk_debug.isChecked())
        self.cfg.set("verbose_logging", self.chk_verbose.isChecked())

    def reset(self):
        self.chk_restore_workspace.setChecked(True)
        self.chk_show_welcome.setChecked(True)
        self.chk_check_updates.setChecked(True)
        self.sb_threads.setValue(8)
        self.sb_cache_mb.setValue(512)
        self.chk_hw_accel.setChecked(False)
        self.chk_debug.setChecked(False)
        self.chk_verbose.setChecked(False)


class ThemePanel(QWidget):
    """Theme and appearance settings."""

    changed = Signal()

    THEMES = ["Dark (Default)", "Light", "High Contrast", "Midnight Blue", "Solarized Dark"]
    ACCENT_COLORS = {
        "Blue (#007ACC)": "#007acc",
        "Cyan (#00BFFF)": "#00bfff",
        "Green (#3FB950)": "#3fb950",
        "Orange (#E8890C)": "#e8890c",
        "Purple (#7B68EE)": "#7b68ee",
        "Red (#F85149)": "#f85149",
    }

    def __init__(self, config_manager, theme_manager, parent=None):
        super().__init__(parent)
        self.cfg = config_manager
        self.theme_mgr = theme_manager
        self._build()
        self._load()

    def _build(self):
        outer = QWidget()
        layout = QVBoxLayout(outer)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        layout.addWidget(_section_title("Theme & Appearance"))
        layout.addWidget(_divider())

        # Theme selection
        theme_box = _card("Color Theme")
        tf = QFormLayout(theme_box)
        tf.setContentsMargins(16, 20, 16, 16)
        tf.setSpacing(10)
        self.cb_theme = QComboBox()
        self.cb_theme.addItems(self.THEMES)
        self.cb_accent = QComboBox()
        self.cb_accent.addItems(list(self.ACCENT_COLORS.keys()))
        self.btn_preview = QPushButton("Preview Theme")
        self.btn_preview.setMaximumWidth(140)
        self.btn_preview.clicked.connect(self._preview_theme)
        tf.addRow("Application theme:", self.cb_theme)
        tf.addRow("Accent colour:", self.cb_accent)
        tf.addRow("", self.btn_preview)
        layout.addWidget(theme_box)

        # Typography
        font_box = _card("Typography")
        ff = QFormLayout(font_box)
        ff.setContentsMargins(16, 20, 16, 16)
        ff.setSpacing(10)
        self.sb_ui_font_size = QSpinBox()
        self.sb_ui_font_size.setRange(8, 24)
        self.sb_ui_font_size.setSuffix(" pt")
        self.sb_editor_font_size = QSpinBox()
        self.sb_editor_font_size.setRange(8, 28)
        self.sb_editor_font_size.setSuffix(" pt")
        ff.addRow("UI font size:", self.sb_ui_font_size)
        ff.addRow("Editor font size:", self.sb_editor_font_size)
        layout.addWidget(font_box)

        # Layout
        layout_box = _card("Layout & Density")
        lf = QFormLayout(layout_box)
        lf.setContentsMargins(16, 20, 16, 16)
        lf.setSpacing(10)
        self.cb_density = QComboBox()
        self.cb_density.addItems(["Comfortable", "Compact", "Spacious"])
        self.chk_animations = QCheckBox("Enable UI animations")
        self.chk_tooltips = QCheckBox("Show extended tooltips")
        self.chk_show_breadcrumb = QCheckBox("Show breadcrumb navigation bar")
        lf.addRow("UI density:", self.cb_density)
        lf.addRow(self.chk_animations)
        lf.addRow(self.chk_tooltips)
        lf.addRow(self.chk_show_breadcrumb)
        layout.addWidget(layout_box)

        layout.addStretch()
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(_build_scroll(outer))

        self.cb_theme.currentIndexChanged.connect(lambda _: self.changed.emit())
        self.cb_accent.currentIndexChanged.connect(lambda _: self.changed.emit())
        for w in [self.sb_ui_font_size, self.sb_editor_font_size]:
            w.valueChanged.connect(lambda _: self.changed.emit())

    def _load(self):
        if not self.cfg:
            return
        theme_name = self.cfg.get("theme", "Dark (Default)")
        idx = self.cb_theme.findText(theme_name)
        if idx >= 0:
            self.cb_theme.setCurrentIndex(idx)
        self.cb_accent.setCurrentIndex(self.cfg.get("accent_index", 0))
        self.sb_ui_font_size.setValue(self.cfg.get("ui_font_size", 10))
        self.sb_editor_font_size.setValue(self.cfg.get("editor_font_size", 12))
        density = self.cfg.get("ui_density", "Comfortable")
        self.cb_density.setCurrentText(density)
        self.chk_animations.setChecked(self.cfg.get("animations", True))
        self.chk_tooltips.setChecked(self.cfg.get("extended_tooltips", True))
        self.chk_show_breadcrumb.setChecked(self.cfg.get("show_breadcrumb", True))

    def _preview_theme(self):
        raw = self.cb_theme.currentText().lower().replace(" (default)", "").replace(" ", "_")
        if self.theme_mgr:
            self.theme_mgr.apply_theme(raw)

    def apply(self):
        if not self.cfg:
            return
        self.cfg.set("theme", self.cb_theme.currentText())
        self.cfg.set("accent_index", self.cb_accent.currentIndex())
        self.cfg.set("ui_font_size", self.sb_ui_font_size.value())
        self.cfg.set("editor_font_size", self.sb_editor_font_size.value())
        self.cfg.set("ui_density", self.cb_density.currentText())
        self.cfg.set("animations", self.chk_animations.isChecked())
        self.cfg.set("extended_tooltips", self.chk_tooltips.isChecked())
        self.cfg.set("show_breadcrumb", self.chk_show_breadcrumb.isChecked())
        self._preview_theme()

    def reset(self):
        self.cb_theme.setCurrentIndex(0)
        self.cb_accent.setCurrentIndex(0)
        self.sb_ui_font_size.setValue(10)
        self.sb_editor_font_size.setValue(12)
        self.cb_density.setCurrentText("Comfortable")
        self.chk_animations.setChecked(True)
        self.chk_tooltips.setChecked(True)
        self.chk_show_breadcrumb.setChecked(True)


class LanguagePanel(QWidget):
    """Language and localisation settings."""

    changed = Signal()

    LANGUAGES = [
        "English (US)", "English (UK)", "German (Deutsch)",
        "French (Français)", "Spanish (Español)", "Portuguese (Português)",
        "Japanese (日本語)", "Chinese Simplified (简体中文)", "Korean (한국어)",
    ]
    DATE_FORMATS = ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD", "DD.MM.YYYY"]

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.cfg = config_manager
        self._build()
        self._load()

    def _build(self):
        outer = QWidget()
        layout = QVBoxLayout(outer)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        layout.addWidget(_section_title("Language & Localisation"))
        layout.addWidget(_divider())

        lang_box = _card("Display Language")
        lf = QFormLayout(lang_box)
        lf.setContentsMargins(16, 20, 16, 16)
        lf.setSpacing(10)
        self.cb_language = QComboBox()
        self.cb_language.addItems(self.LANGUAGES)
        lbl_note = QLabel("⚠  Restart required for language changes to take full effect.")
        lbl_note.setStyleSheet("color: #d4a017; font-size: 11px;")
        lf.addRow("Interface language:", self.cb_language)
        lf.addRow(lbl_note)
        layout.addWidget(lang_box)

        format_box = _card("Date & Number Format")
        ff = QFormLayout(format_box)
        ff.setContentsMargins(16, 20, 16, 16)
        ff.setSpacing(10)
        self.cb_date_format = QComboBox()
        self.cb_date_format.addItems(self.DATE_FORMATS)
        self.cb_decimal = QComboBox()
        self.cb_decimal.addItems(["Period (1,234.56)", "Comma (1.234,56)"])
        ff.addRow("Date format:", self.cb_date_format)
        ff.addRow("Number format:", self.cb_decimal)
        layout.addWidget(format_box)

        layout.addStretch()
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(_build_scroll(outer))

        self.cb_language.currentIndexChanged.connect(lambda _: self.changed.emit())
        self.cb_date_format.currentIndexChanged.connect(lambda _: self.changed.emit())

    def _load(self):
        if not self.cfg:
            return
        self.cb_language.setCurrentText(self.cfg.get("language", "English (US)"))
        self.cb_date_format.setCurrentText(self.cfg.get("date_format", "DD/MM/YYYY"))
        self.cb_decimal.setCurrentIndex(self.cfg.get("decimal_format", 0))

    def apply(self):
        if not self.cfg:
            return
        self.cfg.set("language", self.cb_language.currentText())
        self.cfg.set("date_format", self.cb_date_format.currentText())
        self.cfg.set("decimal_format", self.cb_decimal.currentIndex())

    def reset(self):
        self.cb_language.setCurrentIndex(0)
        self.cb_date_format.setCurrentIndex(0)
        self.cb_decimal.setCurrentIndex(0)


class WorkspaceSettingsPanel(QWidget):
    """Workspace management preferences."""

    changed = Signal()

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.cfg = config_manager
        self._build()
        self._load()

    def _build(self):
        outer = QWidget()
        layout = QVBoxLayout(outer)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        layout.addWidget(_section_title("Workspace Settings"))
        layout.addWidget(_divider())

        dir_box = _card("Default Directory")
        df = QFormLayout(dir_box)
        df.setContentsMargins(16, 20, 16, 16)
        df.setSpacing(10)
        dir_row = QHBoxLayout()
        self.txt_workspace_dir = QLineEdit()
        self.txt_workspace_dir.setPlaceholderText("Select default workspace root folder...")
        self.txt_workspace_dir.setReadOnly(True)
        btn_browse = QPushButton("Browse…")
        btn_browse.setMaximumWidth(90)
        btn_browse.clicked.connect(self._browse_dir)
        dir_row.addWidget(self.txt_workspace_dir)
        dir_row.addWidget(btn_browse)
        df.addRow("Workspace root:", dir_row)
        self.sb_recent = QSpinBox()
        self.sb_recent.setRange(1, 50)
        df.addRow("Recent workspaces to remember:", self.sb_recent)
        layout.addWidget(dir_box)

        auto_box = _card("Auto-Save & Backups")
        af = QFormLayout(auto_box)
        af.setContentsMargins(16, 20, 16, 16)
        af.setSpacing(10)
        self.chk_autosave = QCheckBox("Enable auto-save")
        self.sb_autosave_interval = QSpinBox()
        self.sb_autosave_interval.setRange(1, 60)
        self.sb_autosave_interval.setSuffix(" minutes")
        self.chk_backup_on_close = QCheckBox("Create backup on workspace close")
        self.sb_backup_count = QSpinBox()
        self.sb_backup_count.setRange(1, 30)
        self.sb_backup_count.setSuffix(" backups")
        af.addRow(self.chk_autosave)
        af.addRow("Auto-save interval:", self.sb_autosave_interval)
        af.addRow(self.chk_backup_on_close)
        af.addRow("Maximum backups to keep:", self.sb_backup_count)
        layout.addWidget(auto_box)

        layout.addStretch()
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(_build_scroll(outer))

        self.chk_autosave.stateChanged.connect(lambda _: self.changed.emit())
        self.chk_backup_on_close.stateChanged.connect(lambda _: self.changed.emit())

    def _browse_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Select Workspace Root")
        if d:
            self.txt_workspace_dir.setText(d)
            self.changed.emit()

    def _load(self):
        if not self.cfg:
            return
        self.txt_workspace_dir.setText(
            self.cfg.get("default_workspace_dir", str(AppConstants.WORKSPACES_DIR)))
        self.sb_recent.setValue(self.cfg.get("recent_workspaces_count", 10))
        self.chk_autosave.setChecked(self.cfg.get("autosave_enabled", True))
        self.sb_autosave_interval.setValue(self.cfg.get("autosave_interval_min", 5))
        self.chk_backup_on_close.setChecked(self.cfg.get("backup_on_close", True))
        self.sb_backup_count.setValue(self.cfg.get("max_backups", 5))

    def apply(self):
        if not self.cfg:
            return
        self.cfg.set("default_workspace_dir", self.txt_workspace_dir.text())
        self.cfg.set("recent_workspaces_count", self.sb_recent.value())
        self.cfg.set("autosave_enabled", self.chk_autosave.isChecked())
        self.cfg.set("autosave_interval_min", self.sb_autosave_interval.value())
        self.cfg.set("backup_on_close", self.chk_backup_on_close.isChecked())
        self.cfg.set("max_backups", self.sb_backup_count.value())

    def reset(self):
        self.txt_workspace_dir.setText(str(AppConstants.WORKSPACES_DIR))
        self.sb_recent.setValue(10)
        self.chk_autosave.setChecked(True)
        self.sb_autosave_interval.setValue(5)
        self.chk_backup_on_close.setChecked(True)
        self.sb_backup_count.setValue(5)


class AIProvidersPanel(QWidget):
    """AI provider configuration hub — loads existing provider widgets."""

    changed = Signal()

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.cfg = config_manager
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        layout.addWidget(_section_title("AI Providers"))
        layout.addWidget(_divider())

        tabs = QTabWidget()
        tabs.setDocumentMode(True)

        # Load each provider widget safely
        tabs.addTab(self._load_openai_tab(), "OpenAI")
        tabs.addTab(self._load_gemini_tab(), "Gemini")
        tabs.addTab(self._load_groq_tab(), "Groq")
        tabs.addTab(self._load_deepseek_tab(), "DeepSeek")
        tabs.addTab(self._load_openrouter_tab(), "OpenRouter")

        layout.addWidget(tabs, 1)

    def _load_openai_tab(self) -> QWidget:
        try:
            from gui.ai.openai_settings_widget import OpenAISettingsWidget
            w = OpenAISettingsWidget()
            w.settings_saved.connect(lambda _: self.changed.emit())
            return w
        except Exception as e:
            return self._err_tab(f"OpenAI widget unavailable: {e}")

    def _load_gemini_tab(self) -> QWidget:
        try:
            from gui.ai.gemini_settings_widget import GeminiSettingsWidget
            w = GeminiSettingsWidget()
            w.settings_saved.connect(lambda _: self.changed.emit())
            return w
        except Exception as e:
            return self._err_tab(f"Gemini widget unavailable: {e}")

    def _load_groq_tab(self) -> QWidget:
        try:
            from gui.ai.groq_settings_widget import GroqSettingsWidget
            w = GroqSettingsWidget()
            w.settings_saved.connect(lambda _: self.changed.emit())
            return w
        except Exception as e:
            return self._err_tab(f"Groq widget unavailable: {e}")

    def _load_deepseek_tab(self) -> QWidget:
        try:
            from gui.ai.deepseek_settings_widget import DeepSeekSettingsWidget
            w = DeepSeekSettingsWidget()
            w.settings_saved.connect(lambda _: self.changed.emit())
            return w
        except Exception as e:
            return self._err_tab(f"DeepSeek widget unavailable: {e}")

    def _load_openrouter_tab(self) -> QWidget:
        try:
            from gui.ai.openrouter_settings_widget import OpenRouterSettingsWidget
            w = OpenRouterSettingsWidget()
            w.settings_saved.connect(lambda _: self.changed.emit())
            return w
        except Exception as e:
            return self._err_tab(f"OpenRouter widget unavailable: {e}")

    def _err_tab(self, msg: str) -> QWidget:
        w = QWidget()
        lyt = QVBoxLayout(w)
        lbl = QLabel(f"⚠  {msg}")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("color: #858585; padding: 40px;")
        lyt.addWidget(lbl)
        return w

    def apply(self):
        pass  # Each provider widget handles its own save

    def reset(self):
        pass


class APIKeysPanel(QWidget):
    """Centralised API key management table."""

    changed = Signal()

    KNOWN_SERVICES = [
        ("OpenAI", "openai_api_key", "sk-..."),
        ("Google Gemini", "gemini_api_key", "AIza..."),
        ("Groq", "groq_api_key", "gsk_..."),
        ("DeepSeek", "deepseek_api_key", "sk-..."),
        ("OpenRouter", "openrouter_api_key", "sk-or-..."),
        ("Shutterstock", "shutterstock_api_key", "Your Shutterstock key"),
        ("Adobe Stock", "adobe_api_key", "Your Adobe Stock key"),
        ("Getty Images", "getty_api_key", "Your Getty key"),
    ]

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.cfg = config_manager
        self._build()
        self._load()

    def _build(self):
        outer = QWidget()
        layout = QVBoxLayout(outer)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        layout.addWidget(_section_title("API Keys"))
        layout.addWidget(_divider())

        info = QLabel(
            "API keys are stored locally in your configuration file.  "
            "Never share your config directory with untrusted parties."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #858585; font-size: 11px; padding: 4px 0;")
        layout.addWidget(info)

        self.table = QTableWidget(len(self.KNOWN_SERVICES), 3)
        self.table.setHorizontalHeaderLabels(["Service", "API Key", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)

        self._key_edits = {}
        for row, (service, key_name, placeholder) in enumerate(self.KNOWN_SERVICES):
            svc_item = QTableWidgetItem(service)
            svc_item.setFlags(svc_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, svc_item)

            edit = QLineEdit()
            edit.setEchoMode(QLineEdit.EchoMode.Password)
            edit.setPlaceholderText(placeholder)
            edit.textChanged.connect(lambda _, r=row: self._update_status(r))
            self.table.setCellWidget(row, 1, edit)
            self._key_edits[key_name] = edit

            status = QLabel("○ Not set")
            status.setStyleSheet("color: #858585; padding: 0 8px;")
            self.table.setCellWidget(row, 2, status)

        self.table.setMinimumHeight(280)
        layout.addWidget(self.table)

        btn_row = QHBoxLayout()
        self.btn_reveal = QPushButton("👁  Show / Hide Key")
        self.btn_reveal.setCheckable(True)
        self.btn_reveal.toggled.connect(self._toggle_reveal)
        self.btn_clear_all = QPushButton("Clear All Keys")
        self.btn_clear_all.setStyleSheet("color: #f48771;")
        self.btn_clear_all.clicked.connect(self._clear_all)
        btn_row.addWidget(self.btn_reveal)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_clear_all)
        layout.addLayout(btn_row)

        layout.addStretch()
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(_build_scroll(outer))

    def _load(self):
        if not self.cfg:
            return
        for service, key_name, _ in self.KNOWN_SERVICES:
            val = self.cfg.get(key_name, "")
            if val and key_name in self._key_edits:
                self._key_edits[key_name].setText(val)
        for row in range(len(self.KNOWN_SERVICES)):
            self._update_status(row)

    def _update_status(self, row: int):
        _, key_name, _ = self.KNOWN_SERVICES[row]
        edit = self._key_edits.get(key_name)
        status_lbl = self.table.cellWidget(row, 2)
        if not edit or not status_lbl:
            return
        if edit.text().strip():
            status_lbl.setText("● Configured")
            status_lbl.setStyleSheet("color: #3fb950; padding: 0 8px; font-weight: bold;")
        else:
            status_lbl.setText("○ Not set")
            status_lbl.setStyleSheet("color: #858585; padding: 0 8px;")
        self.changed.emit()

    def _toggle_reveal(self, checked: bool):
        mode = QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        for edit in self._key_edits.values():
            edit.setEchoMode(mode)

    def _clear_all(self):
        if QMessageBox.question(
            self, "Clear All API Keys",
            "This will remove all stored API keys. Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            for edit in self._key_edits.values():
                edit.clear()

    def apply(self):
        if not self.cfg:
            return
        for _, key_name, _ in self.KNOWN_SERVICES:
            val = self._key_edits[key_name].text().strip()
            self.cfg.set(key_name, val)

    def reset(self):
        for edit in self._key_edits.values():
            edit.clear()


class MarketplaceProfilesPanel(QWidget):
    """Marketplace profile configuration."""

    changed = Signal()

    MARKETPLACES = [
        "Shutterstock", "Adobe Stock", "Getty Images",
        "iStock", "Alamy", "Dreamstime", "123RF", "Depositphotos",
        "Pond5", "Stocksy", "EyeEm",
    ]

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.cfg = config_manager
        self._build()
        self._load()

    def _build(self):
        outer = QWidget()
        layout = QVBoxLayout(outer)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        layout.addWidget(_section_title("Marketplace Profiles"))
        layout.addWidget(_divider())

        active_box = _card("Active Marketplaces")
        af = QVBoxLayout(active_box)
        af.setContentsMargins(16, 20, 16, 16)
        af.setSpacing(8)
        self._market_checks = {}
        for name in self.MARKETPLACES:
            chk = QCheckBox(name)
            chk.stateChanged.connect(lambda _: self.changed.emit())
            af.addWidget(chk)
            self._market_checks[name] = chk
        layout.addWidget(active_box)

        defaults_box = _card("Upload Defaults")
        df = QFormLayout(defaults_box)
        df.setContentsMargins(16, 20, 16, 16)
        df.setSpacing(10)
        self.cb_default_category = QComboBox()
        self.cb_default_category.addItems([
            "Nature", "Business", "Technology", "Travel",
            "Food & Drink", "Architecture", "People", "Abstract",
        ])
        self.sb_min_price = QDoubleSpinBox()
        self.sb_min_price.setRange(0, 999)
        self.sb_min_price.setPrefix("$ ")
        self.sb_min_price.setDecimals(2)
        self.chk_exclusive = QCheckBox("Mark new uploads as exclusive by default")
        df.addRow("Default category:", self.cb_default_category)
        df.addRow("Minimum price floor:", self.sb_min_price)
        df.addRow(self.chk_exclusive)
        layout.addWidget(defaults_box)

        layout.addStretch()
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(_build_scroll(outer))

    def _load(self):
        if not self.cfg:
            return
        active = self.cfg.get("active_marketplaces", ["Shutterstock", "Adobe Stock"])
        for name, chk in self._market_checks.items():
            chk.setChecked(name in active)
        self.cb_default_category.setCurrentText(
            self.cfg.get("default_category", "Nature"))
        self.sb_min_price.setValue(self.cfg.get("min_price", 0.0))
        self.chk_exclusive.setChecked(self.cfg.get("default_exclusive", False))

    def apply(self):
        if not self.cfg:
            return
        active = [n for n, c in self._market_checks.items() if c.isChecked()]
        self.cfg.set("active_marketplaces", active)
        self.cfg.set("default_category", self.cb_default_category.currentText())
        self.cfg.set("min_price", self.sb_min_price.value())
        self.cfg.set("default_exclusive", self.chk_exclusive.isChecked())

    def reset(self):
        for name, chk in self._market_checks.items():
            chk.setChecked(name in ("Shutterstock", "Adobe Stock"))
        self.cb_default_category.setCurrentIndex(0)
        self.sb_min_price.setValue(0.0)
        self.chk_exclusive.setChecked(False)


class PromptProfilesPanel(QWidget):
    """Prompt template management."""

    changed = Signal()

    DEFAULT_PROMPTS = {
        "Standard Description": (
            "Write a concise, professional stock photo description for the following image. "
            "Focus on subject, mood, lighting, and commercial appeal. Maximum 200 words."
        ),
        "SEO-Optimised Title": (
            "Generate a compelling, keyword-rich title for this stock photo. "
            "Title should be descriptive, searchable, and under 70 characters."
        ),
        "Keyword Extraction": (
            "Extract 30–50 highly relevant, commercially valuable keywords for this stock photo. "
            "Include subjects, concepts, colours, mood, and use cases. Output as a comma-separated list."
        ),
    }

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.cfg = config_manager
        self._build()
        self._load()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        layout.addWidget(_section_title("Prompt Profiles"))
        layout.addWidget(_divider())

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # List
        left = QWidget()
        left_lyt = QVBoxLayout(left)
        left_lyt.setContentsMargins(0, 0, 0, 0)
        left_lyt.setSpacing(6)
        lbl = QLabel("Profiles")
        lbl.setStyleSheet("font-weight: bold; color: #cccccc;")
        left_lyt.addWidget(lbl)
        self.lst_profiles = QListWidget()
        self.lst_profiles.currentRowChanged.connect(self._on_profile_select)
        left_lyt.addWidget(self.lst_profiles)
        btn_row = QHBoxLayout()
        self.btn_add_profile = QPushButton("+ New")
        self.btn_del_profile = QPushButton("Delete")
        self.btn_del_profile.setStyleSheet("color: #f48771;")
        btn_row.addWidget(self.btn_add_profile)
        btn_row.addWidget(self.btn_del_profile)
        left_lyt.addLayout(btn_row)
        self.btn_add_profile.clicked.connect(self._add_profile)
        self.btn_del_profile.clicked.connect(self._delete_profile)
        splitter.addWidget(left)

        # Editor
        right = QWidget()
        right_lyt = QVBoxLayout(right)
        right_lyt.setContentsMargins(0, 0, 0, 0)
        right_lyt.setSpacing(8)
        lbl2 = QLabel("Prompt Template")
        lbl2.setStyleSheet("font-weight: bold; color: #cccccc;")
        right_lyt.addWidget(lbl2)
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Profile name…")
        self.txt_name.textChanged.connect(lambda _: self.changed.emit())
        right_lyt.addWidget(self.txt_name)
        self.txt_prompt = QTextEdit()
        self.txt_prompt.setPlaceholderText("Enter your prompt template here…")
        self.txt_prompt.textChanged.connect(self.changed.emit)
        right_lyt.addWidget(self.txt_prompt)

        meta_form = QFormLayout()
        meta_form.setSpacing(6)
        self.cb_profile_type = QComboBox()
        self.cb_profile_type.addItems(["Description", "Title", "Keywords", "Tags", "Custom"])
        self.sb_max_tokens = QSpinBox()
        self.sb_max_tokens.setRange(50, 4096)
        self.sb_max_tokens.setValue(500)
        self.sb_max_tokens.setSuffix("  tokens")
        meta_form.addRow("Profile type:", self.cb_profile_type)
        meta_form.addRow("Max output tokens:", self.sb_max_tokens)
        right_lyt.addLayout(meta_form)

        splitter.addWidget(right)
        splitter.setSizes([200, 600])
        layout.addWidget(splitter, 1)

    def _load(self):
        self.lst_profiles.clear()
        saved = (self.cfg.get("prompt_profiles", {}) if self.cfg else {}) or {}
        self._profiles = {**self.DEFAULT_PROMPTS, **saved}
        for name in self._profiles:
            self.lst_profiles.addItem(QListWidgetItem(name))
        if self.lst_profiles.count():
            self.lst_profiles.setCurrentRow(0)

    def _on_profile_select(self, row: int):
        if row < 0:
            return
        name = self.lst_profiles.item(row).text()
        self.txt_name.setText(name)
        self.txt_prompt.setPlainText(self._profiles.get(name, ""))

    def _add_profile(self):
        name = f"New Profile {self.lst_profiles.count() + 1}"
        self._profiles[name] = ""
        self.lst_profiles.addItem(QListWidgetItem(name))
        self.lst_profiles.setCurrentRow(self.lst_profiles.count() - 1)
        self.changed.emit()

    def _delete_profile(self):
        row = self.lst_profiles.currentRow()
        if row < 0:
            return
        name = self.lst_profiles.item(row).text()
        self._profiles.pop(name, None)
        self.lst_profiles.takeItem(row)
        self.changed.emit()

    def apply(self):
        # Save current editor back
        row = self.lst_profiles.currentRow()
        if row >= 0:
            old_name = self.lst_profiles.item(row).text()
            new_name = self.txt_name.text().strip() or old_name
            if new_name != old_name:
                self._profiles[new_name] = self._profiles.pop(old_name, "")
                self.lst_profiles.item(row).setText(new_name)
            self._profiles[new_name] = self.txt_prompt.toPlainText()
        if self.cfg:
            self.cfg.set("prompt_profiles", self._profiles)

    def reset(self):
        self._profiles = dict(self.DEFAULT_PROMPTS)
        self.lst_profiles.clear()
        for name in self._profiles:
            self.lst_profiles.addItem(QListWidgetItem(name))
        if self.lst_profiles.count():
            self.lst_profiles.setCurrentRow(0)


class PerformancePanel(QWidget):
    """Processing and performance tuning."""

    changed = Signal()

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.cfg = config_manager
        self._build()
        self._load()

    def _build(self):
        outer = QWidget()
        layout = QVBoxLayout(outer)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        layout.addWidget(_section_title("Performance & Processing"))
        layout.addWidget(_divider())

        batch_box = _card("Batch Processing")
        bf = QFormLayout(batch_box)
        bf.setContentsMargins(16, 20, 16, 16)
        bf.setSpacing(10)
        self.sb_batch_size = QSpinBox()
        self.sb_batch_size.setRange(1, 500)
        self.sb_batch_size.setSuffix(" images")
        self.sb_concurrent_ai = QSpinBox()
        self.sb_concurrent_ai.setRange(1, 20)
        self.sb_concurrent_ai.setSuffix(" parallel requests")
        self.sb_ai_delay = QDoubleSpinBox()
        self.sb_ai_delay.setRange(0, 10)
        self.sb_ai_delay.setSingleStep(0.1)
        self.sb_ai_delay.setSuffix(" s  (rate-limit delay)")
        self.chk_priority_boost = QCheckBox("Boost AI processing thread priority")
        bf.addRow("Batch size:", self.sb_batch_size)
        bf.addRow("Concurrent AI requests:", self.sb_concurrent_ai)
        bf.addRow("Inter-request delay:", self.sb_ai_delay)
        bf.addRow(self.chk_priority_boost)
        layout.addWidget(batch_box)

        img_box = _card("Image Processing")
        iif = QFormLayout(img_box)
        iif.setContentsMargins(16, 20, 16, 16)
        iif.setSpacing(10)
        self.sb_thumbnail_size = QSpinBox()
        self.sb_thumbnail_size.setRange(64, 512)
        self.sb_thumbnail_size.setSuffix(" px")
        self.sb_thumbnail_size.setSingleStep(32)
        self.chk_lazy_load = QCheckBox("Enable lazy image loading (improves grid performance)")
        self.chk_preload_meta = QCheckBox("Pre-load EXIF metadata on import")
        iif.addRow("Thumbnail size:", self.sb_thumbnail_size)
        iif.addRow(self.chk_lazy_load)
        iif.addRow(self.chk_preload_meta)
        layout.addWidget(img_box)

        cache_box = _card("Cache Management")
        cf = QVBoxLayout(cache_box)
        cf.setContentsMargins(16, 20, 16, 16)
        cf.setSpacing(8)
        self.lbl_cache_size = QLabel("Calculating cache size…")
        self.lbl_cache_size.setStyleSheet("color: #858585;")
        btn_clear_cache = QPushButton("Clear Image Cache")
        btn_clear_cache.setMaximumWidth(160)
        btn_clear_cache.clicked.connect(self._clear_cache)
        cf.addWidget(self.lbl_cache_size)
        cf.addWidget(btn_clear_cache)
        layout.addWidget(cache_box)

        QTimer.singleShot(200, self._compute_cache_size)

        layout.addStretch()
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(_build_scroll(outer))

        for w in [self.sb_batch_size, self.sb_concurrent_ai, self.sb_ai_delay, self.sb_thumbnail_size]:
            w.valueChanged.connect(lambda _: self.changed.emit())

    def _compute_cache_size(self):
        try:
            cache_path = AppConstants.CACHE_DIR
            if cache_path.exists():
                size = sum(f.stat().st_size for f in cache_path.rglob("*") if f.is_file())
                mb = size / (1024 * 1024)
                self.lbl_cache_size.setText(f"Cache size: {mb:.1f} MB  ({cache_path})")
            else:
                self.lbl_cache_size.setText("Cache directory not found.")
        except Exception:
            self.lbl_cache_size.setText("Unable to calculate cache size.")

    def _clear_cache(self):
        try:
            cache_path = AppConstants.CACHE_DIR
            if cache_path.exists():
                shutil.rmtree(cache_path)
                cache_path.mkdir(parents=True, exist_ok=True)
                QMessageBox.information(self, "Cache Cleared", "Image cache has been cleared successfully.")
                self._compute_cache_size()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to clear cache:\n{e}")

    def _load(self):
        if not self.cfg:
            return
        self.sb_batch_size.setValue(self.cfg.get("batch_size", 50))
        self.sb_concurrent_ai.setValue(self.cfg.get("concurrent_ai_requests", 3))
        self.sb_ai_delay.setValue(self.cfg.get("ai_request_delay", 0.5))
        self.chk_priority_boost.setChecked(self.cfg.get("priority_boost", False))
        self.sb_thumbnail_size.setValue(self.cfg.get("thumbnail_size", 128))
        self.chk_lazy_load.setChecked(self.cfg.get("lazy_load_images", True))
        self.chk_preload_meta.setChecked(self.cfg.get("preload_metadata", True))

    def apply(self):
        if not self.cfg:
            return
        self.cfg.set("batch_size", self.sb_batch_size.value())
        self.cfg.set("concurrent_ai_requests", self.sb_concurrent_ai.value())
        self.cfg.set("ai_request_delay", self.sb_ai_delay.value())
        self.cfg.set("priority_boost", self.chk_priority_boost.isChecked())
        self.cfg.set("thumbnail_size", self.sb_thumbnail_size.value())
        self.cfg.set("lazy_load_images", self.chk_lazy_load.isChecked())
        self.cfg.set("preload_metadata", self.chk_preload_meta.isChecked())

    def reset(self):
        self.sb_batch_size.setValue(50)
        self.sb_concurrent_ai.setValue(3)
        self.sb_ai_delay.setValue(0.5)
        self.chk_priority_boost.setChecked(False)
        self.sb_thumbnail_size.setValue(128)
        self.chk_lazy_load.setChecked(True)
        self.chk_preload_meta.setChecked(True)


class LoggingPanel(QWidget):
    """Logging configuration."""

    changed = Signal()

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.cfg = config_manager
        self._build()
        self._load()

    def _build(self):
        outer = QWidget()
        layout = QVBoxLayout(outer)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        layout.addWidget(_section_title("Logging"))
        layout.addWidget(_divider())

        config_box = _card("Log Configuration")
        cf = QFormLayout(config_box)
        cf.setContentsMargins(16, 20, 16, 16)
        cf.setSpacing(10)
        self.cb_log_level = QComboBox()
        self.cb_log_level.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.chk_log_to_file = QCheckBox("Write logs to file")
        self.chk_log_to_console = QCheckBox("Output logs to console")
        self.sb_max_log_size = QSpinBox()
        self.sb_max_log_size.setRange(1, 500)
        self.sb_max_log_size.setSuffix(" MB")
        self.sb_log_backups = QSpinBox()
        self.sb_log_backups.setRange(1, 20)
        self.sb_log_backups.setSuffix(" files")
        dir_row = QHBoxLayout()
        self.txt_log_dir = QLineEdit()
        self.txt_log_dir.setReadOnly(True)
        btn_open = QPushButton("Open Folder")
        btn_open.setMaximumWidth(100)
        btn_open.clicked.connect(self._open_log_dir)
        dir_row.addWidget(self.txt_log_dir)
        dir_row.addWidget(btn_open)
        cf.addRow("Log level:", self.cb_log_level)
        cf.addRow(self.chk_log_to_file)
        cf.addRow(self.chk_log_to_console)
        cf.addRow("Max log file size:", self.sb_max_log_size)
        cf.addRow("Backup files to keep:", self.sb_log_backups)
        cf.addRow("Log directory:", dir_row)
        layout.addWidget(config_box)

        viewer_box = _card("Live Log Viewer")
        vf = QVBoxLayout(viewer_box)
        vf.setContentsMargins(16, 20, 16, 16)
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setFont(QFont("Consolas", 9))
        self.log_viewer.setMaximumHeight(200)
        self.log_viewer.setStyleSheet("background: #1e1e1e; color: #d4d4d4;")
        self._load_recent_log()
        vf.addWidget(self.log_viewer)
        btn_row = QHBoxLayout()
        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self._load_recent_log)
        btn_clear_logs = QPushButton("Clear Log Files")
        btn_clear_logs.setStyleSheet("color: #f48771;")
        btn_clear_logs.clicked.connect(self._clear_logs)
        btn_row.addWidget(btn_refresh)
        btn_row.addStretch()
        btn_row.addWidget(btn_clear_logs)
        vf.addLayout(btn_row)
        layout.addWidget(viewer_box)

        layout.addStretch()
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(_build_scroll(outer))

        self.cb_log_level.currentIndexChanged.connect(lambda _: self.changed.emit())

    def _load_recent_log(self):
        try:
            log_files = sorted(AppConstants.LOGS_DIR.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
            if log_files:
                with open(log_files[0], "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                self.log_viewer.setPlainText("".join(lines[-100:]))
                self.log_viewer.verticalScrollBar().setValue(
                    self.log_viewer.verticalScrollBar().maximum())
            else:
                self.log_viewer.setPlainText("No log files found.")
        except Exception as e:
            self.log_viewer.setPlainText(f"Error reading logs: {e}")

    def _clear_logs(self):
        if QMessageBox.question(
            self, "Clear Logs", "Delete all log files?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            for f in AppConstants.LOGS_DIR.glob("*.log"):
                try:
                    f.unlink()
                except Exception:
                    pass
            self.log_viewer.setPlainText("Log files cleared.")

    def _open_log_dir(self):
        import subprocess, sys
        path = str(AppConstants.LOGS_DIR)
        if sys.platform == "win32":
            subprocess.Popen(["explorer", path])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def _load(self):
        if not self.cfg:
            return
        self.cb_log_level.setCurrentText(self.cfg.get("log_level", "INFO"))
        self.chk_log_to_file.setChecked(self.cfg.get("log_to_file", True))
        self.chk_log_to_console.setChecked(self.cfg.get("log_to_console", True))
        self.sb_max_log_size.setValue(self.cfg.get("max_log_size_mb", 10))
        self.sb_log_backups.setValue(self.cfg.get("log_backup_count", 5))
        self.txt_log_dir.setText(str(AppConstants.LOGS_DIR))

    def apply(self):
        if not self.cfg:
            return
        self.cfg.set("log_level", self.cb_log_level.currentText())
        self.cfg.set("log_to_file", self.chk_log_to_file.isChecked())
        self.cfg.set("log_to_console", self.chk_log_to_console.isChecked())
        self.cfg.set("max_log_size_mb", self.sb_max_log_size.value())
        self.cfg.set("log_backup_count", self.sb_log_backups.value())
        # Apply log level to root logger
        import logging as _logging
        level = getattr(_logging, self.cb_log_level.currentText(), _logging.INFO)
        _logging.getLogger().setLevel(level)

    def reset(self):
        self.cb_log_level.setCurrentText("INFO")
        self.chk_log_to_file.setChecked(True)
        self.chk_log_to_console.setChecked(True)
        self.sb_max_log_size.setValue(10)
        self.sb_log_backups.setValue(5)


class BackupPanel(QWidget):
    """Backup and restore settings."""

    changed = Signal()

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.cfg = config_manager
        self._build()

    def _build(self):
        outer = QWidget()
        layout = QVBoxLayout(outer)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        layout.addWidget(_section_title("Backup & Restore"))
        layout.addWidget(_divider())

        schedule_box = _card("Automatic Backup Schedule")
        sf = QFormLayout(schedule_box)
        sf.setContentsMargins(16, 20, 16, 16)
        sf.setSpacing(10)
        self.chk_auto_backup = QCheckBox("Enable scheduled backups")
        self.cb_backup_frequency = QComboBox()
        self.cb_backup_frequency.addItems(["Daily", "Weekly", "On workspace close", "Manually only"])
        self.sb_keep_backups = QSpinBox()
        self.sb_keep_backups.setRange(1, 50)
        self.sb_keep_backups.setSuffix(" most recent")
        backup_dir_row = QHBoxLayout()
        self.txt_backup_dir = QLineEdit()
        self.txt_backup_dir.setReadOnly(True)
        self.txt_backup_dir.setText(str(AppConstants.BASE_DIR / "recovery"))
        btn_backup_browse = QPushButton("Browse…")
        btn_backup_browse.setMaximumWidth(90)
        btn_backup_browse.clicked.connect(self._browse_backup_dir)
        backup_dir_row.addWidget(self.txt_backup_dir)
        backup_dir_row.addWidget(btn_backup_browse)
        sf.addRow(self.chk_auto_backup)
        sf.addRow("Backup frequency:", self.cb_backup_frequency)
        sf.addRow("Backups to retain:", self.sb_keep_backups)
        sf.addRow("Backup location:", backup_dir_row)
        layout.addWidget(schedule_box)

        manual_box = _card("Manual Backup & Restore")
        mf = QVBoxLayout(manual_box)
        mf.setContentsMargins(16, 20, 16, 16)
        mf.setSpacing(10)
        btn_backup_now = QPushButton("⬆  Create Backup Now")
        btn_backup_now.clicked.connect(self._backup_now)
        btn_restore = QPushButton("⬇  Restore From Backup…")
        btn_restore.clicked.connect(self._restore_backup)
        self.lbl_last_backup = QLabel("Last backup: Unknown")
        self.lbl_last_backup.setStyleSheet("color: #858585; font-size: 11px;")
        mf.addWidget(btn_backup_now)
        mf.addWidget(btn_restore)
        mf.addWidget(self.lbl_last_backup)
        layout.addWidget(manual_box)

        layout.addStretch()
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(_build_scroll(outer))

        self._check_last_backup()

    def _browse_backup_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Select Backup Directory")
        if d:
            self.txt_backup_dir.setText(d)
            self.changed.emit()

    def _backup_now(self):
        try:
            backup_dir = Path(self.txt_backup_dir.text())
            backup_dir.mkdir(parents=True, exist_ok=True)
            config_file = AppConstants.APP_CONFIG_FILE
            if config_file.exists():
                import time
                dest = backup_dir / f"config_backup_{int(time.time())}.json"
                shutil.copy2(config_file, dest)
                self.lbl_last_backup.setText(f"Last backup: {dest.name}")
                QMessageBox.information(self, "Backup Complete", f"Configuration backed up to:\n{dest}")
        except Exception as e:
            QMessageBox.critical(self, "Backup Failed", str(e))

    def _restore_backup(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Select Backup File", str(self.txt_backup_dir.text()), "JSON Files (*.json)")
        if file:
            try:
                shutil.copy2(file, AppConstants.APP_CONFIG_FILE)
                QMessageBox.information(
                    self, "Restore Complete",
                    "Configuration restored. Restart the application to apply changes."
                )
            except Exception as e:
                QMessageBox.critical(self, "Restore Failed", str(e))

    def _check_last_backup(self):
        try:
            backup_dir = Path(self.txt_backup_dir.text())
            if backup_dir.exists():
                files = sorted(backup_dir.glob("config_backup_*.json"))
                if files:
                    import time
                    mtime = files[-1].stat().st_mtime
                    self.lbl_last_backup.setText(
                        f"Last backup: {files[-1].name}")
                    return
            self.lbl_last_backup.setText("Last backup: None found")
        except Exception:
            pass

    def apply(self):
        if not self.cfg:
            return
        self.cfg.set("auto_backup", self.chk_auto_backup.isChecked())
        self.cfg.set("backup_frequency", self.cb_backup_frequency.currentText())
        self.cfg.set("keep_backups", self.sb_keep_backups.value())
        self.cfg.set("backup_dir", self.txt_backup_dir.text())

    def reset(self):
        self.chk_auto_backup.setChecked(True)
        self.cb_backup_frequency.setCurrentIndex(2)
        self.sb_keep_backups.setValue(10)


class AboutPanel(QWidget):
    """About / version information."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        outer = QWidget()
        layout = QVBoxLayout(outer)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        layout.addWidget(_section_title("About StockPilot AI"))
        layout.addWidget(_divider())

        # App info
        about_box = _card("Application")
        af = QVBoxLayout(about_box)
        af.setContentsMargins(16, 20, 16, 16)
        af.setSpacing(8)
        name_lbl = QLabel(AppConstants.APP_NAME)
        name_lbl.setFont(QFont("", 18, QFont.Weight.Bold))
        name_lbl.setStyleSheet("color: #007acc;")
        ver_lbl = QLabel(f"Version {AppConstants.APP_VERSION}")
        ver_lbl.setStyleSheet("color: #cccccc; font-size: 13px;")
        desc_lbl = QLabel(
            "AI-powered metadata generation and stock photo management platform.\n"
            "Automate titles, descriptions, and keywords across all major marketplaces."
        )
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("color: #858585; padding-top: 8px;")
        af.addWidget(name_lbl)
        af.addWidget(ver_lbl)
        af.addWidget(desc_lbl)
        layout.addWidget(about_box)

        # System info
        sys_box = _card("System Information")
        sf = QFormLayout(sys_box)
        sf.setContentsMargins(16, 20, 16, 16)
        sf.setSpacing(8)

        import sys, platform
        try:
            from PySide6.QtCore import __version__ as pyside_ver
        except Exception:
            pyside_ver = "Unknown"

        for label, value in [
            ("Python version:", platform.python_version()),
            ("Platform:", f"{platform.system()} {platform.release()} ({platform.machine()})"),
            ("PySide6 version:", pyside_ver),
            ("Config directory:", str(AppConstants.CONFIG_DIR)),
            ("Workspace directory:", str(AppConstants.WORKSPACES_DIR)),
            ("Logs directory:", str(AppConstants.LOGS_DIR)),
        ]:
            key_lbl = QLabel(label)
            key_lbl.setStyleSheet("color: #858585;")
            val_lbl = QLabel(value)
            val_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            val_lbl.setStyleSheet("color: #cccccc;")
            sf.addRow(key_lbl, val_lbl)
        layout.addWidget(sys_box)

        # Links
        links_box = _card("Resources")
        lf = QVBoxLayout(links_box)
        lf.setContentsMargins(16, 20, 16, 16)
        lf.setSpacing(6)
        for text in ["📖  Documentation", "🐛  Report an Issue", "💬  Community Forum", "📋  Changelog"]:
            lbl = QLabel(text)
            lbl.setStyleSheet("color: #007acc; padding: 2px 0;")
            lf.addWidget(lbl)
        layout.addWidget(links_box)

        layout.addStretch()
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(_build_scroll(outer))

    def apply(self):
        pass

    def reset(self):
        pass


# ─────────────────────────────────────────────────────────────────────────────
# Main SettingsPage
# ─────────────────────────────────────────────────────────────────────────────

SECTIONS = [
    ("⚙  General",           "general"),
    ("🎨  Theme",             "theme"),
    ("🌐  Language",          "language"),
    ("📁  Workspace",         "workspace"),
    ("🤖  AI Providers",      "ai_providers"),
    ("🔑  API Keys",          "api_keys"),
    ("🏪  Marketplace Profiles", "marketplace"),
    ("📝  Prompt Profiles",   "prompts"),
    ("⚡  Performance",       "performance"),
    ("📋  Logging",           "logging"),
    ("💾  Backup",            "backup"),
    ("ℹ  About",             "about"),
]


class SettingsPage(QWidget):
    """
    Production-ready Settings page.
    Wired to DependencyContainer → ConfigManager, ThemeManager, EventBus.
    """

    def __init__(self, container=None, parent=None):
        super().__init__(parent)
        self.container = container

        # Resolve services via DI
        self._cfg = container.get_service("config_manager") if container else None
        self._theme = container.get_service("theme_manager") if container else None
        self._event_bus = container.get_service("event_bus") if container else None

        self._has_unsaved = False
        self._panels: dict[str, QWidget] = {}

        self._build_ui()
        self._build_toolbar()
        self._build_panels()
        self._connect_signals()

        # Navigate to first section
        self.lst_sections.setCurrentRow(0)

    # ──────────────────────────────────────
    # UI Construction
    # ──────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Top toolbar
        self.toolbar = QFrame()
        self.toolbar.setFixedHeight(48)
        self.toolbar.setStyleSheet("background: #252526; border-bottom: 1px solid #3f3f46;")
        toolbar_lyt = QHBoxLayout(self.toolbar)
        toolbar_lyt.setContentsMargins(16, 6, 16, 6)
        toolbar_lyt.setSpacing(8)

        lbl_title = QLabel("Settings")
        lbl_title.setFont(QFont("", 14, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #cccccc;")
        toolbar_lyt.addWidget(lbl_title)
        toolbar_lyt.addStretch()

        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("🔍  Search settings…")
        self.txt_search.setFixedWidth(240)
        self.txt_search.setStyleSheet("""
            QLineEdit {
                background: #3c3c3c;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px 10px;
                color: #cccccc;
            }
            QLineEdit:focus { border-color: #007acc; }
        """)
        self.txt_search.textChanged.connect(self._filter_sections)
        toolbar_lyt.addWidget(self.txt_search)

        toolbar_lyt.addSpacing(16)

        self.btn_import = QPushButton("⬆  Import")
        self.btn_export = QPushButton("⬇  Export")
        self.btn_reset = QPushButton("↺  Reset")
        self.btn_cancel = QPushButton("Cancel")
        self.btn_apply = QPushButton("✓  Apply")

        for btn, style in [
            (self.btn_import, ""),
            (self.btn_export, ""),
            (self.btn_reset, "color: #d4a017;"),
            (self.btn_cancel, ""),
            (self.btn_apply, "background: #007acc; color: white; font-weight: bold;"),
        ]:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: #3c3c3c;
                    border: 1px solid #555;
                    border-radius: 4px;
                    padding: 5px 14px;
                    color: #cccccc;
                    min-width: 70px;
                    {style}
                }}
                QPushButton:hover {{ background: #4a4a4a; border-color: #007acc; }}
                QPushButton:pressed {{ background: #2a2a2a; }}
            """)
            toolbar_lyt.addWidget(btn)

        root.addWidget(self.toolbar)

        # Status bar
        self.status_bar = QFrame()
        self.status_bar.setFixedHeight(24)
        self.status_bar.setStyleSheet("background: #007acc;")
        status_lyt = QHBoxLayout(self.status_bar)
        status_lyt.setContentsMargins(12, 0, 12, 0)
        self.lbl_status = QLabel("All settings up to date.")
        self.lbl_status.setStyleSheet("color: white; font-size: 11px;")
        status_lyt.addWidget(self.lbl_status)
        self.status_bar.hide()
        root.addWidget(self.status_bar)

        # Main content: sidebar + panel stack
        content = QSplitter(Qt.Orientation.Horizontal)
        content.setHandleWidth(1)
        content.setStyleSheet("QSplitter::handle { background: #3f3f46; }")

        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(210)
        sidebar.setStyleSheet("background: #252526;")
        sidebar_lyt = QVBoxLayout(sidebar)
        sidebar_lyt.setContentsMargins(0, 8, 0, 8)
        sidebar_lyt.setSpacing(0)

        self.lst_sections = QListWidget()
        self.lst_sections.setSpacing(1)
        self.lst_sections.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                outline: none;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 9px 20px;
                color: #cccccc;
                border-radius: 4px;
                margin: 1px 6px;
            }
            QListWidget::item:hover { background: #2a2d2e; }
            QListWidget::item:selected {
                background: #094771;
                color: #ffffff;
                font-weight: 600;
            }
        """)

        for label, section_id in SECTIONS:
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, section_id)
            self.lst_sections.addItem(item)

        sidebar_lyt.addWidget(self.lst_sections)
        content.addWidget(sidebar)

        # Panel area
        self.panel_stack = QStackedWidget()
        self.panel_stack.setStyleSheet("background: #1e1e1e;")
        content.addWidget(self.panel_stack)
        content.setSizes([210, 1000])
        content.setCollapsible(0, False)
        content.setCollapsible(1, False)

        root.addWidget(content, 1)

    def _build_toolbar(self):
        self.btn_apply.clicked.connect(self._apply)
        self.btn_cancel.clicked.connect(self._cancel)
        self.btn_reset.clicked.connect(self._reset_current)
        self.btn_import.clicked.connect(self._import_settings)
        self.btn_export.clicked.connect(self._export_settings)

    def _build_panels(self):
        panel_constructors = {
            "general":      lambda: GeneralPanel(self._cfg),
            "theme":        lambda: ThemePanel(self._cfg, self._theme),
            "language":     lambda: LanguagePanel(self._cfg),
            "workspace":    lambda: WorkspaceSettingsPanel(self._cfg),
            "ai_providers": lambda: AIProvidersPanel(self._cfg),
            "api_keys":     lambda: APIKeysPanel(self._cfg),
            "marketplace":  lambda: MarketplaceProfilesPanel(self._cfg),
            "prompts":      lambda: PromptProfilesPanel(self._cfg),
            "performance":  lambda: PerformancePanel(self._cfg),
            "logging":      lambda: LoggingPanel(self._cfg),
            "backup":       lambda: BackupPanel(self._cfg),
            "about":        lambda: AboutPanel(),
        }

        for _, section_id in SECTIONS:
            try:
                panel = panel_constructors[section_id]()
                if hasattr(panel, "changed"):
                    panel.changed.connect(self._on_changed)
            except Exception as e:
                logger.error(f"Failed to build panel '{section_id}': {e}", exc_info=True)
                panel = self._error_panel(section_id, e)
            self._panels[section_id] = panel
            self.panel_stack.addWidget(panel)

    def _error_panel(self, section_id: str, error: Exception) -> QWidget:
        w = QWidget()
        lyt = QVBoxLayout(w)
        lbl = QLabel(f"⚠  Failed to load panel '{section_id}':\n{error}")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("color: #f48771; padding: 40px;")
        lyt.addWidget(lbl)
        return w

    def _connect_signals(self):
        self.lst_sections.currentRowChanged.connect(self._on_section_changed)

    # ──────────────────────────────────────
    # Navigation
    # ──────────────────────────────────────

    def _on_section_changed(self, row: int):
        if row < 0 or row >= self.lst_sections.count():
            return
        item = self.lst_sections.item(row)
        if not item:
            return
        section_id = item.data(Qt.ItemDataRole.UserRole)
        panel = self._panels.get(section_id)
        if panel:
            self.panel_stack.setCurrentWidget(panel)

    def _filter_sections(self, query: str):
        q = query.strip().lower()
        for i in range(self.lst_sections.count()):
            item = self.lst_sections.item(i)
            item.setHidden(bool(q) and q not in item.text().lower())

    # ──────────────────────────────────────
    # Toolbar Actions
    # ──────────────────────────────────────

    def _on_changed(self):
        if not self._has_unsaved:
            self._has_unsaved = True
            self.status_bar.show()
            self.status_bar.setStyleSheet("background: #d4a017;")
            self.lbl_status.setText("⚠  You have unsaved changes — click Apply to save.")

    def _apply(self):
        try:
            for panel in self._panels.values():
                if hasattr(panel, "apply"):
                    panel.apply()
            self._has_unsaved = False
            self.status_bar.show()
            self.status_bar.setStyleSheet("background: #2ea043;")
            self.lbl_status.setText("✓  Settings saved successfully.")
            if self._event_bus:
                self._event_bus.publish("settings_applied")
            QTimer.singleShot(3000, self._hide_status)
            logger.info("Settings applied by user.")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save settings:\n{e}")
            logger.error(f"Settings apply error: {e}", exc_info=True)

    def _cancel(self):
        if self._has_unsaved:
            reply = QMessageBox.question(
                self, "Discard Changes",
                "You have unsaved changes. Discard them?",
                QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel,
            )
            if reply != QMessageBox.StandardButton.Discard:
                return
        # Reload all panels from config
        for panel in self._panels.values():
            if hasattr(panel, "_load"):
                try:
                    panel._load()
                except Exception:
                    pass
        self._has_unsaved = False
        self._hide_status()

    def _reset_current(self):
        item = self.lst_sections.currentItem()
        if not item:
            return
        section_id = item.data(Qt.ItemDataRole.UserRole)
        panel = self._panels.get(section_id)
        if panel and hasattr(panel, "reset"):
            reply = QMessageBox.question(
                self, "Reset to Defaults",
                f"Reset '{item.text().strip()}' settings to defaults?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                panel.reset()
                self._on_changed()

    def _import_settings(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Import Settings", "", "JSON Files (*.json)")
        if not file:
            return
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if self._cfg:
                for key, value in data.items():
                    self._cfg.set(key, value)
            # Reload all panels
            for panel in self._panels.values():
                if hasattr(panel, "_load"):
                    panel._load()
            self._on_changed()
            QMessageBox.information(self, "Import Successful",
                                    f"Settings imported from:\n{file}")
        except Exception as e:
            QMessageBox.critical(self, "Import Failed", str(e))

    def _export_settings(self):
        file, _ = QFileDialog.getSaveFileName(
            self, "Export Settings", "stockpilot_settings.json", "JSON Files (*.json)")
        if not file:
            return
        try:
            if self._cfg and hasattr(self._cfg, "_config"):
                data = self._cfg._config
            else:
                data = {}
            with open(file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            QMessageBox.information(self, "Export Successful",
                                    f"Settings exported to:\n{file}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))

    def _hide_status(self):
        self.status_bar.hide()

    # Public API for external navigation
    def navigate_to(self, section_id: str):
        for i in range(self.lst_sections.count()):
            item = self.lst_sections.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == section_id:
                self.lst_sections.setCurrentRow(i)
                break
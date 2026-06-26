# gui/pages/dashboard_page.py
"""
DashboardPage – Production-Ready Implementation
Sections:
  1. Welcome Banner
  2. Recent Workspaces
  3. Recent Images
  4. Recent Metadata
  5. Recent Export
  6. Quick Actions
  7. AI Provider Status
  8. Workspace Statistics
  9. Today's Activity
 10. Image Statistics
 11. Metadata Statistics
 12. Export Statistics
 13. Recent Logs
"""

import logging
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGridLayout, QScrollArea,
    QSizePolicy, QFileDialog, QMessageBox, QListWidget,
    QListWidgetItem
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QColor

from gui.widgets.icon_loader import IconLoader
from core.constants import AppConstants
from image.image_events import ImageEvents
from workspace.workspace_events import WorkspaceEvents

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Style constants
# ─────────────────────────────────────────────
_TEXT_PRIMARY = "#d4d4d4"
_TEXT_MUTED   = "#858585"
_ACCENT_BLUE  = "#007acc"
_ACCENT_GREEN = "#28a745"
_ACCENT_ORANGE = "#e8a000"
_ACCENT_RED   = "#f44747"
_ACCENT_PURPLE = "#9b59b6"

_CARD_STYLE = """
    QFrame {
        background-color: palette(base);
        border: 1px solid palette(alternate-base);
        border-radius: 8px;
    }
"""

class SectionLabel(QLabel):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(
            f"color: {_TEXT_MUTED}; font-size: 11px; font-weight: bold; "
            f"text-transform: uppercase; letter-spacing: 1px; padding: 0;"
        )

class CardFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(_CARD_STYLE)

class StatBadge(QLabel):
    def __init__(self, value: str, color: str = _ACCENT_BLUE, parent=None):
        super().__init__(value, parent)
        self.setStyleSheet(
            f"background-color: {color}22; color: {color}; "
            f"border: 1px solid {color}44; border-radius: 4px; "
            f"padding: 2px 8px; font-size: 11px; font-weight: bold;"
        )
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

class MetricCard(CardFrame):
    def __init__(self, title: str, value: str = "0", icon_name: str = "image",
                 accent: str = _ACCENT_BLUE, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(90)

        row = QHBoxLayout(self)
        row.setContentsMargins(16, 14, 16, 14)
        row.setSpacing(14)

        icon_container = QFrame()
        icon_container.setFixedSize(44, 44)
        icon_container.setStyleSheet(
            f"background-color: {accent}22; border: 1px solid {accent}44; border-radius: 22px;"
        )
        icon_row = QHBoxLayout(icon_container)
        icon_row.setContentsMargins(0, 0, 0, 0)
        lbl_icon = QLabel()
        px = IconLoader.get_icon(icon_name).pixmap(20, 20)
        lbl_icon.setPixmap(px)
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_icon.setStyleSheet("background: transparent; border: none;")
        icon_row.addWidget(lbl_icon)

        col = QVBoxLayout()
        col.setSpacing(2)
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"color: {_TEXT_MUTED}; font-size: 11px; background: transparent; border: none;")
        self.lbl_value = QLabel(str(value))
        self.lbl_value.setStyleSheet(f"color: palette(text); font-size: 20px; font-weight: bold; background: transparent; border: none;")
        col.addWidget(lbl_title)
        col.addWidget(self.lbl_value)

        row.addWidget(icon_container)
        row.addLayout(col)
        row.addStretch()

    def set_value(self, v: str) -> None:
        self.lbl_value.setText(str(v))

class QuickActionButton(QPushButton):
    def __init__(self, label: str, icon_name: str, accent: str = _ACCENT_BLUE, parent=None):
        super().__init__(parent)
        self.setText(f"  {label}")
        self.setIcon(IconLoader.get_icon(icon_name))
        self.setFixedHeight(42)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: palette(button);
                border: 1px solid palette(alternate-base);
                border-radius: 6px;
                color: palette(button-text);
                font-size: 13px;
                text-align: left;
                padding-left: 8px;
            }}
            QPushButton:hover {{
                background-color: {accent}22;
                border: 1px solid {accent};
                color: {accent};
            }}
            QPushButton:pressed {{
                background-color: {accent}44;
            }}
        """)

class StatusDot(QLabel):
    def __init__(self, online: bool, parent=None):
        super().__init__(parent)
        color = _ACCENT_GREEN if online else _TEXT_MUTED
        self.setFixedSize(10, 10)
        self.setStyleSheet(
            f"background-color: {color}; border-radius: 5px; border: none;"
        )

class LogRow(QFrame):
    def __init__(self, level: str, message: str, timestamp: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: transparent; border: none;")
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 2, 0, 2)
        row.setSpacing(8)

        colors = {"ERROR": _ACCENT_RED, "WARNING": _ACCENT_ORANGE,
                  "INFO": _ACCENT_BLUE, "DEBUG": _TEXT_MUTED}
        c = colors.get(level.upper(), _TEXT_MUTED)
        badge = StatBadge(level[:4], c)
        badge.setFixedWidth(40)

        lbl_msg = QLabel(message)
        lbl_msg.setStyleSheet(f"color: palette(text); font-size: 11px;")
        lbl_msg.setWordWrap(False)

        lbl_ts = QLabel(timestamp)
        lbl_ts.setStyleSheet(f"color: {_TEXT_MUTED}; font-size: 10px;")
        lbl_ts.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        row.addWidget(badge)
        row.addWidget(lbl_msg, 1)
        row.addWidget(lbl_ts)

def _section_header(title: str, btn_label: Optional[str] = None, btn_target: Optional[str] = None,
                    signal: Optional[Signal] = None) -> QHBoxLayout:
    hdr = QHBoxLayout()
    lbl = SectionLabel(title)
    hdr.addWidget(lbl)
    hdr.addStretch()
    if btn_label and signal:
        btn = QPushButton(btn_label)
        btn.setStyleSheet(
            f"QPushButton {{ color: {_ACCENT_BLUE}; background: transparent; border: none; "
            f"font-size: 11px; }} QPushButton:hover {{ color: palette(text); }}"
        )
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        if btn_target:
            btn.clicked.connect(lambda: signal.emit(btn_target))
        hdr.addWidget(btn)
    return hdr

class DashboardPage(QWidget):
    """Complete, production-ready Dashboard."""

    action_requested = Signal(str)

    def __init__(self, container=None, parent=None):
        super().__init__(parent)
        self.container = container
        self.setObjectName("DashboardPage")

        self._timer = QTimer(self)
        self._timer.setInterval(30_000)
        self._timer.timeout.connect(self._refresh_state)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        self._content = QWidget()
        self._content.setStyleSheet("background: transparent;")
        self._main_layout = QVBoxLayout(self._content)
        self._main_layout.setContentsMargins(32, 28, 32, 32)
        self._main_layout.setSpacing(20)

        self._scroll.setWidget(self._content)
        root_layout.addWidget(self._scroll)

        self._build_welcome_banner()
        self._build_quick_actions()
        self._build_stats_row()
        self._build_recent_row()
        self._build_bottom_row()
        self._main_layout.addStretch()

        self._connect_events()
        self._refresh_state()
        self._timer.start()

    def _build_welcome_banner(self) -> None:
        self._banner = CardFrame()
        self._banner.setMinimumHeight(100)
        self._banner.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {_ACCENT_BLUE}44, stop:1 palette(base)
                );
                border: 1px solid {_ACCENT_BLUE}44;
                border-radius: 10px;
            }}
        """)

        row = QHBoxLayout(self._banner)
        row.setContentsMargins(24, 20, 24, 20)
        row.setSpacing(20)

        col = QVBoxLayout()
        col.setSpacing(4)

        self._lbl_greeting = QLabel("Welcome to StockPilot AI")
        self._lbl_greeting.setStyleSheet("color: palette(text); font-size: 20px; font-weight: bold; background: transparent; border: none;")

        self._lbl_ws_info = QLabel("No workspace open — create or open one to get started.")
        self._lbl_ws_info.setStyleSheet(f"color: {_TEXT_MUTED}; font-size: 13px; background: transparent; border: none;")

        self._lbl_ws_path = QLabel("")
        self._lbl_ws_path.setStyleSheet(f"color: {_TEXT_MUTED}; font-size: 11px; background: transparent; border: none;")
        self._lbl_ws_path.hide()

        col.addWidget(self._lbl_greeting)
        col.addWidget(self._lbl_ws_info)
        col.addWidget(self._lbl_ws_path)
        col.addStretch()

        row.addLayout(col, 1)

        btn_col = QVBoxLayout()
        btn_col.setSpacing(8)
        btn_col.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        self._btn_refresh_banner = QPushButton(IconLoader.get_icon("refresh-cw"), " Refresh")
        self._btn_refresh_banner.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_refresh_banner.setFixedSize(110, 34)
        self._btn_refresh_banner.setStyleSheet(f"""
            QPushButton {{
                background-color: {_ACCENT_BLUE};
                color: #ffffff;
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #1a8ae0; }}
        """)
        self._btn_refresh_banner.clicked.connect(self._refresh_state)
        btn_col.addWidget(self._btn_refresh_banner)

        row.addLayout(btn_col)
        self._main_layout.addWidget(self._banner)

    def _build_quick_actions(self) -> None:
        hdr = _section_header("Quick Actions")
        self._main_layout.addLayout(hdr)

        card = CardFrame()
        card.setMinimumHeight(110)
        grid = QGridLayout(card)
        grid.setContentsMargins(16, 14, 16, 14)
        grid.setSpacing(10)

        actions = [
            ("New Workspace",   "plus",        "workspaces",  _ACCENT_BLUE),
            ("Open Workspace",  "folder-open", "_open_ws",    _ACCENT_BLUE),
            ("Import Images",   "import",      "_import_img", _ACCENT_GREEN),
            ("Generate Metadata","cpu",        "metadata",    _ACCENT_ORANGE),
            ("Open AI Studio",  "columns",     "ai_studio",   _ACCENT_PURPLE),
            ("Export Metadata", "export",      "export",      _ACCENT_GREEN),
        ]

        for idx, (label, icon, target, color) in enumerate(actions):
            btn = QuickActionButton(label, icon, color)
            if target == "_open_ws":
                btn.clicked.connect(self._action_open_workspace)
            elif target == "_import_img":
                btn.clicked.connect(self._action_import_images)
            else:
                btn.clicked.connect(lambda _, t=target: self.action_requested.emit(t))
            grid.addWidget(btn, idx // 3, idx % 3)

        self._main_layout.addWidget(card)

    def _build_stats_row(self) -> None:
        hdr = _section_header("Statistics Overview")
        self._main_layout.addLayout(hdr)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)

        ws_card = CardFrame()
        ws_col = QVBoxLayout(ws_card)
        ws_col.setContentsMargins(14, 12, 14, 12)
        ws_col.setSpacing(6)
        ws_col.addWidget(SectionLabel("Workspace Statistics"))
        ws_grid = QGridLayout()
        ws_grid.setSpacing(8)
        self._mc_total_ws    = MetricCard("Total Workspaces", "0", "folder", _ACCENT_BLUE)
        self._mc_active_ws   = MetricCard("Active",           "—", "folder-open", _ACCENT_GREEN)
        ws_grid.addWidget(self._mc_total_ws, 0, 0)
        ws_grid.addWidget(self._mc_active_ws, 0, 1)
        ws_col.addLayout(ws_grid)

        img_card = CardFrame()
        img_col = QVBoxLayout(img_card)
        img_col.setContentsMargins(14, 12, 14, 12)
        img_col.setSpacing(6)
        img_col.addWidget(SectionLabel("Image Statistics"))
        img_grid = QGridLayout()
        img_grid.setSpacing(8)
        self._mc_total_img   = MetricCard("Total Images",  "0", "image",  _ACCENT_BLUE)
        self._mc_img_size    = MetricCard("Total Size",    "0 MB", "folder", _ACCENT_PURPLE)
        self._mc_img_formats = MetricCard("Formats",       "0",  "edit",   _ACCENT_ORANGE)
        self._mc_img_pending = MetricCard("Pending AI",    "0",  "cpu",    _ACCENT_ORANGE)
        img_grid.addWidget(self._mc_total_img, 0, 0)
        img_grid.addWidget(self._mc_img_size, 0, 1)
        img_grid.addWidget(self._mc_img_formats, 1, 0)
        img_grid.addWidget(self._mc_img_pending, 1, 1)
        img_col.addLayout(img_grid)

        meta_card = CardFrame()
        meta_col = QVBoxLayout(meta_card)
        meta_col.setContentsMargins(14, 12, 14, 12)
        meta_col.setSpacing(6)
        meta_col.addWidget(SectionLabel("Metadata Statistics"))
        meta_grid = QGridLayout()
        meta_grid.setSpacing(8)
        self._mc_meta_generated = MetricCard("Generated",  "0", "edit",   _ACCENT_GREEN)
        self._mc_meta_pending   = MetricCard("Pending",    "0", "cpu",    _ACCENT_ORANGE)
        meta_grid.addWidget(self._mc_meta_generated, 0, 0)
        meta_grid.addWidget(self._mc_meta_pending, 0, 1)
        meta_col.addLayout(meta_grid)

        exp_card = CardFrame()
        exp_col = QVBoxLayout(exp_card)
        exp_col.setContentsMargins(14, 12, 14, 12)
        exp_col.setSpacing(6)
        exp_col.addWidget(SectionLabel("Export & Today's Activity"))
        exp_grid = QGridLayout()
        exp_grid.setSpacing(8)
        self._mc_exports_total  = MetricCard("Total Exports",    "0", "export",  _ACCENT_GREEN)
        self._mc_today_imported = MetricCard("Imported Today",   "0", "import",  _ACCENT_BLUE)
        self._mc_today_generated= MetricCard("Generated Today",  "0", "cpu",     _ACCENT_PURPLE)
        self._mc_today_exported = MetricCard("Exported Today",   "0", "export",  _ACCENT_GREEN)
        exp_grid.addWidget(self._mc_exports_total, 0, 0)
        exp_grid.addWidget(self._mc_today_imported, 0, 1)
        exp_grid.addWidget(self._mc_today_generated, 1, 0)
        exp_grid.addWidget(self._mc_today_exported, 1, 1)
        exp_col.addLayout(exp_grid)

        stats_row.addWidget(ws_card, 1)
        stats_row.addWidget(img_card, 2)
        stats_row.addWidget(meta_card, 1)
        stats_row.addWidget(exp_card, 2)
        self._main_layout.addLayout(stats_row)

    def _build_recent_row(self) -> None:
        hdr = _section_header("Recent Activity")
        self._main_layout.addLayout(hdr)

        row = QHBoxLayout()
        row.setSpacing(12)

        rw_card = self._make_list_card("Recent Workspaces", "workspaces")
        self._list_recent_ws = rw_card["list"]
        row.addWidget(rw_card["frame"], 1)

        ri_card = self._make_list_card("Recent Images", "images")
        self._list_recent_img = ri_card["list"]
        row.addWidget(ri_card["frame"], 1)

        rm_card = self._make_list_card("Recent Metadata", "metadata")
        self._list_recent_meta = rm_card["list"]
        row.addWidget(rm_card["frame"], 1)

        re_card = self._make_list_card("Recent Exports", "export")
        self._list_recent_export = re_card["list"]
        row.addWidget(re_card["frame"], 1)

        self._main_layout.addLayout(row)

    def _make_list_card(self, title: str, nav_target: str) -> dict:
        frame = CardFrame()
        frame.setMinimumHeight(200)
        col = QVBoxLayout(frame)
        col.setContentsMargins(14, 12, 14, 10)
        col.setSpacing(6)

        hdr_row = QHBoxLayout()
        hdr_row.addWidget(SectionLabel(title))
        hdr_row.addStretch()
        btn = QPushButton("View All")
        btn.setStyleSheet(
            f"QPushButton {{ color: {_ACCENT_BLUE}; background: transparent; border: none; "
            f"font-size: 10px; }} QPushButton:hover {{ color: palette(text); }}"
        )
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda _, t=nav_target: self.action_requested.emit(t))
        hdr_row.addWidget(btn)
        col.addLayout(hdr_row)

        lst = QListWidget()
        lst.setStyleSheet(f"""
            QListWidget {{
                background: transparent;
                border: none;
                color: palette(text);
                font-size: 12px;
            }}
            QListWidget::item {{
                padding: 5px 4px;
                border-bottom: 1px solid palette(alternate-base);
            }}
            QListWidget::item:hover {{
                background-color: palette(highlight);
                color: palette(highlighted-text);
                border-radius: 4px;
            }}
        """)
        lst.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        col.addWidget(lst)
        return {"frame": frame, "list": lst}

    def _build_bottom_row(self) -> None:
        row = QHBoxLayout()
        row.setSpacing(12)

        ai_frame = CardFrame()
        ai_frame.setMinimumHeight(180)
        ai_col = QVBoxLayout(ai_frame)
        ai_col.setContentsMargins(14, 12, 14, 12)
        ai_col.setSpacing(8)

        hdr_ai = QHBoxLayout()
        hdr_ai.addWidget(SectionLabel("AI Provider Status"))
        hdr_ai.addStretch()
        btn_ai_studio = QPushButton("AI Studio →")
        btn_ai_studio.setStyleSheet(
            f"QPushButton {{ color: {_ACCENT_BLUE}; background: transparent; border: none; "
            f"font-size: 10px; }} QPushButton:hover {{ color: palette(text); }}"
        )
        btn_ai_studio.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ai_studio.clicked.connect(lambda: self.action_requested.emit("ai_studio"))
        hdr_ai.addWidget(btn_ai_studio)
        ai_col.addLayout(hdr_ai)

        self._ai_providers_container = QVBoxLayout()
        self._ai_providers_container.setSpacing(4)
        ai_col.addLayout(self._ai_providers_container)
        ai_col.addStretch()
        row.addWidget(ai_frame, 1)

        log_frame = CardFrame()
        log_frame.setMinimumHeight(180)
        log_col = QVBoxLayout(log_frame)
        log_col.setContentsMargins(14, 12, 14, 12)
        log_col.setSpacing(6)

        hdr_log = QHBoxLayout()
        hdr_log.addWidget(SectionLabel("Recent Logs"))
        hdr_log.addStretch()
        btn_logs = QPushButton("View All →")
        btn_logs.setStyleSheet(
            f"QPushButton {{ color: {_ACCENT_BLUE}; background: transparent; border: none; "
            f"font-size: 10px; }} QPushButton:hover {{ color: palette(text); }}"
        )
        btn_logs.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logs.clicked.connect(lambda: self.action_requested.emit("logs"))
        hdr_log.addWidget(btn_logs)
        log_col.addLayout(hdr_log)

        self._logs_container = QVBoxLayout()
        self._logs_container.setSpacing(2)
        log_col.addLayout(self._logs_container)
        log_col.addStretch()
        row.addWidget(log_frame, 2)

        self._main_layout.addLayout(row)

    def _connect_events(self) -> None:
        if not self.container:
            return
        eb = self.container.get_service("event_bus")
        if not eb:
            return
        eb.subscribe(AppConstants.EVENT_WORKSPACE_LOADED, self._on_workspace_event)
        eb.subscribe(WorkspaceEvents.RECENT_UPDATED,      self._on_workspace_event)
        eb.subscribe(WorkspaceEvents.CREATED,             self._on_workspace_event)
        eb.subscribe(WorkspaceEvents.LOADED,              self._on_workspace_event)
        eb.subscribe(WorkspaceEvents.CLOSED,              self._on_workspace_event)
        eb.subscribe(ImageEvents.INDEXED,                 self._on_image_event)
        eb.subscribe(ImageEvents.SCAN_COMPLETED,          self._on_image_event)
        eb.subscribe(ImageEvents.IMPORTED,                self._on_image_event)

    def _on_workspace_event(self, payload=None) -> None:
        self._refresh_state()

    def _on_image_event(self, payload=None) -> None:
        self._refresh_image_stats()

    def showEvent(self, event) -> None:
        self._refresh_state()
        super().showEvent(event)

    def _refresh_state(self) -> None:
        try:
            self._refresh_banner()
            self._refresh_workspace_stats()
            self._refresh_image_stats()
            self._refresh_metadata_stats()
            self._refresh_export_stats()
            self._refresh_today_activity()
            self._refresh_recent_workspaces()
            self._refresh_recent_images()
            self._refresh_recent_metadata()
            self._refresh_recent_exports()
            self._refresh_ai_providers()
            self._refresh_logs()
        except Exception as e:
            logger.error(f"DashboardPage._refresh_state error: {e}", exc_info=True)

    def _refresh_banner(self) -> None:
        hour = datetime.now().hour
        if hour < 12:
            greeting = "Good Morning"
        elif hour < 17:
            greeting = "Good Afternoon"
        else:
            greeting = "Good Evening"

        wm = self._get_service("workspace_manager")
        if wm and wm.active_workspace:
            ws = wm.active_workspace
            self._lbl_greeting.setText(f"{greeting} — {ws.name}")
            im = self._get_service("image_manager")
            count = len(im.repository.get_all()) if im and im.repository else 0
            meta_count = self._count_metadata_files(ws)
            self._lbl_ws_info.setText(
                f"Marketplace: {ws.marketplace_profile}  ·  "
                f"Images: {count}  ·  Metadata: {meta_count}  ·  "
                f"Status: {ws.status}"
            )
            self._lbl_ws_path.setText(ws.root_path)
            self._lbl_ws_path.show()
        else:
            self._lbl_greeting.setText(f"{greeting} — StockPilot AI")
            self._lbl_ws_info.setText("No workspace open. Create or open one to get started.")
            self._lbl_ws_path.hide()

    def _refresh_workspace_stats(self) -> None:
        wm = self._get_service("workspace_manager")
        if not wm:
            return
        recent = wm.get_recent_workspaces()
        self._mc_total_ws.set_value(str(len(recent)))
        if wm.active_workspace:
            self._mc_active_ws.set_value(wm.active_workspace.name[:18])
        else:
            self._mc_active_ws.set_value("None")

    def _refresh_image_stats(self) -> None:
        im = self._get_service("image_manager")
        if not im or not im.repository:
            self._mc_total_img.set_value("0")
            self._mc_img_size.set_value("0 MB")
            self._mc_img_formats.set_value("0")
            self._mc_img_pending.set_value("0")
            return

        images = im.repository.get_all()
        total = len(images)
        total_bytes = sum(img.file_size_bytes for img in images)
        total_mb = round(total_bytes / (1024 * 1024), 1) if total_bytes else 0
        formats = len({img.format for img in images if img.format})
        pending = sum(1 for img in images if img.status == "Pending")

        self._mc_total_img.set_value(str(total))
        self._mc_img_size.set_value(
            f"{total_mb} MB" if total_mb < 1024 else f"{round(total_mb/1024, 1)} GB"
        )
        self._mc_img_formats.set_value(str(formats))
        self._mc_img_pending.set_value(str(pending))

    def _refresh_metadata_stats(self) -> None:
        wm = self._get_service("workspace_manager")
        im = self._get_service("image_manager")

        if not wm or not wm.active_workspace or not im or not im.repository:
            self._mc_meta_generated.set_value("0")
            self._mc_meta_pending.set_value("0")
            return

        images = im.repository.get_all()
        generated = sum(1 for img in images if img.status not in ("Pending", "Error"))
        pending = sum(1 for img in images if img.status == "Pending")
        self._mc_meta_generated.set_value(str(generated))
        self._mc_meta_pending.set_value(str(pending))

    def _refresh_export_stats(self) -> None:
        exports_dir = AppConstants.EXPORTS_DIR
        total = 0
        if exports_dir.exists():
            total = sum(1 for f in exports_dir.rglob("*") if f.is_file())
        self._mc_exports_total.set_value(str(total))

    def _refresh_today_activity(self) -> None:
        today_str = date.today().isoformat()
        im = self._get_service("image_manager")
        imported_today = 0
        generated_today = 0
        if im and im.repository:
            images = im.repository.get_all()
            for img in images:
                try:
                    if img.imported_date and img.imported_date[:10] == today_str:
                        imported_today += 1
                    if img.modified_date and img.modified_date[:10] == today_str and img.status not in ("Pending",):
                        generated_today += 1
                except Exception:
                    pass

        exports_dir = AppConstants.EXPORTS_DIR
        exported_today = 0
        if exports_dir.exists():
            for f in exports_dir.rglob("*"):
                if f.is_file():
                    try:
                        mtime = date.fromtimestamp(f.stat().st_mtime).isoformat()
                        if mtime == today_str:
                            exported_today += 1
                    except Exception:
                        pass

        self._mc_today_imported.set_value(str(imported_today))
        self._mc_today_generated.set_value(str(generated_today))
        self._mc_today_exported.set_value(str(exported_today))

    def _refresh_recent_workspaces(self) -> None:
        self._list_recent_ws.clear()
        wm = self._get_service("workspace_manager")
        if not wm:
            self._list_empty(self._list_recent_ws, "No workspace manager")
            return
        recent = wm.get_recent_workspaces()
        recent.sort(key=lambda x: str(x.get("last_opened", "")), reverse=True)
        if not recent:
            self._list_empty(self._list_recent_ws, "No recent workspaces")
            return
        for ws in recent[:8]:
            name = ws.get("name", "Unknown")
            item = QListWidgetItem(name)
            item.setToolTip(ws.get("path", ""))
            self._list_recent_ws.addItem(item)
            item.setData(Qt.ItemDataRole.UserRole, ws.get("path", ""))

        self._list_recent_ws.itemClicked.connect(self._on_recent_ws_clicked)

    def _refresh_recent_images(self) -> None:
        self._list_recent_img.clear()
        im = self._get_service("image_manager")
        if not im or not im.repository:
            self._list_empty(self._list_recent_img, "No workspace open")
            return
        images = im.repository.get_all()
        if not images:
            self._list_empty(self._list_recent_img, "No images indexed")
            return
        try:
            images.sort(key=lambda x: str(x.imported_date or ""), reverse=True)
        except Exception:
            pass
        for img in images[:8]:
            size_kb = round(img.file_size_bytes / 1024, 0) if img.file_size_bytes else 0
            label = f"{img.filename}  ({img.format}, {size_kb} KB)"
            item = QListWidgetItem(label)
            item.setToolTip(img.absolute_path)
            self._list_recent_img.addItem(item)

    def _refresh_recent_metadata(self) -> None:
        self._list_recent_meta.clear()
        im = self._get_service("image_manager")
        wm = self._get_service("workspace_manager")
        if not im or not im.repository or not wm or not wm.active_workspace:
            self._list_empty(self._list_recent_meta, "No workspace open")
            return
        images = im.repository.get_all()
        done = [img for img in images if img.status not in ("Pending", "Error")]
        if not done:
            self._list_empty(self._list_recent_meta, "No metadata generated yet")
            return
        try:
            done.sort(key=lambda x: str(x.modified_date or ""), reverse=True)
        except Exception:
            pass
        for img in done[:8]:
            item = QListWidgetItem(img.filename)
            item.setToolTip(f"Status: {img.status}")
            self._list_recent_meta.addItem(item)

    def _refresh_recent_exports(self) -> None:
        self._list_recent_export.clear()
        exports_dir = AppConstants.EXPORTS_DIR
        if not exports_dir.exists():
            self._list_empty(self._list_recent_export, "No exports yet")
            return
        files = sorted(
            (f for f in exports_dir.rglob("*") if f.is_file()),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )
        if not files:
            self._list_empty(self._list_recent_export, "No export files found")
            return
        for f in files[:8]:
            size_kb = round(f.stat().st_size / 1024, 0)
            item = QListWidgetItem(f"{f.name}  ({size_kb} KB)")
            item.setToolTip(str(f))
            self._list_recent_export.addItem(item)

    def _refresh_ai_providers(self) -> None:
        while self._ai_providers_container.count():
            item = self._ai_providers_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        config_manager = self._get_service("config_manager")
        if not config_manager:
            self._ai_providers_container.addWidget(QLabel("Config manager unavailable"))
            return

        providers = [
            ("OpenAI",       "openai_api_key"),
            ("Gemini",       "gemini_api_key"),
            ("Groq",         "groq_api_key"),
            ("DeepSeek",     "deepseek_api_key"),
            ("OpenRouter",   "openrouter_api_key"),
        ]

        found_any = False
        for name, key in providers:
            api_key = config_manager.get(key, "")
            is_configured = bool(api_key and api_key.strip())
            row_widget = QWidget()
            row_widget.setStyleSheet("background: transparent;")
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 2, 0, 2)
            row_layout.setSpacing(8)

            dot = StatusDot(is_configured)
            lbl_name = QLabel(name)
            lbl_name.setStyleSheet(f"color: palette(text); font-size: 12px;")
            lbl_status = QLabel("Configured" if is_configured else "Not configured")
            lbl_status.setStyleSheet(
                f"color: {_ACCENT_GREEN if is_configured else _TEXT_MUTED}; font-size: 11px;"
            )
            lbl_status.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            row_layout.addWidget(dot)
            row_layout.addWidget(lbl_name)
            row_layout.addStretch()
            row_layout.addWidget(lbl_status)
            self._ai_providers_container.addWidget(row_widget)
            found_any = True

        if not found_any:
            lbl = QLabel("No providers configured")
            lbl.setStyleSheet(f"color: {_TEXT_MUTED}; font-size: 12px;")
            self._ai_providers_container.addWidget(lbl)

        btn_cfg = QPushButton("Configure Providers →")
        btn_cfg.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cfg.setStyleSheet(
            f"QPushButton {{ color: {_ACCENT_BLUE}; background: transparent; border: none; "
            f"font-size: 11px; text-align: left; }} QPushButton:hover {{ color: palette(text); }}"
        )
        btn_cfg.clicked.connect(lambda: self.action_requested.emit("settings"))
        self._ai_providers_container.addWidget(btn_cfg)

    def _refresh_logs(self) -> None:
        while self._logs_container.count():
            item = self._logs_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        log_entries = self._read_recent_log_lines(max_lines=10)
        if not log_entries:
            lbl = QLabel("No log entries found")
            lbl.setStyleSheet(f"color: {_TEXT_MUTED}; font-size: 11px;")
            self._logs_container.addWidget(lbl)
            return

        for level, message, timestamp in log_entries:
            row = LogRow(level, message, timestamp)
            self._logs_container.addWidget(row)

    def _read_recent_log_lines(self, max_lines: int = 10) -> List[Tuple[str, str, str]]:
        entries = []
        logs_dir = AppConstants.LOGS_DIR
        if not logs_dir.exists():
            return entries

        log_files = sorted(
            (f for f in logs_dir.glob("*.log") if f.is_file()),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )
        if not log_files:
            return entries

        try:
            with open(log_files[0], "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except Exception:
            return entries

        recent = [l.strip() for l in reversed(lines) if l.strip()][:max_lines]
        for line in recent:
            try:
                level = "INFO"
                timestamp = ""
                message = line
                if "[ERROR]" in line or " ERROR " in line:
                    level = "ERROR"
                elif "[WARNING]" in line or " WARNING " in line:
                    level = "WARNING"
                elif "[DEBUG]" in line or " DEBUG " in line:
                    level = "DEBUG"

                if len(line) > 23 and line[4] == "-":
                    timestamp = line[:19]
                    message = line[24:].strip() if len(line) > 24 else line

                if len(message) > 80:
                    message = message[:77] + "..."

                entries.append((level, message, timestamp))
            except Exception:
                continue

        return entries

    def _action_open_workspace(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Open Workspace Directory")
        if folder and self.container:
            wm = self._get_service("workspace_manager")
            if wm:
                if not wm.load_workspace(folder):
                    QMessageBox.critical(self, "Error",
                        f"Could not load workspace at:\n{folder}\n\n"
                        "Make sure it is a valid StockPilot workspace directory.")
                else:
                    self._refresh_state()

    def _action_import_images(self) -> None:
        if not self.container:
            return
        wm = self._get_service("workspace_manager")
        if not wm or not wm.active_workspace:
            QMessageBox.warning(self, "No Active Workspace",
                "Please open or create a workspace before importing images.")
            return
        files, _ = QFileDialog.getOpenFileNames(
            self, "Import Images", "",
            "Image Files (*.png *.jpg *.jpeg *.webp *.tiff *.bmp)"
        )
        if files:
            im = self._get_service("image_manager")
            if im:
                im.import_files([Path(f) for f in files])
                self.action_requested.emit("images")

    def _on_recent_ws_clicked(self, item: QListWidgetItem) -> None:
        path = item.data(Qt.ItemDataRole.UserRole)
        if not path or not self.container:
            return
        wm = self._get_service("workspace_manager")
        if wm:
            if wm.load_workspace(path):
                self._refresh_state()
            else:
                QMessageBox.warning(self, "Load Failed",
                    f"Could not open workspace:\n{path}")

    def _get_service(self, name: str) -> Any:
        if not self.container:
            return None
        return self.container.get_service(name)

    @staticmethod
    def _list_empty(lst: QListWidget, text: str) -> None:
        item = QListWidgetItem(text)
        item.setFlags(Qt.ItemFlag.NoItemFlags)
        item.setForeground(QColor(_TEXT_MUTED))
        lst.addItem(item)

    @staticmethod
    def _count_metadata_files(ws: Any) -> int:
        try:
            meta_dir = Path(ws.root_path) / "metadata"
            if meta_dir.exists():
                return sum(1 for f in meta_dir.rglob("*.json") if f.is_file())
        except Exception:
            pass
        return 0
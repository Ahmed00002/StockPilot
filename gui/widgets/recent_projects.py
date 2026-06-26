# gui/widgets/recent_projects.py
from typing import Dict, Any, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem, 
    QLabel, QHBoxLayout, QPushButton, QFrame
)
from PySide6.QtCore import Qt, Signal
from gui.widgets.icon_loader import IconLoader
from workspace.workspace_events import WorkspaceEvents

class RecentProjectsWidget(QFrame):
    """Widget displaying recently accessed workspaces bound to backend storage."""
    
    action_requested = Signal(str)
    
    def __init__(self, container=None, parent=None):
        super().__init__(parent)
        self.container = container
        self.setObjectName("RecentProjects")
        self.setStyleSheet("""
            #RecentProjects {
                background-color: #252526;
                border: 1px solid #3f3f46;
                border-radius: 6px;
            }
            QLabel { font-size: 14px; font-weight: bold; }
            QListWidget { background-color: transparent; border: none; }
            QListWidget::item { padding: 8px; border-bottom: 1px solid #3f3f46; }
            QListWidget::item:hover { background-color: #2d2d30; }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Recent Projects"))
        btn_new = QPushButton(IconLoader.get_icon("plus"), "New")
        btn_new.clicked.connect(lambda: self.action_requested.emit("workspaces"))
        header_layout.addWidget(btn_new, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addLayout(header_layout)
        
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.list_widget)
        
        self._subscribe_events()
        self._load_data()

    def _subscribe_events(self) -> None:
        if self.container:
            eb = self.container.get_service("event_bus")
            if eb:
                eb.subscribe(WorkspaceEvents.RECENT_UPDATED, self._on_recent_updated)

    def _on_recent_updated(self, payload=None) -> None:
        self._load_data()

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        path = item.data(Qt.ItemDataRole.UserRole)
        if not path or not self.container: return
        wm = self.container.get_service("workspace_manager")
        if wm and wm.load_workspace(path):
            self.action_requested.emit("dashboard")

    def _load_data(self) -> None:
        """Fetches data from WorkspaceManager and populates the list."""
        self.list_widget.clear()
        
        if not self.container:
            self._add_item("Service Unreachable", "Error", "0", "N/A", False, "")
            return

        workspace_manager = self.container.get_service("workspace_manager")
        if not workspace_manager:
            self._add_item("Backend Offline", "Error", "0", "N/A", False, "")
            return

        recent_workspaces: List[Dict[str, Any]] = workspace_manager.get_recent_workspaces()
        
        if not recent_workspaces:
            # Placeholder for empty state
            item = QListWidgetItem("No recent workspaces found.")
            item.setFlags(Qt.ItemFlag.NoItemFlags) # Make it unclickable
            self.list_widget.addItem(item)
            return
            
        # FIX: String cast required to prevent TypeError when comparing ISO date strings to integers
        recent_workspaces.sort(key=lambda x: str(x.get('last_opened', '')), reverse=True)
        
        for ws in recent_workspaces[:10]: # Max 10 items
            name = ws.get("name", "Unknown Workspace")
            market = ws.get("marketplace", "Unassigned")
            pinned = ws.get("is_pinned", False)
            path = ws.get("path", "")
            
            raw_time = ws.get("last_opened", "")
            time_str = "Recently"
            if raw_time:
                try:
                    time_str = raw_time.split("T")[0]
                except Exception:
                    pass
                    
            self._add_item(name, market, "View Details", time_str, pinned, path)

    def _add_item(self, name: str, market: str, count: str, time_str: str, pinned: bool, path: str) -> None:
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, path)
        
        widget = QWidget()
        w_layout = QHBoxLayout(widget)
        w_layout.setContentsMargins(0, 0, 0, 0)
        
        pin_icon = "star" if pinned else "folder"
        w_layout.addWidget(QLabel(text="", pixmap=IconLoader.get_icon(pin_icon).pixmap(16, 16)))
        
        info_layout = QVBoxLayout()
        lbl_name = QLabel(name)
        lbl_name.setStyleSheet("font-weight: bold; font-size: 13px;")
        
        lbl_meta = QLabel(f"{market} • {time_str}")
        lbl_meta.setStyleSheet("color: #858585; font-size: 11px;")
        info_layout.addWidget(lbl_name)
        info_layout.addWidget(lbl_meta)
        
        w_layout.addLayout(info_layout)
        w_layout.addStretch()
        
        item.setSizeHint(widget.sizeHint())
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, widget)
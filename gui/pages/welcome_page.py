# gui/pages/welcome_page.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from core.constants import AppConstants
from gui.widgets.recent_projects import RecentProjectsWidget
from gui.widgets.quick_actions import QuickActionsWidget

class WelcomePage(QWidget):
    """The default landing page providing quick starts and recent history."""

    action_requested = Signal(str)
    
    def __init__(self, container=None, parent=None):
        super().__init__(parent)
        self.container = container
        self.setObjectName("WelcomePage")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)
        
        # Header
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title = QLabel(AppConstants.APP_NAME)
        lbl_title.setStyleSheet("font-size: 32px; font-weight: bold; color: #ffffff;")
        lbl_subtitle = QLabel("Professional Metadata Assistant")
        lbl_subtitle.setStyleSheet("font-size: 16px; color: #858585;")
        
        header_layout.addWidget(lbl_title, alignment=Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(lbl_subtitle, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(header_layout)
        
        # Content Split
        content_layout = QHBoxLayout()
        content_layout.setSpacing(40)
        
        # Left Side (Quick Actions)
        left_layout = QVBoxLayout()
        quick_actions = QuickActionsWidget()
        quick_actions.action_requested.connect(self.action_requested.emit)
        left_layout.addWidget(quick_actions)
        left_layout.addStretch()
        content_layout.addLayout(left_layout, 1)
        
        # Right Side (Recent Projects - Now dynamically bound)
        right_layout = QVBoxLayout()
        self.recent_projects = RecentProjectsWidget(container=self.container)
        self.recent_projects.action_requested.connect(self.action_requested.emit)
        right_layout.addWidget(self.recent_projects)
        content_layout.addLayout(right_layout, 1)
        
        main_layout.addLayout(content_layout)
        main_layout.addStretch()
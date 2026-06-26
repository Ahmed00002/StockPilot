# gui/pages/metadata_page.py
import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget, 
    QLineEdit, QComboBox, QLabel, QPushButton, QToolBar, 
    QTabWidget, QTextEdit, QCheckBox, QFormLayout, QProgressBar,
    QScrollArea, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QAction, QIcon

class MetadataPage(QWidget):
    """
    Metadata Studio page providing comprehensive tools for viewing, editing,
    and generating image metadata.
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
            
        self.event_bus = self.container.get_service("event_bus")
        self.image_manager = self.container.get_service("image_manager")
        self.workspace_manager = self.container.get_service("workspace_manager")
        self.metadata_manager = self.container.get_service("metadata_manager")

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self._create_toolbar()

        # Main vertical splitter (Top: Panels, Bottom: Tabs)
        self.v_splitter = QSplitter(Qt.Vertical)
        
        # Horizontal splitter for Top Panels
        self.h_splitter = QSplitter(Qt.Horizontal)
        
        self._create_left_panel()
        self._create_center_panel()
        self._create_right_panel()
        
        self.h_splitter.addWidget(self.left_panel)
        self.h_splitter.addWidget(self.center_panel)
        self.h_splitter.addWidget(self.right_panel)
        self.h_splitter.setSizes([250, 600, 250])
        
        self._create_bottom_tabs()
        
        self.v_splitter.addWidget(self.h_splitter)
        self.v_splitter.addWidget(self.bottom_tabs_widget)
        self.v_splitter.setSizes([700, 200])
        
        self.main_layout.addWidget(self.v_splitter)

    def _create_toolbar(self):
        self.toolbar = QToolBar("Metadata Toolbar", self)
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(16, 16))
        
        self.act_generate = QAction("Generate Metadata", self)
        self.act_improve = QAction("Improve", self)
        self.act_regenerate = QAction("Regenerate", self)
        self.act_save = QAction("Save", self)
        self.act_reset = QAction("Reset", self)
        self.act_review = QAction("Review", self)
        
        self.toolbar.addAction(self.act_generate)
        self.toolbar.addAction(self.act_improve)
        self.toolbar.addAction(self.act_regenerate)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.act_save)
        self.toolbar.addAction(self.act_reset)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.act_review)
        
        self.main_layout.addWidget(self.toolbar)

    def _create_left_panel(self):
        self.left_panel = QWidget()
        layout = QVBoxLayout(self.left_panel)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Search & Filter
        search_filter_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search images...")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Needs Metadata", "Reviewed", "Approved"])
        search_filter_layout.addWidget(self.search_input)
        search_filter_layout.addWidget(self.filter_combo)
        layout.addLayout(search_filter_layout)
        
        # Image List (Thumbnails)
        self.image_list = QListWidget()
        self.image_list.setViewMode(QListWidget.IconMode)
        self.image_list.setIconSize(QSize(100, 100))
        self.image_list.setResizeMode(QListWidget.Adjust)
        self.image_list.setSpacing(5)
        layout.addWidget(self.image_list)
        
        # Status
        self.lbl_list_status = QLabel("0 Images loaded")
        self.lbl_list_status.setStyleSheet("color: gray;")
        layout.addWidget(self.lbl_list_status)

    def _create_center_panel(self):
        self.center_panel = QScrollArea()
        self.center_panel.setWidgetResizable(True)
        self.center_panel.setFrameShape(QFrame.NoFrame)
        
        container = QWidget()
        layout = QFormLayout(container)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        self.title_editor = QLineEdit()
        self.title_editor.setPlaceholderText("Enter image title...")
        
        self.desc_editor = QTextEdit()
        self.desc_editor.setPlaceholderText("Enter image description...")
        self.desc_editor.setMaximumHeight(100)
        
        self.keywords_editor = QTextEdit()
        self.keywords_editor.setPlaceholderText("Enter keywords, comma separated...")
        self.keywords_editor.setMaximumHeight(150)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Select Category...", "Nature", "Technology", "People", "Business", "Abstract"])
        
        self.concepts_editor = QLineEdit()
        self.concepts_editor.setPlaceholderText("Enter core concepts...")
        
        self.chk_commercial = QCheckBox("Commercial Use Allowed")
        self.chk_editorial = QCheckBox("Editorial Only")
        
        toggles_layout = QHBoxLayout()
        toggles_layout.addWidget(self.chk_commercial)
        toggles_layout.addWidget(self.chk_editorial)
        toggles_layout.addStretch()
        
        layout.addRow(QLabel("<b>Title:</b>"), self.title_editor)
        layout.addRow(QLabel("<b>Description:</b>"), self.desc_editor)
        layout.addRow(QLabel("<b>Keywords:</b>"), self.keywords_editor)
        layout.addRow(QLabel("<b>Category:</b>"), self.category_combo)
        layout.addRow(QLabel("<b>Concepts:</b>"), self.concepts_editor)
        layout.addRow(QLabel("<b>Usage Rights:</b>"), toggles_layout)
        
        self.center_panel.setWidget(container)

    def _create_right_panel(self):
        self.right_panel = QWidget()
        layout = QVBoxLayout(self.right_panel)
        layout.setContentsMargins(10, 15, 10, 15)
        layout.setSpacing(15)
        
        title_lbl = QLabel("<b>Validation & Scores</b>")
        layout.addWidget(title_lbl)
        
        form_layout = QFormLayout()
        form_layout.setContentsMargins(0, 0, 0, 0)
        
        self.score_metadata = QProgressBar()
        self.score_metadata.setRange(0, 100)
        self.score_metadata.setValue(0)
        
        self.score_seo = QProgressBar()
        self.score_seo.setRange(0, 100)
        self.score_seo.setValue(0)
        
        self.lbl_adobe_valid = QLabel("Pending")
        self.lbl_keyword_count = QLabel("0")
        self.lbl_char_count = QLabel("0 / 200")
        self.lbl_ai_status = QLabel("Idle")
        
        form_layout.addRow("Metadata Score:", self.score_metadata)
        form_layout.addRow("SEO Score:", self.score_seo)
        form_layout.addRow("Adobe Validation:", self.lbl_adobe_valid)
        form_layout.addRow("Keyword Count:", self.lbl_keyword_count)
        form_layout.addRow("Title Chars:", self.lbl_char_count)
        form_layout.addRow("AI Status:", self.lbl_ai_status)
        
        layout.addLayout(form_layout)
        layout.addStretch()

    def _create_bottom_tabs(self):
        self.bottom_tabs_widget = QWidget()
        layout = QVBoxLayout(self.bottom_tabs_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = QTabWidget()
        
        self.tab_review = QTextEdit()
        self.tab_review.setReadOnly(True)
        self.tab_review.setPlaceholderText("Compliance and quality review insights will appear here...")
        
        self.tab_history = QListWidget()
        
        self.tab_versions = QListWidget()
        
        self.tab_logs = QTextEdit()
        self.tab_logs.setReadOnly(True)
        
        self.tabs.addTab(self.tab_review, "Review")
        self.tabs.addTab(self.tab_history, "History")
        self.tabs.addTab(self.tab_versions, "Versions")
        self.tabs.addTab(self.tab_logs, "Logs")
        
        layout.addWidget(self.tabs)

    def _connect_signals(self):
        self.act_generate.triggered.connect(self._on_generate)
        self.act_improve.triggered.connect(self._on_improve)
        self.act_regenerate.triggered.connect(self._on_regenerate)
        self.act_save.triggered.connect(self._on_save)
        self.act_reset.triggered.connect(self._on_reset)
        self.act_review.triggered.connect(self._on_review)
        
        self.image_list.itemSelectionChanged.connect(self._on_image_selected)
        
        self.title_editor.textChanged.connect(self._update_character_count)
        self.keywords_editor.textChanged.connect(self._update_keyword_count)

    def _on_generate(self):
        self._log("Initiating metadata generation...")
        self.lbl_ai_status.setText("Generating...")

    def _on_improve(self):
        self._log("Improving current metadata...")
        self.lbl_ai_status.setText("Improving...")

    def _on_regenerate(self):
        self._log("Regenerating metadata...")
        self.lbl_ai_status.setText("Regenerating...")

    def _on_save(self):
        self._log("Saving metadata changes...")

    def _on_reset(self):
        self._log("Resetting metadata to last saved state...")

    def _on_review(self):
        self._log("Running compliance review...")
        self.tabs.setCurrentIndex(0)

    def _on_image_selected(self):
        items = self.image_list.selectedItems()
        if items:
            self._log(f"Selected image: {items[0].text()}")

    def _update_character_count(self):
        text_length = len(self.title_editor.text())
        self.lbl_char_count.setText(f"{text_length} / 200")

    def _update_keyword_count(self):
        text = self.keywords_editor.toPlainText()
        if not text.strip():
            self.lbl_keyword_count.setText("0")
            return
        keywords = [k.strip() for k in text.split(",") if k.strip()]
        self.lbl_keyword_count.setText(str(len(keywords)))

    def _log(self, message: str):
        self.logger.info(message)
        self.tab_logs.append(message)
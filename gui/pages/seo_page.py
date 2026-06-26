# gui/pages/seo_page.py
import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTableWidget, 
    QTableWidgetItem, QHeaderView, QLabel, QToolBar, QTextEdit, 
    QProgressBar, QFormLayout, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QAction, QFont, QColor

class SEOPage(QWidget):
    """
    SEO Engine Page.
    Provides comprehensive SEO analysis, marketplace scoring, keyword density,
    buyer intent evaluation, and optimization tools for image metadata.
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
            
        self.seo_manager = self.container.get_service("seo_manager")
        self.metadata_manager = self.container.get_service("metadata_manager")
        self.event_bus = self.container.get_service("event_bus")

        self._init_ui()
        self._connect_signals()
        self._load_initial_state()

    def _init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self._create_toolbar()

        # Main vertical splitter (Top: Dashboard, Bottom: Feedback)
        self.v_splitter = QSplitter(Qt.Vertical)
        
        # Horizontal splitter for Top Dashboard (Left: Scores, Right: Keywords)
        self.h_splitter = QSplitter(Qt.Horizontal)
        
        self._create_scores_panel()
        self._create_keywords_panel()
        
        self.h_splitter.addWidget(self.scores_panel)
        self.h_splitter.addWidget(self.keywords_panel)
        self.h_splitter.setSizes([350, 650])
        
        self._create_feedback_panel()
        
        self.v_splitter.addWidget(self.h_splitter)
        self.v_splitter.addWidget(self.feedback_panel)
        self.v_splitter.setSizes([600, 200])
        
        self.main_layout.addWidget(self.v_splitter)

    def _create_toolbar(self):
        self.toolbar = QToolBar("SEO Toolbar", self)
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(16, 16))
        
        self.act_optimize = QAction("Optimize", self)
        self.act_optimize.setToolTip("Auto-optimize metadata for maximum SEO reach")
        
        self.act_review = QAction("Review", self)
        self.act_review.setToolTip("Run SEO compliance and intent review")
        
        self.toolbar.addAction(self.act_optimize)
        self.toolbar.addAction(self.act_review)
        
        self.main_layout.addWidget(self.toolbar)

    def _create_scores_panel(self):
        self.scores_panel = QScrollArea()
        self.scores_panel.setWidgetResizable(True)
        self.scores_panel.setFrameShape(QFrame.NoFrame)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)
        
        lbl_title = QLabel("<b>SEO & Performance Scores</b>")
        lbl_title.setFont(QFont("Arial", 11))
        layout.addWidget(lbl_title)
        
        # Form for progress bars
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        self.bar_seo = self._create_progress_bar("SEO Score")
        self.bar_commercial = self._create_progress_bar("Commercial Score")
        self.bar_adobe = self._create_progress_bar("Adobe Stock Score")
        self.bar_shutterstock = self._create_progress_bar("Shutterstock Score")
        self.bar_freepik = self._create_progress_bar("Freepik Score")
        
        form_layout.addRow("<b>Global SEO:</b>", self.bar_seo)
        form_layout.addRow("<b>Commercial Viability:</b>", self.bar_commercial)
        form_layout.addRow("<hr>", QLabel("<hr>"))
        form_layout.addRow("<b>Adobe Stock:</b>", self.bar_adobe)
        form_layout.addRow("<b>Shutterstock:</b>", self.bar_shutterstock)
        form_layout.addRow("<b>Freepik:</b>", self.bar_freepik)
        
        layout.addLayout(form_layout)
        
        # Buyer Intent Frame
        intent_frame = QFrame()
        intent_frame.setStyleSheet("QFrame { background-color: rgba(43, 87, 154, 0.1); border-left: 3px solid #2b579a; padding: 10px; }")
        intent_layout = QVBoxLayout(intent_frame)
        intent_layout.setContentsMargins(10, 10, 10, 10)
        
        intent_layout.addWidget(QLabel("<b>Primary Buyer Intent</b>"))
        self.lbl_buyer_intent = QLabel("Pending Analysis...")
        self.lbl_buyer_intent.setFont(QFont("Arial", 10, QFont.Bold))
        intent_layout.addWidget(self.lbl_buyer_intent)
        
        layout.addWidget(intent_frame)
        layout.addStretch()
        
        self.scores_panel.setWidget(container)

    def _create_progress_bar(self, tooltip: str) -> QProgressBar:
        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(0)
        bar.setTextVisible(True)
        bar.setToolTip(tooltip)
        return bar

    def _create_keywords_panel(self):
        self.keywords_panel = QWidget()
        layout = QVBoxLayout(self.keywords_panel)
        layout.setContentsMargins(10, 10, 10, 10)
        
        tables_layout = QHBoxLayout()
        
        # Keyword Density Table
        density_container = QWidget()
        density_layout = QVBoxLayout(density_container)
        density_layout.setContentsMargins(0, 0, 0, 0)
        density_layout.addWidget(QLabel("<b>Keyword Density</b>"))
        
        self.table_density = QTableWidget(0, 3)
        self.table_density.setHorizontalHeaderLabels(["Keyword", "Count", "Density %"])
        self.table_density.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_density.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table_density.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        density_layout.addWidget(self.table_density)
        
        # Keyword Ranking Table
        ranking_container = QWidget()
        ranking_layout = QVBoxLayout(ranking_container)
        ranking_layout.setContentsMargins(0, 0, 0, 0)
        ranking_layout.addWidget(QLabel("<b>Keyword Ranking & Trends</b>"))
        
        self.table_ranking = QTableWidget(0, 3)
        self.table_ranking.setHorizontalHeaderLabels(["Keyword", "Global Rank", "Competition"])
        self.table_ranking.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_ranking.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table_ranking.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        ranking_layout.addWidget(self.table_ranking)
        
        tables_layout.addWidget(density_container)
        tables_layout.addWidget(ranking_container)
        layout.addLayout(tables_layout)

    def _create_feedback_panel(self):
        self.feedback_panel = QWidget()
        layout = QHBoxLayout(self.feedback_panel)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Suggestions
        sugg_container = QWidget()
        sugg_layout = QVBoxLayout(sugg_container)
        sugg_layout.setContentsMargins(0, 0, 0, 0)
        sugg_layout.addWidget(QLabel("<b>Optimization Suggestions</b>"))
        self.txt_suggestions = QTextEdit()
        self.txt_suggestions.setReadOnly(True)
        self.txt_suggestions.setStyleSheet("background-color: rgba(46, 107, 60, 0.05); border: 1px solid #2e6b3c;")
        sugg_layout.addWidget(self.txt_suggestions)
        
        # Warnings
        warn_container = QWidget()
        warn_layout = QVBoxLayout(warn_container)
        warn_layout.setContentsMargins(0, 0, 0, 0)
        warn_layout.addWidget(QLabel("<b>Critical Warnings</b>"))
        self.txt_warnings = QTextEdit()
        self.txt_warnings.setReadOnly(True)
        self.txt_warnings.setStyleSheet("background-color: rgba(163, 50, 50, 0.05); border: 1px solid #a33232; color: #ff6b6b;")
        warn_layout.addWidget(self.txt_warnings)
        
        layout.addWidget(sugg_container)
        layout.addWidget(warn_container)

    def _connect_signals(self):
        self.act_optimize.triggered.connect(self._on_optimize)
        self.act_review.triggered.connect(self._on_review)

    def _load_initial_state(self):
        self.txt_suggestions.setPlainText("Run an SEO review to generate actionable suggestions for title and keywords.")
        self.txt_warnings.setPlainText("No active warnings.")

    def _on_optimize(self):
        self.logger.info("Triggering SEO optimization routine.")
        self.txt_suggestions.setPlainText("Optimizing keywords based on marketplace algorithms...\nReordering keywords by commercial weight...")
        # Placeholder updates
        self._update_progress_bar(self.bar_seo, 92, "#2e6b3c")
        self._update_progress_bar(self.bar_commercial, 88, "#2e6b3c")
        self._update_progress_bar(self.bar_adobe, 95, "#2e6b3c")
        self._update_progress_bar(self.bar_shutterstock, 85, "#2e6b3c")
        self._update_progress_bar(self.bar_freepik, 78, "#c9a022")
        self.lbl_buyer_intent.setText("High Commercial / Advertising")
        self.txt_suggestions.append("\nOptimization complete. Title and top 10 keywords aligned with trending search vectors.")

    def _on_review(self):
        self.logger.info("Triggering SEO compliance and intent review.")
        self.txt_suggestions.setPlainText("Reviewing metadata...")
        
        # Dummy data injection for visual feedback
        self.table_density.setRowCount(3)
        self._set_table_row(self.table_density, 0, ["business", "4", "12%"])
        self._set_table_row(self.table_density, 1, ["technology", "3", "9%"])
        self._set_table_row(self.table_density, 2, ["office", "2", "6%"])
        
        self.table_ranking.setRowCount(3)
        self._set_table_row(self.table_ranking, 0, ["business", "Top 1%", "High"])
        self._set_table_row(self.table_ranking, 1, ["corporate team", "Top 5%", "Medium"])
        self._set_table_row(self.table_ranking, 2, ["modern workspace", "Top 10%", "Low"])
        
        self._update_progress_bar(self.bar_seo, 65, "#c9a022")
        self.txt_warnings.setPlainText("- Missing primary subject in the first 5 keywords.\n- Title length is too short for Adobe Stock optimal indexing.")
        self.txt_suggestions.setPlainText("- Move 'business' and 'corporate team' to the first 5 keyword slots.\n- Expand title to include setting and emotional context.")

    def _update_progress_bar(self, bar: QProgressBar, value: int, color: str = None):
        bar.setValue(value)
        if color:
            bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {color}; }}")

    def _set_table_row(self, table: QTableWidget, row: int, data: list):
        for col, text in enumerate(data):
            item = QTableWidgetItem(text)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            table.setItem(row, col, item)
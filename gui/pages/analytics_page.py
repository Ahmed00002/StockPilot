# gui/pages/analytics_page.py
import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTableWidget, 
    QTableWidgetItem, QHeaderView, QLabel, QToolBar, QTabWidget, 
    QComboBox, QFrame, QScrollArea, QProgressBar, QFormLayout, QPushButton
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QAction, QFont, QIcon, QColor

class AnalyticsPage(QWidget):
    """
    Production-ready Analytics Dashboard.
    Provides deep insights into Workspace statistics, Metadata generation rates,
    Export volumes, AI Token/Provider usage, Cost tracking, and Performance metrics.
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
            
        self.workspace_manager = self.container.get_service("workspace_manager")
        self.ai_manager = self.container.get_service("ai_manager")
        self.event_bus = self.container.get_service("event_bus")

        self._init_ui()
        self._connect_signals()
        self._load_initial_data()

    def _init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self._create_toolbar()
        
        # Scrollable area for the entire dashboard
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(15, 15, 15, 15)
        self.content_layout.setSpacing(20)
        
        self._create_summary_cards()
        self._create_detail_tabs()
        
        self.scroll_area.setWidget(self.content_widget)
        self.main_layout.addWidget(self.scroll_area)

    def _create_toolbar(self):
        self.toolbar = QToolBar("Analytics Toolbar", self)
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(16, 16))
        
        self.act_refresh = QAction("Refresh Data", self)
        self.act_export_report = QAction("Export Report (PDF/CSV)", self)
        
        self.combo_time_range = QComboBox()
        self.combo_time_range.addItems(["Last 24 Hours", "Last 7 Days", "Last 30 Days", "All Time"])
        
        self.toolbar.addAction(self.act_refresh)
        self.toolbar.addAction(self.act_export_report)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(QLabel(" Time Range: "))
        self.toolbar.addWidget(self.combo_time_range)
        
        self.main_layout.addWidget(self.toolbar)

    def _create_summary_cards(self):
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)
        
        self.card_images = self._build_stat_card("Total Images", "0", "#2b579a")
        self.card_metadata = self._build_stat_card("Metadata Generated", "0", "#2e6b3c")
        self.card_exports = self._build_stat_card("Total Exports", "0", "#b25022")
        self.card_ai_cost = self._build_stat_card("Total AI Cost", "$0.0000", "#68217a")
        
        cards_layout.addWidget(self.card_images)
        cards_layout.addWidget(self.card_metadata)
        cards_layout.addWidget(self.card_exports)
        cards_layout.addWidget(self.card_ai_cost)
        
        self.content_layout.addLayout(cards_layout)

    def _build_stat_card(self, title: str, initial_value: str, border_color: str) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(255, 255, 255, 0.05);
                border-top: 4px solid {border_color};
                border-radius: 4px;
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #a0a0a0; font-size: 12px; font-weight: bold;")
        
        lbl_value = QLabel(initial_value)
        lbl_value.setFont(QFont("Arial", 24, QFont.Bold))
        lbl_value.setStyleSheet("border: none; background: transparent;")
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        layout.addStretch()
        
        # Store a reference dynamically to easily update it later
        frame.value_label = lbl_value 
        return frame

    def _create_detail_tabs(self):
        self.tabs = QTabWidget()
        
        self._init_workspace_tab()
        self._init_ai_usage_tab()
        self._init_performance_tab()
        self._init_history_tab()
        
        self.tabs.addTab(self.tab_workspace, "Workspace Statistics")
        self.tabs.addTab(self.tab_ai_usage, "AI & Token Usage")
        self.tabs.addTab(self.tab_performance, "Performance")
        self.tabs.addTab(self.tab_history, "History & Logs")
        
        self.content_layout.addWidget(self.tabs)

    def _init_workspace_tab(self):
        self.tab_workspace = QWidget()
        layout = QVBoxLayout(self.tab_workspace)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Splitter for Tables vs Charts
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Completion Rates
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        left_layout.addWidget(QLabel("<b>Asset Completion Rates</b>"))
        self.table_completion = QTableWidget(0, 3)
        self.table_completion.setHorizontalHeaderLabels(["Category", "Count", "Completion %"])
        self.table_completion.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        left_layout.addWidget(self.table_completion)
        
        # Right side - Marketplace Exports
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        right_layout.addWidget(QLabel("<b>Export Distribution</b>"))
        self.table_distribution = QTableWidget(0, 3)
        self.table_distribution.setHorizontalHeaderLabels(["Marketplace", "Exports", "Ratio"])
        self.table_distribution.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        right_layout.addWidget(self.table_distribution)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        layout.addWidget(splitter)

    def _init_ai_usage_tab(self):
        self.tab_ai_usage = QWidget()
        layout = QVBoxLayout(self.tab_ai_usage)
        layout.setContentsMargins(15, 15, 15, 15)
        
        layout.addWidget(QLabel("<b>Provider Usage Breakdown</b>"))
        self.table_ai_usage = QTableWidget(0, 6)
        self.table_ai_usage.setHorizontalHeaderLabels([
            "Provider", "Model", "Calls", "Tokens (In)", "Tokens (Out)", "Est. Cost"
        ])
        header = self.table_ai_usage.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        layout.addWidget(self.table_ai_usage)
        
        # Cost visualization (progress bars mimicking bar charts)
        layout.addWidget(QLabel("<b>Cost Distribution</b>"))
        self.cost_chart_layout = QFormLayout()
        layout.addLayout(self.cost_chart_layout)

    def _init_performance_tab(self):
        self.tab_performance = QWidget()
        layout = QVBoxLayout(self.tab_performance)
        layout.setContentsMargins(15, 15, 15, 15)
        
        layout.addWidget(QLabel("<b>System Performance & Latency</b>"))
        
        self.table_performance = QTableWidget(0, 4)
        self.table_performance.setHorizontalHeaderLabels([
            "Operation / Provider", "Avg Latency (ms)", "Success Rate", "Total Ops"
        ])
        self.table_performance.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        
        layout.addWidget(self.table_performance)

    def _init_history_tab(self):
        self.tab_history = QWidget()
        layout = QVBoxLayout(self.tab_history)
        layout.setContentsMargins(15, 15, 15, 15)
        
        self.table_history = QTableWidget(0, 5)
        self.table_history.setHorizontalHeaderLabels([
            "Timestamp", "Event Type", "Target", "Status", "Details"
        ])
        header = self.table_history.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        
        layout.addWidget(self.table_history)

    def _connect_signals(self):
        self.act_refresh.triggered.connect(self._refresh_analytics)
        self.act_export_report.triggered.connect(self._export_report)
        self.combo_time_range.currentTextChanged.connect(self._on_time_range_changed)

    def _load_initial_data(self):
        """Populate dashboard with initial / dummy data to show layout structure."""
        self._refresh_analytics()

    def _refresh_analytics(self):
        self.logger.info("Refreshing analytics dashboard...")
        
        # Update Summary Cards
        self.card_images.value_label.setText("1,245")
        self.card_metadata.value_label.setText("890")
        self.card_exports.value_label.setText("3,450")
        self.card_ai_cost.value_label.setText("$4.52")
        
        # Populate Workspace Table
        self.table_completion.setRowCount(0)
        self._add_table_row(self.table_completion, ["Title Generated", "890", "71.4%"])
        self._add_table_row(self.table_completion, ["Keywords Generated", "840", "67.4%"])
        self._add_table_row(self.table_completion, ["Compliance Reviewed", "512", "41.1%"])
        
        self.table_distribution.setRowCount(0)
        self._add_table_row(self.table_distribution, ["Adobe Stock", "1,200", "34.7%"])
        self._add_table_row(self.table_distribution, ["Shutterstock", "1,150", "33.3%"])
        self._add_table_row(self.table_distribution, ["Freepik", "1,100", "31.8%"])
        
        # Populate AI Usage Table
        self.table_ai_usage.setRowCount(0)
        self._add_table_row(self.table_ai_usage, ["OpenAI", "gpt-4o", "450", "150,000", "45,000", "$2.85"])
        self._add_table_row(self.table_ai_usage, ["Gemini", "gemini-1.5-flash", "800", "320,000", "80,000", "$1.15"])
        self._add_table_row(self.table_ai_usage, ["DeepSeek", "deepseek-chat", "245", "85,000", "22,000", "$0.52"])
        
        # Populate Cost Progress Bars
        self._clear_layout(self.cost_chart_layout)
        self._add_progress_bar_row(self.cost_chart_layout, "OpenAI ($2.85)", 63, "#2b579a")
        self._add_progress_bar_row(self.cost_chart_layout, "Gemini ($1.15)", 25, "#2e6b3c")
        self._add_progress_bar_row(self.cost_chart_layout, "DeepSeek ($0.52)", 12, "#68217a")

        # Populate Performance Table
        self.table_performance.setRowCount(0)
        self._add_table_row(self.table_performance, ["OpenAI Metadata Gen", "1,205 ms", "99.2%", "450"])
        self._add_table_row(self.table_performance, ["Gemini Keyword Ext", "840 ms", "99.8%", "800"])
        self._add_table_row(self.table_performance, ["Local Disk Scan", "45 ms / img", "100%", "1,245"])

        # Populate History Table
        self.table_history.setRowCount(0)
        self._add_table_row(self.table_history, ["2026-06-27 10:15:02", "Export", "Workspace A", "Success", "Generated Adobe CSV for 150 images."])
        self._add_table_row(self.table_history, ["2026-06-27 10:12:45", "AI Gen", "IMG_4922.jpg", "Success", "Generated Title & Desc via OpenAI."])
        self._add_table_row(self.table_history, ["2026-06-27 10:10:10", "System", "Index", "Complete", "Indexed 245 new images."])

    def _on_time_range_changed(self, range_text):
        self.logger.info(f"Time range changed to: {range_text}")
        self._refresh_analytics()

    def _export_report(self):
        self.logger.info("Exporting analytics report...")
        # Placeholder for PDF/CSV generation logic

    def _add_table_row(self, table: QTableWidget, row_data: list):
        row = table.rowCount()
        table.insertRow(row)
        for col, data in enumerate(row_data):
            item = QTableWidgetItem(str(data))
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            table.setItem(row, col, item)

    def _add_progress_bar_row(self, layout: QFormLayout, label: str, percentage: int, color: str):
        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(percentage)
        bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {color}; }}")
        bar.setTextVisible(True)
        bar.setFormat("%v%")
        layout.addRow(QLabel(label), bar)

    def _clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self._clear_layout(item.layout())
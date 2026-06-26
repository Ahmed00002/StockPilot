# gui/ai/provider_benchmark_widget.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt, QTimer
from ai.orchestration.provider_benchmark import ProviderBenchmark

class ProviderBenchmarkWidget(QWidget):
    """Displays real-time reliability and latency metrics collected by the orchestration engine."""

    def __init__(self, benchmark: ProviderBenchmark, parent=None):
        super().__init__(parent)
        self.benchmark = benchmark
        self.providers = ["Google Gemini", "OpenAI Engine", "Anthropic Claude", "Groq LPU Engine", "DeepSeek", "OpenRouter Gateway System"]
        self._setup_ui()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._refresh_data)
        self.timer.start(5000)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        self.table = QTableWidget(len(self.providers), 3)
        self.table.setHorizontalHeaderLabels(["Provider", "Avg Latency (ms)", "Success Rate (%)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        self._refresh_data()

    def _refresh_data(self):
        for row, provider in enumerate(self.providers):
            self.table.setItem(row, 0, QTableWidgetItem(provider))
            
            latency = self.benchmark.get_average_latency(provider)
            latency_str = f"{latency:.0f} ms" if latency != float('inf') else "N/A"
            self.table.setItem(row, 1, QTableWidgetItem(latency_str))
            
            success = self.benchmark.get_success_rate(provider)
            self.table.setItem(row, 2, QTableWidgetItem(f"{success * 100:.1f}%"))
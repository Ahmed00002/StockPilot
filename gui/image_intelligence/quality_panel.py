# gui/image_intelligence/quality_panel.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QFrame
from PySide6.QtCore import Qt

class QualityPanel(QWidget):
    """Displays image quality metrics from ImageQualityAnalyzer."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._clear_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        
        title = QLabel("Image Quality Analysis")
        title.setStyleSheet("font-weight: bold; font-size: 14px; padding: 8px;")
        layout.addWidget(title)
        
        self.sharpness_bar = self._create_metric_row("Sharpness", layout)
        self.contrast_bar = self._create_metric_row("Contrast", layout)
        self.brightness_bar = self._create_metric_row("Brightness", layout)
        self.noise_bar = self._create_metric_row("Noise Level", layout, invert=True)
        
        self.overall_score_label = QLabel("Overall Score: --")
        self.overall_score_label.setStyleSheet("font-weight: bold; font-size: 13px; padding: 8px;")
        layout.addWidget(self.overall_score_label)
        
        self.status_label = QLabel("No image analyzed")
        self.status_label.setStyleSheet("color: #858585; font-style: italic;")
        layout.addWidget(self.status_label)

    def _create_metric_row(self, label_text, layout, invert=False):
        frame = QFrame()
        frame.setStyleSheet("background-color: #1e1e1e; border-radius: 4px;")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(8, 4, 8, 4)
        
        label = QLabel(label_text)
        label.setStyleSheet("color: #cccccc; font-size: 12px;")
        frame_layout.addWidget(label)
        
        progress = QProgressBar()
        progress.setMinimum(0)
        progress.setMaximum(100)
        progress.setValue(0)
        progress.setTextVisible(False)
        progress.setFixedHeight(8)
        progress.setStyleSheet("""
            QProgressBar { background-color: #3a3a3a; border-radius: 4px; }
            QProgressBar::chunk { background-color: #4CAF50; border-radius: 4px; }
        """)
        frame_layout.addWidget(progress)
        
        layout.addWidget(frame)
        return progress

    def set_quality_data(self, quality_data):
        """Set quality data from ImageQualityData."""
        if not quality_data:
            self._clear_data()
            return
        
        sharpness_score = min(100.0, quality_data.sharpness / 10.0)
        contrast_score = min(100.0, quality_data.contrast * 1.5)
        brightness_score = min(100.0, quality_data.brightness * 0.4)
        noise_score = max(0.0, 100.0 - (quality_data.noise_level * 10.0))
        
        self.sharpness_bar.setValue(int(sharpness_score))
        self.contrast_bar.setValue(int(contrast_score))
        self.brightness_bar.setValue(int(brightness_score))
        self.noise_bar.setValue(int(noise_score))
        
        self.overall_score_label.setText(f"Overall Score: {quality_data.overall_score:.1f}/100")
        self.overall_score_label.setStyleSheet(
            f"font-weight: bold; font-size: 13px; padding: 8px; color: {'#4CAF50' if quality_data.overall_score >= 70 else '#FFC107' if quality_data.overall_score >= 40 else '#F44336'};"
        )
        self.status_label.setText("Quality analysis complete")

    def _clear_data(self):
        self.sharpness_bar.setValue(0)
        self.contrast_bar.setValue(0)
        self.brightness_bar.setValue(0)
        self.noise_bar.setValue(0)
        self.overall_score_label.setText("Overall Score: --")
        self.status_label.setText("No image analyzed")

    def clear(self):
        """Clear all quality data."""
        self._clear_data()
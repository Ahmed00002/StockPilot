# gui/description/description_editor.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal

from gui.description.description_score_widget import DescriptionScoreWidget
from gui.description.description_preview import DescriptionPreviewPanel
from gui.description.description_history_panel import DescriptionHistoryPanel

class DescriptionEditorWidget(QWidget):
    generate_requested = Signal()
    save_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        main_layout = QHBoxLayout(self)

        left_panel = QVBoxLayout()
        
        editor_header = QLabel("Description Editor")
        editor_header.setStyleSheet("font-weight: bold; font-size: 14px;")
        left_panel.addWidget(editor_header)

        self.text_edit = QTextEdit()
        self.text_edit.setMinimumHeight(120)
        self.text_edit.textChanged.connect(self._on_text_changed)
        left_panel.addWidget(self.text_edit)

        counters_layout = QHBoxLayout()
        self.char_counter = QLabel("0 / 500 characters")
        self.word_counter = QLabel("0 words")
        self.live_seo_score = QLabel("Live SEO: 0")
        
        counters_layout.addWidget(self.char_counter)
        counters_layout.addWidget(self.word_counter)
        counters_layout.addStretch()
        counters_layout.addWidget(self.live_seo_score)
        left_panel.addLayout(counters_layout)

        btn_layout = QHBoxLayout()
        self.generate_btn = QPushButton("Generate Intelligent Description")
        self.generate_btn.clicked.connect(self.generate_requested.emit)
        
        self.save_btn = QPushButton("Save Description")
        self.save_btn.clicked.connect(self._on_save_clicked)
        
        btn_layout.addWidget(self.generate_btn)
        btn_layout.addWidget(self.save_btn)
        left_panel.addLayout(btn_layout)

        self.score_widget = DescriptionScoreWidget()
        left_panel.addWidget(self.score_widget)

        self.preview_panel = DescriptionPreviewPanel()
        left_panel.addWidget(self.preview_panel)
        left_panel.addStretch()

        right_panel = QVBoxLayout()
        self.history_panel = DescriptionHistoryPanel()
        self.history_panel.description_selected.connect(self._on_history_selected)
        right_panel.addWidget(self.history_panel)

        main_layout.addLayout(left_panel, stretch=2)
        main_layout.addLayout(right_panel, stretch=1)

    def _on_text_changed(self):
        text = self.text_edit.toPlainText()
        char_len = len(text)
        words = len(text.split())
        
        self.char_counter.setText(f"{char_len} / 500 characters")
        self.word_counter.setText(f"{words} words")
        
        if char_len > 500:
            self.char_counter.setStyleSheet("color: red;")
        elif char_len < 20:
            self.char_counter.setStyleSheet("color: orange;")
        else:
            self.char_counter.setStyleSheet("color: green;")
            
        self.preview_panel.update_preview(text)
        self._update_live_seo(words, char_len)

    def _update_live_seo(self, words: int, chars: int):
        score = 100
        if words < 10:
            score -= 30
        elif words > 50:
            score -= (words - 50)
            
        score = max(0, min(100, score))
        self.live_seo_score.setText(f"Live SEO: {score}")

    def _on_save_clicked(self):
        self.save_requested.emit(self.text_edit.toPlainText().strip())

    def _on_history_selected(self, desc: str):
        self.text_edit.setPlainText(desc)

    def update_engine_results(self, result_dict: dict):
        self.text_edit.setPlainText(result_dict.get("description", ""))
        
        best_details = next((r for r in result_dict.get("ranked_details", []) if r["description"] == result_dict["description"]), None)
        if best_details:
            self.score_widget.update_scores(
                overall=best_details["score"],
                seo=best_details["seo"],
                comm=best_details["comm"],
                readability=best_details["readability"]
            )
            
        alternatives = [r for r in result_dict.get("ranked_details", []) if r["description"] != result_dict["description"]]
        self.history_panel.update_history(alternatives)
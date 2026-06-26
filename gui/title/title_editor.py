# gui/title/title_editor.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal

from gui.title.title_score_widget import TitleScoreWidget
from gui.title.title_preview import TitlePreviewPanel
from gui.title.title_history_panel import TitleHistoryPanel

class TitleEditorWidget(QWidget):
    generate_requested = Signal()
    save_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        main_layout = QHBoxLayout(self)

        left_panel = QVBoxLayout()
        
        editor_header = QLabel("Title Editor")
        editor_header.setStyleSheet("font-weight: bold; font-size: 14px;")
        left_panel.addWidget(editor_header)

        self.text_edit = QTextEdit()
        self.text_edit.setFixedHeight(80)
        self.text_edit.textChanged.connect(self._on_text_changed)
        left_panel.addWidget(self.text_edit)

        self.char_counter = QLabel("0 / 200 characters")
        self.char_counter.setAlignment(Qt.AlignmentFlag.AlignRight)
        left_panel.addWidget(self.char_counter)

        btn_layout = QHBoxLayout()
        self.generate_btn = QPushButton("Generate Intelligent Title")
        self.generate_btn.clicked.connect(self.generate_requested.emit)
        
        self.save_btn = QPushButton("Save Title")
        self.save_btn.clicked.connect(self._on_save_clicked)
        
        btn_layout.addWidget(self.generate_btn)
        btn_layout.addWidget(self.save_btn)
        left_panel.addLayout(btn_layout)

        self.score_widget = TitleScoreWidget()
        left_panel.addWidget(self.score_widget)

        self.preview_panel = TitlePreviewPanel()
        left_panel.addWidget(self.preview_panel)
        left_panel.addStretch()

        right_panel = QVBoxLayout()
        self.history_panel = TitleHistoryPanel()
        self.history_panel.title_selected.connect(self._on_history_selected)
        right_panel.addWidget(self.history_panel)

        main_layout.addLayout(left_panel, stretch=2)
        main_layout.addLayout(right_panel, stretch=1)

    def _on_text_changed(self):
        text = self.text_edit.toPlainText()
        length = len(text)
        self.char_counter.setText(f"{length} / 200 characters")
        if length > 200:
            self.char_counter.setStyleSheet("color: red;")
        elif length < 5:
            self.char_counter.setStyleSheet("color: orange;")
        else:
            self.char_counter.setStyleSheet("color: green;")
            
        self.preview_panel.update_preview(text)

    def _on_save_clicked(self):
        self.save_requested.emit(self.text_edit.toPlainText().strip())

    def _on_history_selected(self, title: str):
        self.text_edit.setPlainText(title)

    def update_engine_results(self, result_dict: dict):
        self.text_edit.setPlainText(result_dict.get("title", ""))
        
        best_details = next((r for r in result_dict.get("ranked_details", []) if r["title"] == result_dict["title"]), None)
        if best_details:
            self.score_widget.update_scores(
                overall=best_details["score"],
                seo=best_details["seo"],
                comm=best_details["comm"]
            )
            
        alternatives = [r for r in result_dict.get("ranked_details", []) if r["title"] != result_dict["title"]]
        self.history_panel.update_history(alternatives)
# gui/workspace/metadata_compare_view.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QSplitter
from PySide6.QtCore import Qt

class MetadataCompareView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        header = QLabel("Metadata Comparison")
        header.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        self.left_panel = self._create_side("Version 1 (Active)")
        self.right_panel = self._create_side("Version 2 (Selected)")
        
        splitter.addWidget(self.left_panel['widget'])
        splitter.addWidget(self.right_panel['widget'])
        
        layout.addWidget(splitter)

    def _create_side(self, title: str) -> dict:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-weight: bold; background: #eee; padding: 5px; color: black;")
        layout.addWidget(lbl_title)
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        return {'widget': widget, 'label': lbl_title, 'text': text_edit}

    def _render_diff_html(self, diff_list, show_op: str) -> str:
        """Converts difflib opcodes into visually highlighted HTML chunks."""
        html = ""
        for op, text in diff_list:
            safe_text = str(text).replace("<", "&lt;").replace(">", "&gt;")
            if op == 'equal':
                html += safe_text + " "
            elif op == show_op:
                color = "#28a745" if op == "insert" else "#dc3545"
                text_dec = "line-through" if op == "delete" else "none"
                html += f'<span style="background-color: {color}; color: white; padding: 1px 3px; border-radius: 3px; text-decoration: {text_dec};">{safe_text}</span> '
        return html

    def update_compare(self, v1: any, v2: any, diff_result: any):
        self.left_panel['label'].setText(f"Active Version: {v1.provider} ({v1.reason})")
        self.right_panel['label'].setText(f"Selected Version: {v2.provider} ({v2.reason})")
        
        if not diff_result:
            # Fallback for empty comparisons
            v1_text = f"TITLE:\n{v1.title}\n\nDESCRIPTION:\n{v1.description}\n\nKEYWORDS ({len(v1.keywords)}):\n{', '.join(v1.keywords)}"
            v2_text = f"TITLE:\n{v2.title}\n\nDESCRIPTION:\n{v2.description}\n\nKEYWORDS ({len(v2.keywords)}):\n{', '.join(v2.keywords)}"
            self.left_panel['text'].setPlainText(v1_text)
            self.right_panel['text'].setPlainText(v2_text)
            return

        # INTEGRATION FIX: Map diff results to visual HTML formatting
        v1_title = self._render_diff_html(diff_result.title_diff, 'delete')
        v2_title = self._render_diff_html(diff_result.title_diff, 'insert')

        v1_desc = self._render_diff_html(diff_result.desc_diff, 'delete')
        v2_desc = self._render_diff_html(diff_result.desc_diff, 'insert')

        # Render Keywords with status tags
        v1_kws = []
        for kw in v1.keywords:
            if kw in diff_result.removed_keywords:
                v1_kws.append(f'<span style="background-color: #dc3545; color: white; padding: 2px;">{kw}</span>')
            else:
                v1_kws.append(kw)

        v2_kws = []
        for kw in v2.keywords:
            if kw in diff_result.added_keywords:
                v2_kws.append(f'<span style="background-color: #28a745; color: white; padding: 2px;">{kw}</span>')
            else:
                v2_kws.append(kw)

        v1_html = f"<b>TITLE:</b><br>{v1_title}<br><br><b>DESCRIPTION:</b><br>{v1_desc}<br><br><b>KEYWORDS ({len(v1.keywords)}):</b><br>{', '.join(v1_kws)}"
        v2_html = f"<b>TITLE:</b><br>{v2_title}<br><br><b>DESCRIPTION:</b><br>{v2_desc}<br><br><b>KEYWORDS ({len(v2.keywords)}):</b><br>{', '.join(v2_kws)}"
        
        self.left_panel['text'].setHtml(v1_html)
        self.right_panel['text'].setHtml(v2_html)
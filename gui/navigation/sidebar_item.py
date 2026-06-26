# gui/navigation/sidebar_item.py
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSizePolicy
from PySide6.QtGui import QIcon, QMouseEvent
from PySide6.QtCore import Qt, Signal, Property, QPropertyAnimation, QEasingCurve
from gui.widgets.icon_loader import IconLoader

class SidebarItem(QWidget):
    """An interactive item inside the global left sidebar navigation."""
    
    clicked = Signal(str)

    def __init__(self, page_id: str, label_text: str, icon_name: str, parent=None):
        super().__init__(parent)
        self.page_id = page_id
        self.label_text = label_text
        self.icon_name = icon_name
        self._is_selected = False
        self._is_collapsed = False
        self._hover_bg_opacity = 0
        
        self.setFixedHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(label_text)
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(16, 0, 16, 0)
        self.layout.setSpacing(12)
        
        self.icon_label = QLabel()
        self.icon_label.setPixmap(IconLoader.get_icon(self.icon_name).pixmap(20, 20))
        self.icon_label.setFixedSize(20, 20)
        
        self.text_label = QLabel(self.label_text)
        self.text_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        self.layout.addWidget(self.icon_label)
        self.layout.addWidget(self.text_label)
        
        self.setStyleSheet(self._get_base_stylesheet())

        self.anim_hover = QPropertyAnimation(self, b"hover_bg_opacity")
        self.anim_hover.setDuration(150)
        self.anim_hover.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def _get_base_stylesheet(self) -> str:
        if self._is_selected:
            return """
                SidebarItem {
                    background-color: #3e3e42;
                    border-left: 3px solid #007acc;
                }
                QLabel { color: #ffffff; font-weight: bold; }
            """
        return """
                SidebarItem {
                    background-color: transparent;
                    border-left: 3px solid transparent;
                }
                QLabel { color: #cccccc; font-weight: normal; }
            """

    def set_collapsed(self, collapsed: bool) -> None:
        self._is_collapsed = collapsed
        self.text_label.setVisible(not collapsed)
        if collapsed:
            self.layout.setContentsMargins(10, 0, 10, 0)
        else:
            self.layout.setContentsMargins(16, 0, 16, 0)

    def set_selected(self, selected: bool) -> None:
        self._is_selected = selected
        self.setStyleSheet(self._get_base_stylesheet())

    @Property(int)
    def hover_bg_opacity(self) -> int:
        return self._hover_bg_opacity

    @hover_bg_opacity.setter
    def hover_bg_opacity(self, value: int) -> None:
        self._hover_bg_opacity = value
        if not self._is_selected:
            self.setStyleSheet(f"""
                SidebarItem {{
                    background-color: rgba(62, 62, 66, {value});
                    border-left: 3px solid transparent;
                }}
                QLabel {{ color: #cccccc; }}
            """)

    def enterEvent(self, event) -> None:
        if not self._is_selected:
            self.anim_hover.setStartValue(self.hover_bg_opacity)
            self.anim_hover.setEndValue(255)
            self.anim_hover.start()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        if not self._is_selected:
            self.anim_hover.setStartValue(self.hover_bg_opacity)
            self.anim_hover.setEndValue(0)
            self.anim_hover.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.page_id)
        super().mousePressEvent(event)
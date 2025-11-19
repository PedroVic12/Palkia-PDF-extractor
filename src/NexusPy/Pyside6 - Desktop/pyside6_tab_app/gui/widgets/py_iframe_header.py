from qt_core import *

class PyIframeHeader(QWidget):
    def __init__(self, title_text, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        self.setStyleSheet("background-color: #2c313a; border-bottom: 1px solid #3d444f;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)

        self.title_label = QLabel(title_text)
        self.title_label.setObjectName("iframe_header_title")
        self.title_label.setStyleSheet("color: #f0f0f0; font-size: 14pt; font-weight: bold;")
        layout.addWidget(self.title_label)
        layout.addStretch()

    def set_title(self, title_text):
        self.title_label.setText(title_text)

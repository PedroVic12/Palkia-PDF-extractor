"""
glass_carousel_app.py

Example PySide6 application following OOP best-practices.

- GlassCard: reusable card widget with glassmorphism-like styling.
- CarouselWidget: simple stacked carousel with prev/next and autoplay.
- DemoApp: main application window assembling cards and carousel.

Run:
  python glass_carousel_app.py

Notes:
- Real "backdrop blur" is platform-dependent. This example simulates glass by
  using translucent backgrounds, a subtle border and shadow.
"""
from __future__ import annotations
import sys
from typing import List
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QFrame, QStackedWidget, QSizePolicy, QGridLayout, QMainWindow
)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QGraphicsDropShadowEffect


class GlassCard(QFrame):
    """A small reusable 'card' widget with glass-like styling.

    Attributes:
        title: large title text
        subtitle: smaller subtitle text
    """

    def __init__(self, title: str, subtitle: str = "", width: int = 260, height: int = 140, parent=None):
        super().__init__(parent)
        self.title = title
        self.subtitle = subtitle
        self.setFixedSize(width, height)
        self.setObjectName("glassCard")
        self._setup_ui()
        self._apply_effects()

    def _setup_ui(self):
        self.setStyleSheet(self._stylesheet())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        self.lbl_title = QLabel(self.title)
        self.lbl_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.lbl_title.setStyleSheet("color: white;")

        self.lbl_sub = QLabel(self.subtitle)
        self.lbl_sub.setFont(QFont("Segoe UI", 9))
        self.lbl_sub.setStyleSheet("color: rgba(255,255,255,0.85);")
        self.lbl_sub.setWordWrap(True)

        layout.addStretch()
        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_sub)
        layout.addStretch()

    def _apply_effects(self):
        # subtle shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(shadow)

    @staticmethod
    def _stylesheet() -> str:
        # translucent background, light border and inner gradient to simulate glass
        return """
        QFrame#glassCard {
            background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(255,255,255,0.06), stop:1 rgba(255,255,255,0.03));
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 12px;
        }
        """


class CarouselWidget(QWidget):
    """Simple stacked carousel. Accepts any QWidget as pages.

    Features:
    - Prev / Next buttons
    - Autoplay with configurable interval
    """

    def __init__(self, pages: List[QWidget] | None = None, autoplay: bool = True, interval_ms: int = 3500, parent=None):
        super().__init__(parent)
        self._pages = pages or []
        self._interval = interval_ms
        self._autoplay = autoplay
        self._setup_ui()
        self._setup_timer()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(8)

        self.stack = QStackedWidget()
        self.stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        btn_layout.addStretch()
        self.btn_prev = QPushButton("◀")
        self.btn_next = QPushButton("▶")
        self.btn_prev.setFixedSize(36, 28)
        self.btn_next.setFixedSize(36, 28)
        btn_layout.addWidget(self.btn_prev)
        btn_layout.addWidget(self.btn_next)
        btn_layout.addStretch()

        layout.addWidget(self.stack, 1)
        layout.addLayout(btn_layout)

        self.btn_prev.clicked.connect(self.prev)
        self.btn_next.clicked.connect(self.next)

        # add initial pages
        for p in self._pages:
            self.add_page(p)

    def _setup_timer(self):
        self.timer = QTimer(self)
        self.timer.setInterval(self._interval)
        self.timer.timeout.connect(self.next)
        if self._autoplay and self.stack.count() > 1:
            self.timer.start()

    def add_page(self, widget: QWidget):
        self.stack.addWidget(widget)
        # start timer only if we have multiple pages
        if self._autoplay and self.stack.count() > 1:
            self.timer.start()

    def next(self):
        if self.stack.count() == 0:
            return
        idx = (self.stack.currentIndex() + 1) % self.stack.count()
        self.stack.setCurrentIndex(idx)

    def prev(self):
        if self.stack.count() == 0:
            return
        idx = (self.stack.currentIndex() - 1) % self.stack.count()
        self.stack.setCurrentIndex(idx)


class DemoApp(QMainWindow):
    """Main application window demonstrating cards and carousel."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Glass Cards & Carousel - Demo")
        self.resize(980, 640)
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # top area: grid of cards
        grid_container = QWidget()
        grid_layout = QGridLayout(grid_container)
        grid_layout.setSpacing(14)

        cards = [
            GlassCard("Relatório Diário", "Visão resumida das atividades e estados"),
            GlassCard("Alertas", "Últimos 5 alertas críticos"),
            GlassCard("Equipe", "Responsáveis e cargas atribuídas"),
            GlassCard("Tempo Real", "Atualizações e métricas em tempo real"),
        ]

        for i, c in enumerate(cards):
            r = i // 2
            col = i % 2
            grid_layout.addWidget(c, r, col)

        main_layout.addWidget(grid_container)

        # carousel area
        carousel_pages = [GlassCard(f"Slide {i+1}", f"Descrição do slide {i+1}") for i in range(4)]
        self.carousel = CarouselWidget(carousel_pages, autoplay=True, interval_ms=3000)
        self.carousel.setFixedHeight(220)
        main_layout.addWidget(self.carousel)

        # footer actions
        actions = QWidget()
        a_layout = QHBoxLayout(actions)
        a_layout.addStretch()
        btn_refresh = QPushButton("Atualizar")
        btn_refresh.clicked.connect(self._on_refresh)
        a_layout.addWidget(btn_refresh)
        main_layout.addWidget(actions)

        # overall glass background simulation
        self.setStyleSheet(self._app_stylesheet())

    def _on_refresh(self):
        # simple demo action: rotate carousel
        self.carousel.next()

    @staticmethod
    def _app_stylesheet() -> str:
        # application-level subtle background
        return """
        QWidget {
            background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(10,12,20,1), stop:1 rgba(28,30,40,1));
        }
        QPushButton {
            background-color: rgba(255,255,255,0.06);
            color: white;
            padding: 6px 10px;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.08);
        }
        QPushButton:hover { background-color: rgba(255,255,255,0.10); }
        QLabel { color: #eaeef6; }
        """


def main():
    app = QApplication(sys.argv)
    demo = DemoApp()
    demo.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

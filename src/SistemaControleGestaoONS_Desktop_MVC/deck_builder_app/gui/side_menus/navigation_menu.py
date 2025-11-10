from PySide6.QtWidgets import QFrame, QVBoxLayout
from PySide6.QtCore import Signal
from ..widgets.py_push_button import PyPushButton

class NavigationMenu(QFrame):
    """
    A widget that holds the main navigation buttons for the Deck Builder app.
    Emits signals when buttons are clicked.
    """
    dashboard_requested = Signal()
    deck_builder_requested = Signal()
    settings_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("navigation_menu")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(5)

        # Create navigation buttons
        self.btn_dashboard = PyPushButton(text="Dashboard", icon_path="icon_home.svg")
        self.btn_deck_builder = PyPushButton(text="Deck Builder", icon_path="icon_widgets.svg")
        self.btn_settings = PyPushButton(text="Configurações", icon_path="icon_settings.svg")

        # Add to layout
        self.layout.addWidget(self.btn_dashboard)
        self.layout.addWidget(self.btn_deck_builder)
        self.layout.addWidget(self.btn_settings)
        
        # Connect internal clicks to signal emissions
        self.btn_dashboard.clicked.connect(self.dashboard_requested)
        self.btn_deck_builder.clicked.connect(self.deck_builder_requested)
        self.btn_settings.clicked.connect(self.settings_requested)

    def set_active_button(self, tab_name):
        """Sets the visual state of the navigation buttons."""
        self.btn_dashboard.set_active(tab_name == "Dashboard")
        self.btn_deck_builder.set_active(tab_name == "Deck Builder")
        self.btn_settings.set_active(tab_name == "Configurações")

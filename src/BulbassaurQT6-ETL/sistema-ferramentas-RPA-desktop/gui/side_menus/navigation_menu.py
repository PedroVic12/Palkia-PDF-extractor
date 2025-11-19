from PySide6.QtWidgets import QFrame, QVBoxLayout
from PySide6.QtCore import Signal
from ..widgets.py_push_button import PyPushButton

class NavigationMenu(QFrame):
    """
    A widget that holds the main navigation buttons.
    Emits signals when buttons are clicked.
    """
    dashboard_requested = Signal()
    pomodoro_requested = Signal()
    checklist_requested = Signal()
    settings_requested = Signal()
    perdas_duplas_requested = Signal() # Novo sinal para Perdas Duplas ETL

    def __init__(self):
        super().__init__()
        self.setObjectName("navigation_menu")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(5)

        # Create navigation buttons
        self.btn_dashboard = PyPushButton(text="Dashboard", icon_path="icon_home.svg")
        self.btn_pomodoro = PyPushButton(text="Pomodoro", icon_path="icon_widgets.svg")
        self.btn_checklist = PyPushButton(text="Checklist", icon_path="icon_widgets.svg")
        self.btn_settings = PyPushButton(text="Configurações", icon_path="icon_settings.svg")
        self.btn_perdas_duplas = PyPushButton(text="🤖 Perdas Duplas ETL", icon_path="icon_rpa.svg") # Novo botão

        # Add to layout
        self.layout.addWidget(self.btn_dashboard)
        self.layout.addWidget(self.btn_pomodoro)
        self.layout.addWidget(self.btn_checklist)
        self.layout.addWidget(self.btn_settings)
        self.layout.addWidget(self.btn_perdas_duplas) # Adiciona o novo botão ao layout
        
        # Connect internal clicks to signal emissions
        self.btn_dashboard.clicked.connect(self.dashboard_requested)
        self.btn_pomodoro.clicked.connect(self.pomodoro_requested)
        self.btn_checklist.clicked.connect(self.checklist_requested)
        self.btn_settings.clicked.connect(self.settings_requested)
        self.btn_perdas_duplas.clicked.connect(self.perdas_duplas_requested) # Conecta o novo botão ao novo sinal

    def set_active_button(self, tab_name):
        """Sets the visual state of the navigation buttons."""
        self.btn_dashboard.set_active(tab_name == "Dashboard")
        self.btn_pomodoro.set_active(tab_name == "Pomodoro")
        self.btn_checklist.set_active(tab_name == "Checklist")
        self.btn_settings.set_active(tab_name == "Configurações")
        self.btn_perdas_duplas.set_active(tab_name == "Perdas Duplas ETL") # Atualiza para o novo botão

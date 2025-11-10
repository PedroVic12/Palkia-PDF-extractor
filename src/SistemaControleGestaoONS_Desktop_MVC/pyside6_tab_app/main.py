# ///////////////////////////////////////////////////////////////
#
# BY: Pedro Victor Rodrigues Veras (based on Wanderson M. Pimenta)
# PROJECT MADE WITH: Qt Designer and PySide6
# V: 5.0.0 (MVC Settings Refactor)
#
# ///////////////////////////////////////////////////////////////

# IMPORT MODULES
import sys
import os 

# IMPORT QT CORE
from qt_core import *

# IMPORT STYLES
from styles import DARK_STYLE, LIGHT_STYLE

# IMPORT MODEL
from settings_model import SettingsModel

# IMPORT MAIN WINDOW
from gui.windows.main_window.ui_main_window import UI_MainWindow

# IMPORT IFRAME WIDGETS
from gui.iframes.dashboard_widget import DashboardWidget
from gui.iframes.pomodoro_widget import PomodoroWidget
from gui.iframes.checklist_widget import ChecklistWidget
from gui.iframes.settings_widget import SettingsWidget

# MAIN WINDOW
class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app 

        # SETUP MAIN WINDOW
        self.ui = UI_MainWindow()
        self.ui.setup_ui(self)

        # SETUP SETTINGS MODEL
        self.settings_model = SettingsModel()
        self.settings_model.settings_changed.connect(self.apply_settings_from_model)

        # APPLY INITIAL SETTINGS
        self.apply_settings_from_model()

        # Store open tabs to avoid duplicates
        self.open_tabs = {}

        # Connect buttons
        self.ui.toggle_button.clicked.connect(self.toggle_button)
        self.ui.btn_dashboard.clicked.connect(self.open_dashboard_tab)
        self.ui.btn_pomodoro.clicked.connect(self.open_pomodoro_tab)
        self.ui.btn_checklist.clicked.connect(self.open_checklist_tab)
        self.ui.settings_btn.clicked.connect(self.open_settings_tab)

        # Connect tab close signal
        self.ui.tabs.tabCloseRequested.connect(self.close_tab)

        # Open the initial dashboard tab
        self.open_dashboard_tab()

        # EXIBI A NOSSA APLICAÇÃO
        self.show()

    # SETTINGS APPLICATION
    # ///////////////////////////////////////////////////////////////
    @Slot()
    def apply_settings_from_model(self):
        """Reads settings from the model and applies them to the app."""
        # Apply theme
        theme = self.settings_model.get("theme")
        if theme == "dark":
            self.app.setStyleSheet(DARK_STYLE)
        else:
            self.app.setStyleSheet(LIGHT_STYLE)
        
        # Apply font
        font_family = self.settings_model.get("font_family")
        font_size = self.settings_model.get("font_size")
        font = QFont(font_family, font_size)
        self.app.setFont(font)

    @Slot(dict)
    def handle_settings_saved(self, settings_dict):
        """Receives new settings from the widget and tells the model to save them."""
        self.settings_model.set_and_save(settings_dict)

    # TAB MANAGEMENT
    # ///////////////////////////////////////////////////////////////
    def open_or_focus_tab(self, name, widget_class):
        if name in self.open_tabs:
            self.ui.tabs.setCurrentWidget(self.open_tabs[name])
        else:
            widget = widget_class()
            
            if name == "Configurações":
                # Connect the widget's save signal to our handler
                widget.settings_saved.connect(self.handle_settings_saved)
                # Set its initial state from the model
                widget.set_initial_values(
                    theme=self.settings_model.get("theme"),
                    font_family=self.settings_model.get("font_family"),
                    font_size=self.settings_model.get("font_size")
                )

            index = self.ui.tabs.addTab(widget, name)
            self.ui.tabs.setCurrentIndex(index)
            self.open_tabs[name] = widget
        
        self.update_active_button(name)

    def close_tab(self, index):
        widget = self.ui.tabs.widget(index)
        if widget is not None:
            tab_name_to_remove = ""
            for name, w in self.open_tabs.items():
                if w == widget:
                    tab_name_to_remove = name
                    break
            
            if tab_name_to_remove in self.open_tabs:
                del self.open_tabs[tab_name_to_remove]

            widget.deleteLater()
            self.ui.tabs.removeTab(index)

    # BUTTON CLICK HANDLERS
    # ///////////////////////////////////////////////////////////////
    def open_dashboard_tab(self):
        self.open_or_focus_tab("Dashboard", DashboardWidget)

    def open_pomodoro_tab(self):
        self.open_or_focus_tab("Pomodoro", PomodoroWidget)

    def open_checklist_tab(self):
        self.open_or_focus_tab("Checklist", ChecklistWidget)

    def open_settings_tab(self):
        self.open_or_focus_tab("Configurações", SettingsWidget)

    # UI UPDATE FUNCTIONS
    # ///////////////////////////////////////////////////////////////
    def update_active_button(self, tab_name):
        self.reset_selection()
        if tab_name == "Dashboard":
            self.ui.btn_dashboard.set_active(True)
        elif tab_name == "Pomodoro":
            self.ui.btn_pomodoro.set_active(True)
        elif tab_name == "Checklist":
            self.ui.btn_checklist.set_active(True)
        elif tab_name == "Configurações":
            self.ui.settings_btn.set_active(True)

    def reset_selection(self):
        for btn in self.ui.left_menu.findChildren(QPushButton):
            try:
                btn.set_active(False)
            except:
                pass

    # ANIMATION
    # ///////////////////////////////////////////////////////////////
    def toggle_button(self):
        menu_width = self.ui.left_menu.width()
        width = 50
        if menu_width == 50:
            width = 240

        self.animation = QPropertyAnimation(self.ui.left_menu, b"minimumWidth")
        self.animation.setStartValue(menu_width)
        self.animation.setEndValue(width)
        self.animation.setDuration(500)
        self.animation.setEasingCurve(QEasingCurve.InOutCirc)
        self.animation.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    window = MainWindow(app)
    sys.exit(app.exec())
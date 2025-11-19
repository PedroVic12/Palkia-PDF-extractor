# ///////////////////////////////////////////////////////////////
#
# BY: Pedro Victor Rodrigues Veras (based on Wanderson M. Pimenta)
# PROJECT MADE WITH: Qt Designer and PySide6
# V: 10.0.0 (Final Architecture)
#
# ///////////////////////////////////////////////////////////////

# IMPORT MODULES
import sys
import os 
import webbrowser
from functools import partial

# IMPORT QT CORE
from qt_core import *

# IMPORT STYLES
from styles import DARK_STYLE, LIGHT_STYLE

# IMPORT MODEL
from settings_model import SettingsModel

# IMPORT MAIN WINDOW
from gui.windows.main_window.ui_main_window import UI_MainWindow

# IMPORT IFRAME WIDGETS (pagina separadas para cada TAB)
from gui.iframes.dashboard_widget import DashboardWidget
from gui.iframes.pomodoro_widget import PomodoroWidget
from gui.iframes.checklist_widget import ChecklistWidget
from gui.iframes.settings_widget import SettingsWidget

# IMPORT SIDE MENU WIDGETS
from gui.side_menus.navigation_menu import NavigationMenu
from gui.side_menus.checklist_sidemenu import ChecklistSideMenu
from gui.side_menus.default_sidemenu import DefaultSideMenu

# IMPORT CUSTOM WIDGETS
from gui.widgets.py_text_button import PyTextButton
from gui.widgets.py_iframe_header import PyIframeHeader # Importa o novo cabeçalho para iframes

# MAIN WINDOW
class MainWindow(QMainWindow):
    """A janela principal da aplicação, gerenciando a UI, navegação, configurações e Iframes."""
    def __init__(self, app):
        """
        Inicializa a MainWindow.

        Args:
            app (QApplication): A instância da aplicação Qt.
        """
        super().__init__()
        self.app = app 

        # --- DICIONÁRIOS PARA GERENCIAR WIDGETS DINÂMICOS ---
        self.open_tabs = {} # Armazena os widgets das abas abertas
        self.side_menus = {} # Armazena os widgets dos menus laterais (por nome de classe)
        self.tab_to_side_menu_map = {} # Mapeia widgets de aba para seus respectivos side menus

        # --- CONFIGURA A JANELA PRINCIPAL E A UI ---
        self.ui = UI_MainWindow() # Instância da UI gerada pelo Qt Designer
        self.ui.setup_ui(self)

        # --- CONFIGURA O MODELO DE CONFIGURAÇÕES E APLICA AS CONFIGURAÇÕES INICIAIS ---
        self.settings_model = SettingsModel() # Modelo para gerenciar configurações da aplicação
        self.settings_model.settings_changed.connect(self.apply_settings_from_model) # Conecta sinal para aplicar mudanças
        self.apply_settings_from_model() # Aplica as configurações ao iniciar

        # --- CONFIGURA MÓDULOS DE UI DINÂMICOS ---
        self.navigation_menu = NavigationMenu() # Menu de navegação principal
        self.ui.left_menu_layout.insertWidget(0, self.navigation_menu)



        self.side_menu_stack = QStackedWidget() # Stack para gerenciar múltiplos menus laterais
        self.default_side_menu = DefaultSideMenu() # Menu lateral padrão
        self.side_menus['default'] = self.default_side_menu
        self.side_menu_stack.addWidget(self.default_side_menu)
        self.ui.left_menu_layout.insertWidget(1, self.side_menu_stack)

        self._setup_appbar_links() # Configura os links na barra superior
        
        # --- CONECTA OS SINAIS ---
        self.connect_signals()

        # --- ABRE A ABA INICIAL ---
        self.open_dashboard_tab()

        # --- MOSTRA O APLICATIVO ---
        self.show()

    def connect_signals(self):
        """Conecta os sinais de elementos da UI aos seus respectivos slots (funções de tratamento)."""
        # Navegação Principal
        self.navigation_menu.dashboard_requested.connect(self.open_dashboard_tab)
        self.navigation_menu.pomodoro_requested.connect(self.open_pomodoro_tab)
        self.navigation_menu.checklist_requested.connect(self.open_checklist_tab)
        self.navigation_menu.settings_requested.connect(self.open_settings_tab)
        

        # Outros elementos da UI
        self.ui.toggle_button.clicked.connect(self.toggle_button) # Botão para expandir/recolher menu
        self.ui.tabs.currentChanged.connect(self.on_tab_changed) # Sinal para mudança de aba
        self.ui.tabs.tabCloseRequested.connect(self.close_tab) # Sinal para fechamento de aba

    def _setup_appbar_links(self):
        """Configura os botões de link na barra superior da aplicação."""
        links = {
            "🌍 GitHub": "https://github.com/PedroVic12",
            "⚽ Probabilidades": "https://www.mat.ufmg.br/futebol/classificacao-para-libertadores_seriea/",
            "📚 Habit Tracker": "https://gohann-treinamentos-web-app-one.vercel.app",
            "⚡ SEP para Leigos": "https://electrical-system-simulator.vercel.app/"
        }
        for text, url in links.items():
            btn = PyTextButton(text=text)
            btn.setToolTip(f"Abrir {url} no navegador")
            btn.clicked.connect(partial(webbrowser.open, url)) # Abre o URL no navegador padrão
            self.ui.top_bar_layout.addWidget(btn)

    # LÓGICA CENTRAL DA UI
    # ///////////////////////////////////////////////////////////////
    def open_or_focus_tab(self, tab_name, main_widget_class, side_menu_class=None):
        """
        Abre uma nova aba ou foca em uma aba existente com o widget especificado.

        Args:
            tab_name (str): O nome da aba a ser aberta/focada.
            main_widget_class (QWidget): A classe do widget principal a ser exibido na aba.
            side_menu_class (QWidget, optional): A classe do menu lateral a ser associado a esta aba. Defaults to None.
        """
        if tab_name in self.open_tabs:
            # Se a aba já está aberta, apenas a torna visível
            self.ui.tabs.setCurrentWidget(self.open_tabs[tab_name])
        else:
            # Se a aba não está aberta, cria uma nova
            side_menu_widget = None
            if side_menu_class:
                # Cria ou reutiliza o widget do menu lateral associado
                if side_menu_class.__name__ not in self.side_menus:
                    side_menu_widget = side_menu_class()
                    self.side_menus[side_menu_class.__name__] = side_menu_widget
                    self.side_menu_stack.addWidget(side_menu_widget)
                else:
                    side_menu_widget = self.side_menus[side_menu_class.__name__]
            
            # Cria o widget principal do iframe
            main_widget = main_widget_class(side_menu=side_menu_widget) # Passa o side_menu para o widget, se houver

            # Cria o cabeçalho do iframe usando PyIframeHeader
            iframe_header = PyIframeHeader(title_text=tab_name)

            # Cria um layout vertical para o cabeçalho e o conteúdo principal do iframe
            iframe_layout = QVBoxLayout()
            iframe_layout.setContentsMargins(0, 0, 0, 0)
            iframe_layout.setSpacing(0)
            iframe_layout.addWidget(iframe_header)
            iframe_layout.addWidget(main_widget)
            
            # Cria um QWidget container para o iframe_layout (cabeçalho + conteúdo)
            iframe_container = QWidget()
            iframe_container.setLayout(iframe_layout)

            # Adiciona o container (com cabeçalho e conteúdo) como uma nova aba
            index = self.ui.tabs.addTab(iframe_container, tab_name)
            self.ui.tabs.setCurrentIndex(index)
            self.open_tabs[tab_name] = iframe_container # Armazena o container completo
            if side_menu_widget:
                self.tab_to_side_menu_map[iframe_container] = side_menu_widget # Mapeia o container para o side menu
        
        self.navigation_menu.set_active_button(tab_name) # Ativa o botão correspondente no menu de navegação

    @Slot(int)
    def on_tab_changed(self, index):
        """
        Slot chamado quando a aba atualmente selecionada é alterada.
        Atualiza o menu lateral e o botão ativo no menu de navegação.

        Args:
            index (int): O índice da nova aba ativa.
        """
        current_tab_widget = self.ui.tabs.widget(index)
        side_menu = self.tab_to_side_menu_map.get(current_tab_widget)
        if side_menu:
            self.side_menu_stack.setCurrentWidget(side_menu) # Mostra o side menu específico da aba
        else:
            self.side_menu_stack.setCurrentWidget(self.default_side_menu) # Volta para o side menu padrão
        
        tab_name = self.ui.tabs.tabText(index)
        self.navigation_menu.set_active_button(tab_name) # Ativa o botão correspondente no menu de navegação

    @Slot(int)
    def close_tab(self, index):
        """
        Slot chamado quando uma aba é solicitada para ser fechada.

        Args:
            index (int): O índice da aba a ser fechada.
        """
        widget = self.ui.tabs.widget(index)
        if widget:
            tab_name = self.ui.tabs.tabText(index)
            if tab_name in self.open_tabs:
                del self.open_tabs[tab_name] # Remove do dicionário de abas abertas
            if widget in self.tab_to_side_menu_map:
                del self.tab_to_side_menu_map[widget] # Remove do mapeamento side menu
            widget.deleteLater() # Agenda a exclusão do widget
            self.ui.tabs.removeTab(index) # Remove a aba da interface

    # HANDLERS DE NAVEGAÇÃO
    # ///////////////////////////////////////////////////////////////
    def open_dashboard_tab(self): """Abre a aba do Dashboard.""" ; self.open_or_focus_tab("Dashboard", DashboardWidget)
    def open_pomodoro_tab(self): """Abre a aba do Pomodoro.""" ; self.open_or_focus_tab("Pomodoro", PomodoroWidget)
    def open_checklist_tab(self): """Abre a aba do Checklist.""" ; self.open_or_focus_tab("Checklist", ChecklistWidget, ChecklistSideMenu)
    def open_settings_tab(self): """Abre a aba de Configurações.""" ; self.open_or_focus_tab("Configurações", SettingsWidget)

    # CONFIGURAÇÕES
    # ///////////////////////////////////////////////////////////////
    @Slot()
    def apply_settings_from_model(self):
        """
        Aplica as configurações da aplicação (tema, fonte) com base no SettingsModel.
        É chamado ao iniciar e quando as configurações são alteradas.
        """
        theme = self.settings_model.get("theme")
        self.app.setStyleSheet(DARK_STYLE if theme == "dark" else LIGHT_STYLE) # Aplica o estilo CSS do tema
        font = QFont(self.settings_model.get("font_family"), self.settings_model.get("font_size"))
        self.app.setFont(font) # Aplica a fonte
        if "Configurações" in self.open_tabs:
            # Se a aba de configurações estiver aberta, atualiza seu estilo
            widget = self.open_tabs["Configurações"]
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.update()

    @Slot(dict)
    def handle_settings_saved(self, settings_dict):
        """Slot para lidar com configurações salvas, atualizando o modelo e aplicando-as."""
        self.settings_model.set_and_save(settings_dict)

    # ANIMAÇÃO
    # ///////////////////////////////////////////////////////////////
    def toggle_button(self):
        """Alterna a largura do menu lateral com uma animação, expandindo-o ou recolhendo-o."""
        menu_width = self.ui.left_menu.width()
        width = 0 if menu_width > 0 else 240 # Define a largura final (recolhido ou expandido)
        self.animation = QPropertyAnimation(self.ui.left_menu, b"minimumWidth")
        self.animation.setStartValue(menu_width)
        self.animation.setEndValue(width)
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.animation.start()

        # Animação para maximumWidth para garantir que o menu recolha/expanda corretamente
        self.animation2 = QPropertyAnimation(self.ui.left_menu, b"maximumWidth")
        self.animation2.setStartValue(menu_width)
        self.animation2.setEndValue(width)
        self.animation2.setDuration(300)
        self.animation2.setEasingCurve(QEasingCurve.InOutCubic)
        self.animation2.start()

if __name__ == "__main__":
    # Bloco de execução principal para iniciar a aplicação
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico")) # Define o ícone da janela
    
    # Para teste individual (pode ser removido se o app principal for outro)
    window = MainWindow(app)
    window.show() # Mostra a janela principal
    
    sys.exit(app.exec()) # Inicia o loop de eventos da aplicação
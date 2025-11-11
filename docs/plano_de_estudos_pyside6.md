# Plano de Estudos: Criando Novas Páginas com PySide6

Este plano de estudos tem como objetivo guiá-lo no processo de criação e integração de novas páginas (widgets) em um aplicativo de desktop PySide6, utilizando como base a arquitetura modular e escalável do projeto `pyside6_tab_app`.

## 1. Entendendo a Arquitetura do `app_template_desktop.py`

Antes de criar novas páginas, é fundamental entender como a aplicação principal (`MainWindow`) gerencia as janelas, abas e menus.

- **`MainWindow`**: É a classe principal que orquestra toda a aplicação. Ela é responsável por:
    - Carregar a interface principal (`ui_main_window.py`).
    - Gerenciar um `QStackedWidget` para os menus laterais.
    - Gerenciar um `QTabWidget` para as páginas principais.
    - Conectar os sinais dos botões de navegação com as funções que abrem as páginas.

- **Gerenciamento Dinâmico de Abas e Menus**:
    - **`self.open_tabs`**: Um dicionário que armazena as abas atualmente abertas para evitar duplicatas.
    - **`self.side_menus`**: Um dicionário que armazena as instâncias dos menus laterais.
    - **`self.tab_to_side_menu_map`**: Mapeia uma aba ao seu menu lateral correspondente.
    - **`open_or_focus_tab()`**: A função central que verifica se uma aba já está aberta e a foca, ou cria uma nova aba e seu menu lateral associado (se houver).

- **Estrutura de Pastas**:
    - `gui/iframes/`: Onde os widgets de cada página (o conteúdo principal) são definidos.
    - `gui/side_menus/`: Onde os menus laterais específicos de cada página são definidos.
    - `gui/windows/main_window/`: Contém a UI da janela principal.

## 2. Passo a Passo: Criando uma Nova Página

Criar uma interface com "páginas" usando QStackedWidget
Para replicar a ideia de "iframes", onde diferentes conteúdos são exibidos em uma área, você usará o QStackedWidget.
Crie sua interface principal:
Abra o Qt Designer.
Crie um novo QMainWindow.
Na "Widget Box" (caixa de widgets) à esquerda, procure por QStackedWidget e arraste-o para sua janela.
Crie suas "sub-interfaces":
No "Widget Box", arraste um QWidget para o QStackedWidget. Ele será sua primeira página.
Para adicionar outra página, selecione o QStackedWidget na barra de "Object Inspector" (geralmente à direita) e clique com o botão direito para selecionar Adicionar página > Adicionar página após a página atual.
Para cada página, adicione os widgets desejados, como botões, rótulos e caixas de texto.
Adicione um controle para trocar as páginas:
Fora do QStackedWidget, adicione um QPushButton ou QComboBox para controlar qual página está visível.
Salve o arquivo .ui. Salve seu design com um nome como main_window.ui. 
4. Converter o arquivo .ui para Python
Use o comando pyside6-uic para gerar o código Python correspondente.
sh
pyside6-uic main_window.ui -o ui_main_window.py
Use o código com cuidado.

Isso criará o arquivo ui_main_window.py.

Vamos criar uma página de exemplo chamada "**Análise de Dados**".

### Passo 2.1: Criar o Widget da Página Principal

1.  **Crie o arquivo do widget**:
    - Vá para a pasta `pyside6_tab_app/gui/iframes/`.
    - Crie um novo arquivo Python chamado `analise_dados_widget.py`.

2.  **Escreva o código do widget**:
    - Este widget será o conteúdo da sua nova aba. Por enquanto, pode ser um `QWidget` simples com um `QLabel`.

    ```python
    # pyside6_tab_app/gui/iframes/analise_dados_widget.py
    from qt_core import QWidget, QLabel, QVBoxLayout

    class AnaliseDadosWidget(QWidget):
        def __init__(self, side_menu=None):
            super().__init__()
            self.side_menu = side_menu # Importante para interagir com o menu lateral
            self.layout = QVBoxLayout(self)
            self.label = QLabel("Página de Análise de Dados")
            self.layout.addWidget(self.label)
    ```

### Passo 2.2: (Opcional) Criar um Menu Lateral Específico

Se a sua página precisar de controles específicos, você pode criar um menu lateral para ela.

1.  **Crie o arquivo do menu**:
    - Vá para a pasta `pyside6_tab_app/gui/side_menus/`.
    - Crie um novo arquivo Python chamado `analise_dados_sidemenu.py`.

2.  **Escreva o código do menu**:
    - Este widget conterá os botões e controles do menu lateral.

    ```python
    # pyside6_tab_app/gui/side_menus/analise_dados_sidemenu.py
    from qt_core import QWidget, QVBoxLayout
    from gui.widgets.py_text_button import PyTextButton # Reutilize seus botões!

    class AnaliseDadosSideMenu(QWidget):
        def __init__(self):
            super().__init__()
            self.layout = QVBoxLayout(self)
            self.btn_1 = PyTextButton(text="Filtro A")
            self.btn_2 = PyTextButton(text="Filtro B")
            self.layout.addWidget(self.btn_1)
            self.layout.addWidget(self.btn_2)
    ```

## 3. Integrando a Nova Página na Aplicação

Agora, vamos fazer a `MainWindow` conhecer nossa nova página.

### Passo 3.1: Importar os Novos Widgets

- Abra o arquivo `pyside6_tab_app/main.py`.
- Importe as novas classes que você criou no topo do arquivo:

    ```python
    # ... outros imports
    from gui.iframes.analise_dados_widget import AnaliseDadosWidget
    from gui.side_menus.analise_dados_sidemenu import AnaliseDadosSideMenu # Se você criou um
    ```

### Passo 3.2: Adicionar um Botão de Navegação

- No `pyside6_tab_app/gui/side_menus/navigation_menu.py`, adicione um novo botão para a sua página e emita um sinal quando ele for clicado.

    ```python
    # pyside6_tab_app/gui/side_menus/navigation_menu.py
    class NavigationMenu(QWidget):
        # ...
        analise_dados_requested = Signal() # 1. Defina o sinal

        def __init__(self):
            # ...
            self.analise_dados_btn = PyTextButton(text="Análise") # 2. Crie o botão
            self.analise_dados_btn.clicked.connect(self.analise_dados_requested) # 3. Conecte o sinal
            self.layout.addWidget(self.analise_dados_btn) # 4. Adicione ao layout
    ```

### Passo 3.3: Conectar o Sinal na `MainWindow`

- De volta ao `pyside6_tab_app/main.py`, conecte o novo sinal do menu de navegação a uma função que abrirá a aba.

    ```python
    # pyside6_tab_app/main.py
    class MainWindow(QMainWindow):
        def connect_signals(self):
            # ...
            self.navigation_menu.analise_dados_requested.connect(self.open_analise_dados_tab) # Conecte aqui

        # ...

        # Crie a função para abrir a aba
        def open_analise_dados_tab(self):
            self.open_or_focus_tab(
                "Análise de Dados",
                AnaliseDadosWidget,
                AnaliseDadosSideMenu # Passe a classe do menu lateral aqui
            )
    ```

## 4. Próximos Passos e Tópicos Avançados

- **Interação entre Página e Menu Lateral**:
    - Use sinais e slots para comunicar o menu lateral com a página. Por exemplo, um clique de botão no `AnaliseDadosSideMenu` pode emitir um sinal que é capturado pelo `AnaliseDadosWidget` para atualizar um gráfico.

- **Estilização**:
    - Explore o arquivo `styles.py` para ver como os temas `DARK_STYLE` e `LIGHT_STYLE` são definidos e como você pode adicionar estilos específicos para seus novos widgets.

- **Persistência de Dados (`settings_model.py`)**:
    - Se sua nova página tiver configurações que precisam ser salvas, estude como o `SettingsWidget` interage com o `SettingsModel` para salvar e carregar configurações de um arquivo JSON. Você pode replicar esse padrão.

- **Ícones**:
    - Adicione um novo ícone para sua página em `gui/images/icons/` e use-o no `PyTextButton` do menu de navegação.

Seguindo estes passos, você poderá adicionar quantas páginas forem necessárias, mantendo seu código organizado e escalável.

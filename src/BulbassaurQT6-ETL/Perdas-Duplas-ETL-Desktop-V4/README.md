# Sistema de Ferramentas RPA

Este projeto implementa um sistema de ferramentas RPA (Robotic Process Automation) com uma interface gráfica construída utilizando PySide6. O objetivo principal é fornecer um ambiente modular para automação de tarefas relacionadas a ETL (Extração, Transformação, Carga) de documentos PDF e Excel, além de outras funcionalidades de controle e gestão.

## Visão Geral da Arquitetura

A aplicação segue uma arquitetura modular baseada em MVC (Model-View-Controller):

-   **app_template_desktop.py**: É a janela principal da aplicação, responsável pela estrutura geral, navegação entre abas (Iframes) e gerenciamento de menus laterais.
-   **gui/iframes/**: Contém os widgets (Iframes) que representam as diferentes funcionalidades da aplicação, como o Dashboard, Pomodoro, Checklist e a ferramenta de Análise de Perdas Duplas.
-   **app/controllers/etl_repository.py**: Contém a lógica de ETL para processamento de PDFs e outros dados, separando a regra de negócio da interface do usuário.
-   **gui/widgets/py_iframe_header.py**: Um widget reutilizável para criar cabeçalhos padronizados para cada Iframe.

## Configuração do Ambiente

Para configurar e executar o projeto, siga os passos abaixo:

1.  **Clone o repositório**:
    ```bash
    git clone <URL_DO_SEU_REPOSITORIO>
    cd Palkia-PDF-extractor/src/NexusPy/Pyside6 - Desktop/pyside6_tab_app/
    ```

2.  **Crie e ative um ambiente virtual** (recomendado):
    ```bash
    python -m venv venv
    # No Windows
    .\venv\Scripts\activate
    # No macOS/Linux
    source venv/bin/activate
    ```

3.  **Instale as dependências**:
    ```bash
    pip install PySide6 pandas PyMuPDF
    ```

## Como Executar a Aplicação

Após configurar o ambiente e instalar as dependências, você pode executar a aplicação principal:

```bash
python app_template_desktop.py
```

## Principais Funcionalidades

As funcionalidades atuais incluem:

-   **Navegação por Abas (Iframes)**: Permite abrir e alternar entre diferentes ferramentas em abas separadas.
-   **Menu Lateral Responsivo**: Exibe opções relevantes para a aba ativa.
-   **Links Externos na Barra Superior**: Acesso rápido a URLs importantes.
-   **Customização de Tema e Fonte**: O usuário pode alterar o tema (claro/escuro), família e tamanho da fonte.
-   **Análise de Perdas Duplas (ETL)**: Uma ferramenta para processar PDFs, extrair dados de contingências duplas e exportar resultados para Excel.

Para mais detalhes sobre os requisitos e o planejamento do projeto, consulte o arquivo `docs/todo.md`.

## Como Adicionar Novos Iframes (Módulos de Ferramentas)

Para adicionar uma nova ferramenta (Iframe) à aplicação, siga estes passos:

1.  **Crie o arquivo do Widget**: Crie um novo arquivo Python para o seu widget na pasta `gui/iframes/`. Este arquivo deve conter uma classe que herda de `QWidget` (ou `QFrame`, `QScrollArea`, etc.) e implemente sua interface de usuário (`setup_ui`) e lógica.

    Exemplo (`meu_novo_widget.py`):
    ```python
    from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
    from PySide6.QtCore import Slot

    class MeuNovoWidget(QWidget):
        def __init__(self, side_menu=None, parent=None):
            super().__init__(parent)
            self.side_menu = side_menu
            self.setup_ui()

        def setup_ui(self):
            layout = QVBoxLayout(self)
            label = QLabel("Bem-vindo ao Meu Novo Widget!")
            layout.addWidget(label)
            # Adicione seus componentes e lógica aqui
    ```

2.  **Importe o Novo Widget**: Abra o arquivo `app_template_desktop.py` e adicione a importação do seu novo widget:

    ```python
    # IMPORT IFRAME WIDGETS (pagina separadas para cada TAB)
    from gui.iframes.dashboard_widget import DashboardWidget
    # ... outros imports ...
    from gui.iframes.meu_novo_widget import MeuNovoWidget # Seu novo widget
    ```

3.  **Crie uma função para abrir a aba**: Ainda em `app_template_desktop.py`, adicione um novo método na classe `MainWindow` para abrir seu widget:

    ```python
    # NAVIGATION HANDLERS
    # ///////////////////////////////////////////////////////////////
    # ... outras funções open_tab ...
    def open_meu_novo_tab(self): self.open_or_focus_tab("Meu Novo Módulo", MeuNovoWidget)
    ```

4.  **Adicione um botão de navegação (opcional)**: Se você quiser que seu novo módulo apareça no menu lateral, adicione um `PyTextButton` na `MainWindow.__init__` de `app_template_desktop.py` e conecte-o à função que você acabou de criar:

    ```python
    # ... dentro de MainWindow.__init__ ...
    self.navigation_menu = NavigationMenu()
    self.ui.left_menu_layout.insertWidget(0, self.navigation_menu)

    # Exemplo: botão para o novo widget
    btn_meu_novo = PyTextButton(text="✨ Meu Novo Módulo")
    btn_meu_novo.clicked.connect(self.open_meu_novo_tab)
    self.navigation_menu.layout().addWidget(btn_meu_novo)
    ```

    *Nota*: Certifique-se de adicionar este botão em uma posição lógica no seu layout do `navigation_menu`.

5.  **Gerenciamento de Side Menu (Opcional)**: Se o seu novo Iframe precisar de um menu lateral específico, crie uma classe de Side Menu (`MeuNovoSideMenu`) na pasta `gui/side_menus/` e passe-a como terceiro argumento para `open_or_focus_tab`:

    ```python
    from gui.side_menus.meu_novo_sidemenu import MeuNovoSideMenu # Importe aqui
    # ...
    def open_meu_novo_tab(self): self.open_or_focus_tab("Meu Novo Módulo", MeuNovoWidget, MeuNovoSideMenu)
    ```

Ao seguir esses passos, você pode facilmente expandir a aplicação com novas funcionalidades de forma modular e organizada.

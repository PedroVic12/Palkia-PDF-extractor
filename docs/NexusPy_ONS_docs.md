# Pyside6 desktop: NexusPy 

Caixa de Ferramentas ONS - Controle e Gestão de automações e Análise de SP/RJ (perdas duplas) assim como controle de requerimentos para MUST com automação de relátorios

---

## 1. Visão Geral e Arquitetura

**Objetivo do Projeto**: Software de Controle e Gestão de automações para a equipe de curto prazo do ONS (PLC). O software facilitará a automação de tarefas, análise de dados e visualização de estudos de sistemas elétricos de potência (SEP).

Possui integrações com o Plugin Notepad++, AnaREDE, Organon e 

**Arquitetura Principal**: **Model-View-Controller (MVC)**. Esta arquitetura é ideal para organizar a complexidade do projeto, separando a lógica de dados, a interface do usuário e o controle da aplicação.

-   **Model (Modelo)**: a lógica de negócio, as classes que representam os dados (ex: `Usina`, `Linha`) e os scripts de automação com conexão ao banco de Dados
-   **View (Visão)**: A interface gráfica (GUI) construída com PySide6. Contém as janelas, abas, botões e gráficos. É responsável por exibir dados e capturar as ações do usuário.
-   **Controller (Controlador)**: O intermediário que conecta o Model e a View. Recebe ações da View, aciona a lógica no Model e atualiza a View com os resultados. É possivel usar pandas, flask e análise de dados para tomada de decisões. assim como solver e machine learning 

## 2. Roadmap de Desenvolvimento Gamificado

Cada tarefa é projetada para ser concluída em blocos de tempo focados, com pontos de experiência (XP) para marcar seu progresso.

**Níveis de Dificuldade:**
-   **Fácil**: 10 XP
-   **Médio**: 25 XP
-   **Difícil**: 50 XP
-   **Desafio**: 100 XP (Grandes marcos do projeto)

---

### **Fase 0: Concepção e Planejamento**
*O objetivo desta fase é definir o escopo e preparar o terreno para o desenvolvimento.*

### UI Dinâmica: AppBar e Menu de Contexto

- **AppBar de Links**: O `main.py`, no método `_setup_appbar_links`, popula a barra superior com `PyTextButton`s, conectando cada um para abrir uma URL externa.
- **Menu Lateral Híbrido**: O `main.py`, através do método `on_tab_changed`, gerencia o conteúdo do menu lateral. Ele sempre garante que o menu de navegação principal (`NavigationMenu`) esteja presente e, em seguida, adiciona o menu de contexto específico da aba ativa, criando a experiência "responsiva" que você desejava.

-   [ ] **Tarefa 1**: Detalhar os 3 principais processos/scripts que o OrquestraPy irá automatizar. Descrever as entradas, o processamento esperado e as saídas desejadas para cada um. `[50 min | Médio | 25 XP]`
-   [ ] **Tarefa 2**: Desenhar um wireframe (esboço em papel ou em software simples) da interface principal e das abas para cada uma das 3 ferramentas. `[50 min | Fácil | 10 XP]`
-   [ ] **Tarefa 3**: Configurar o ambiente de desenvolvimento: criar o repositório Git, configurar o ambiente virtual (`venv`), instalar `PySide6` e criar o arquivo `.gitignore`. `[25 min | Fácil | 10 XP]`
-   [ ] **Tarefa 4**: Criar a estrutura de pastas do projeto (core, ui, controllers) e os arquivos Python iniciais vazios (ex: `main.py`, `main_window.py`, `main_controller.py`). `[25 min | Fácil | 10 XP]`

---

### **Fase 1: Fundação da Aplicação (MVC Básico)**
*O objetivo é ter uma janela funcional que abre e fecha, com a estrutura MVC conectada.*

-   [ ] **Tarefa 1**: Na View (`main_window.py`), criar a classe `MainWindow` com um `QTabWidget` central e um menu superior "Arquivo > Sair". `[50 min | Médio | 25 XP]`
-   [ ] **Tarefa 2**: No Controller (`main_controller.py`), criar a lógica para inicializar e exibir a `MainWindow`. `[25 min | Médio | 25 XP]`
-   [ ] **Tarefa 3**: Conectar a ação "Sair" do menu para fechar a aplicação, garantindo a comunicação View -> Controller. `[25 min | Fácil | 10 XP]`
-   [ ] **🏆 DESAFIO 1**: Executar `main.py` e ver a janela principal abrir corretamente. O menu "Sair" deve funcionar. `[Marco | 100 XP]`

---

### **Fase 2: Ferramenta 1 - Visualizador de Dados**
*O objetivo é implementar a primeira ferramenta de ponta a ponta: carregar dados de um arquivo e exibi-los.*

-   [ ] **Tarefa 1**: No Model (`core/models/`), definir as classes de dados para representar os componentes do sistema (ex: `Usina`, `Barra`). `[25 min | Fácil | 10 XP]`
-   [ ] **Tarefa 2**: Na View (`ui/tabs/`), criar a UI da aba "Visualizador" com um botão "Carregar Arquivo" e uma `QTableView`. `[50 min | Médio | 25 XP]`
-   [ ] **Tarefa 3**: No Model (`core/parsers/`), implementar a lógica para ler **apenas uma seção** de um arquivo de dados (ex: a seção de `[USINAS]` de um deck). `[50 min | Difícil | 50 XP]`
-   [ ] **Tarefa 4**: No Controller, implementar a lógica da aba: o clique do botão abre um `QFileDialog`, passa o caminho para o parser do Model e recebe os dados. `[50 min | Difícil | 50 XP]`
-   [ ] **Tarefa 5**: Conectar o Controller à View para exibir os dados recebidos na `QTableView`. `[25 min | Médio | 25 XP]`
-   [ ] **🏆 DESAFIO 2**: Carregar um arquivo de dados e visualizar as informações corretamente na tabela da interface. `[Marco | 100 XP]`

---

### **Fase 3: Ferramenta 2 - Orquestrador de Script**
*O objetivo é executar um script Python externo a partir da UI e capturar seu output.*

-   [ ] **Tarefa 1**: Na View (`ui/tabs/`), criar a UI da aba "Orquestrador" com um botão "Executar" e um `QTextEdit` para exibir os logs. `[25 min | Fácil | 10 XP]`
-   [ ] **Tarefa 2**: No Model (`core/scripts/`), criar um script de exemplo (`script_exemplo.py`) que realiza um cálculo e usa `print()` para gerar um output. `[25 min | Fácil | 10 XP]`
-   [ ] **Tarefa 3**: No Controller, implementar a lógica para executar o script externo usando `QProcess`. Isso é crucial para não travar a UI. `[50 min | Difícil | 50 XP]`
-   [ ] **Tarefa 4**: Capturar os sinais `readyReadStandardOutput` e `readyReadStandardError` do `QProcess` para ler o output do script em tempo real. `[50 min | Difícil | 50 XP]`
-   [ ] **Tarefa 5**: Exibir os logs capturados no `QTextEdit` da View. `[25 min | Médio | 25 XP]`
-   [ ] **🏆 DESAFIO 3**: Clicar em "Executar", ver o script rodar em segundo plano e os logs aparecerem na tela. `[Marco | 100 XP]`

---

### **Fase 4: Deploy e testes**

-   [ ] **Tarefa 1**: Adicionar um seletor de tema (Claro/Escuro) e fazer a aplicação trocar os estilos dinamicamente. `[50 min | Médio | 25 XP]`
-   [ ] **Tarefa 3**: Implementar uma notification popup de status na `MainWindow` para exibir mensagens informativas (ex: "Arquivo carregado", "Script em execução..."). `[25 min | Médio | 25 XP]`
-   [ ] **Tarefa 4**: Gerar a primeira versão executável (`.exe` ou binário) da aplicação usando `PyInstaller`. `[50 min | Médio | 25 XP]`


## 4. Seu Checklist de Desenvolvimento (Próximos Passos)

Agora que a base está pronta, aqui está um guia para você migrar sua aplicação `desktop_MUST_dashboard_UI_05_11.py`.

**Passo 1: Crie o IFrame do Dashboard MUST**
- Crie o arquivo `pyside6_tab_app/gui/iframes/must_dashboard_widget.py`.
- Crie a classe `MustDashboardWidget(QWidget)`.

**Passo 2: Crie o Modelo de Dados do MUST**
- Crie o arquivo `pyside6_tab_app/must_model.py`.
- Mova a classe `DashboardDB` do seu script antigo para este novo arquivo.

**Passo 3: Construa a UI e a Lógica do Dashboard**
- Dentro de `MustDashboardWidget`, importe e instancie seu `MustModel`.
- Recrie a interface que você tinha. Use `QFrame` com `setObjectName("glassCard")` para criar os "containers" com efeito de vidro.
- Conecte os botões e filtros a funções que chamam os métodos do seu modelo para buscar os dados.
- Use `QWebEngineView` para exibir os gráficos do Plotly.

**Passo 4: Crie o Menu de Contexto para o Dashboard**
- Crie `pyside6_tab_app/gui/side_menus/must_sidemenu.py`.
- Adicione os widgets de filtro que você precisa (ComboBox de empresa, ano, etc.) e faça com que emitam sinais.

**Passo 5: Integre Tudo no `main.py`**
- Em `main.py`, importe suas novas classes `MustDashboardWidget` e `MustSideMenu`.
- Altere o método `open_dashboard_tab` para que ele abra o seu novo dashboard e associe o menu de contexto a ele:
  ```python
  def open_dashboard_tab(self):
      self.open_or_focus_tab("Dashboard MUST", MustDashboardWidget, MustSideMenu)
  ```
- No `MustDashboardWidget`, conecte os sinais do menu lateral para que os gráficos e tabelas sejam atualizados quando um filtro for alterado.

## 5. Como Adicionar Novas Abas com Qt Designer

O processo para adicionar novas abas com o Designer continua o mesmo:
1.  **Desenhe** sua interface em um arquivo `.ui` usando o Qt Designer.
2.  **Converta** o `.ui` para `.py` com o comando `pyside6-uic`.
3.  **Crie** a classe do seu widget que herda de `QWidget` e da classe da UI gerada, implementando a lógica.
4.  **Integre** em `main.py`, importando sua nova classe e chamando `open_or_focus_tab` a partir de um sinal (ex: clique de um botão no `NavigationMenu`).


---

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

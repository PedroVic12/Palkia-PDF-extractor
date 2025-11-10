# Documentação do Projeto PySide6 - PVRV

Este documento serve como um guia completo para o desenvolvimento de aplicações desktop com PySide6, cobrindo desde a análise de projetos existentes até a criação de uma nova aplicação do zero, seguindo as melhores práticas de arquitetura de software.

## 1. Resumo dos Arquivos do Projeto `Pyside6 - Desktop/`

Abaixo está um resumo dos principais arquivos e diretórios encontrados no projeto `Pyside6 - Desktop/`, que serve como base de estudo.

### 1.1. `Pyside6 - Desktop/PySide6-main-desktop/`

Este é um projeto de template de aplicação desktop completo e bem estruturado.

- **`main.py`**: Ponto de entrada da aplicação. Cria a `QMainWindow` e conecta os sinais (cliques de botão) aos slots (funções que executam ações, como trocar de página).
- **`qt_core.py`**: Um arquivo de conveniência que importa todas as classes comuns do PySide6 (`QtCore`, `QtGui`, `QtWidgets`). Isso evita a necessidade de importar de múltiplos módulos em outros arquivos.
- **`gui/`**: Diretório que separa a lógica da interface do usuário (UI).
    - **`windows/main_window/ui_main_window.py`**: Define a estrutura principal da UI (a janela principal). Cria os frames para o menu lateral, a barra superior, a área de conteúdo e a barra inferior. Instancia os botões customizados (`PyPushButton`) e o `QStackedWidget` que gerencia as páginas.
    - **`pages/ui_pages.py`**: Gerado a partir do `pages.ui` (arquivo do Qt Designer). Define o layout das diferentes "páginas" que são exibidas no `QStackedWidget`.
    - **`widgets/py_push_button.py`**: Um exemplo de widget customizado. Cria um `QPushButton` com estilo e ícone próprios, demonstrando como estender componentes do Qt.
    - **`images/icons/`**: Contém os ícones SVG usados na interface.

**Arquitetura:** A aplicação usa um `QStackedWidget` para simular a navegação entre páginas. Clicar em um botão no menu lateral simplesmente muda a página visível no `QStackedWidget`. É uma abordagem simples e eficaz para aplicações com um número fixo de telas.

### 1.2. `Pyside6 - Desktop/PySide6 + SQL + Solver + Automate + AI - project/`

Este diretório contém scripts mais complexos que integram PySide6 com outras tecnologias.

- **`modelo_recomendacao_MUST.py`**: Uma aplicação avançada que demonstra:
    - **GUI com Abas (`QTabWidget`)**: Cria uma interface com múltiplas abas para diferentes funcionalidades (Dashboard, Análise ML, Chatbot).
    - **Machine Learning**: Usa `scikit-learn` para treinar um modelo de classificação de texto.
    - **Threading**: Usa `QThread` para executar tarefas demoradas (treinamento de ML e chamadas de API) sem travar a interface do usuário.
    - **Integração com API**: Conecta-se a uma API externa (Gemini) para funcionalidade de chatbot.
    - **Visualização de Dados**: Usa `matplotlib` para plotar gráficos de métricas de ML diretamente na interface.
- **`plot_atividades_SP_dataset.py`**: Script de análise de dados que usa `pandas` para ler um arquivo Excel e `matplotlib` para gerar um gráfico de barras. Não é uma aplicação GUI, mas um script de automação.
- **`chatbot.py`**: (Arquivo vazio).

### 1.3. Outros Arquivos Notáveis

- **`mvc_app_tabs_template.py`**: Um excelente template que implementa a arquitetura MVC (Model-View-Controller) com um menu em árvore e um `QTabWidget` central. Cada item da árvore pode abrir uma nova aba, que funciona como um "IFrame" (um widget independente).
- **`moderno_desktop_ui_template.py`**: Outro template avançado que demonstra uma arquitetura MVC com componentes reutilizáveis (como `GlassCard` e `CarouselWidget`) e um sistema de abas dinâmicas.
- **`glass_carousel_app.py`**: Um exemplo focado em criar componentes de UI visualmente atraentes com efeito "glassmorphism".

## 2. Arquitetura PySide6 com Abas (IFrames)

A abordagem de usar abas, onde cada aba carrega um módulo independente (semelhante a um IFrame), é ideal para aplicações complexas, pois permite separar as funcionalidades em componentes autônomos.

**Conceito:**
- **`QMainWindow`**: A janela principal que contém a estrutura geral (menu, barra de status, etc.).
- **`QTabWidget`**: O painel central que gerencia as abas.
- **`QWidget` (Módulo/IFrame)**: Cada aba conterá um `QWidget` customizado. Este widget é um módulo independente que encapsula toda a lógica e UI de uma funcionalidade específica (ex: um dashboard, um formulário de cadastro, etc.).

### 2.1. Abordagem sem Qt Designer (Código Puro)

Esta é a abordagem mais flexível e recomendada para aprender os fundamentos.

1.  **`main.py` (Ponto de Entrada)**:
    - Cria a `QApplication` e a `QMainWindow`.
    - Instancia o `QTabWidget` e o define como widget central da `QMainWindow`.
    - Conecta os sinais do menu (ex: cliques em botões ou itens de uma árvore) a *slots* (funções) que irão controlar a criação de abas.

2.  **`main_window.py` (A View Principal)**:
    - Define a classe `MainWindow(QMainWindow)`.
    - No `__init__`, cria o `QTabWidget` e o menu lateral (`QListWidget` ou `QTreeWidget`).
    - Define a lógica para adicionar e remover abas. Uma função `add_tab(widget, title)` pode ser criada para encapsular `self.tabs.addTab(widget, title)`.

3.  **`iframes/` (Diretório de Módulos)**:
    - Crie um diretório para seus módulos, por exemplo, `iframes/`.
    - Para cada funcionalidade, crie um arquivo Python, por exemplo, `dashboard_iframe.py`.
    - Dentro de `dashboard_iframe.py`, defina uma classe que herda de `QWidget`, por exemplo, `class DashboardWidget(QWidget):`.
    - Construa toda a UI e lógica dessa funcionalidade dentro desta classe. Ela é autônoma.

4.  **Conectando Tudo**:
    - Em `main.py` ou `main_window.py`, quando o usuário clica no item de menu "Dashboard":
        - A função (slot) correspondente importa a classe `DashboardWidget` de `iframes.dashboard_iframe`.
        - Instancia o widget: `dashboard = DashboardWidget()`.
        - Adiciona o widget à `QTabWidget`: `self.tabs.addTab(dashboard, "Dashboard")`.

**Vantagem:** Máxima flexibilidade, separação clara de responsabilidades e fácil manutenção.

### 2.2. Abordagem com Qt Designer

O Qt Designer é útil para prototipar layouts rapidamente.

1.  **Crie a Janela Principal (`main_window.ui`)**:
    - No Qt Designer, crie uma `QMainWindow`.
    - Adicione um `QTabWidget` como widget central.
    - Adicione o menu lateral (`QListWidget` ou `QTreeWidget`).

2.  **Crie os "IFrames" (`.ui` separados)**:
    - Para cada módulo, crie um arquivo `.ui` separado. Em vez de `QMainWindow`, comece com um `QWidget`.
    - Desenhe a interface do seu módulo (ex: `dashboard_widget.ui`).

3.  **Converta os `.ui` para `.py`**:
    - Use o comando `pyside6-uic main_window.ui -o ui_main_window.py`.
    - Use o comando `pyside6-uic dashboard_widget.ui -o ui_dashboard_widget.py`.

4.  **Crie as Classes de Lógica**:
    - Crie uma classe `MainWindow` que herda de `QMainWindow` e da classe `Ui_MainWindow` gerada.
    - Crie uma classe `DashboardWidget` que herda de `QWidget` e da classe `Ui_DashboardWidget` gerada. Nesta classe, você implementa a lógica do dashboard.

5.  **Conectando Tudo**:
    - A lógica é a mesma da abordagem sem Designer. Na sua classe `MainWindow`, quando o usuário clica no menu, você importa a classe `DashboardWidget`, a instancia e a adiciona ao `QTabWidget`.

**Vantagem:** Rápida prototipação visual. **Desvantagem:** Requer um passo de compilação (`pyside6-uic`) e pode tornar a estrutura de arquivos um pouco mais complexa.

---

A seguir, iniciarei o levantamento de requisitos para o seu projeto **Pomodoro Todo-List**.

## 3. Projeto Novo: Pomodoro Todo-List App

Vamos construir uma aplicação de produtividade que combina a técnica Pomodoro com uma lista de tarefas (To-Do List).

### 3.1. Levantamento de Requisitos

#### Requisitos Funcionais (RF)
- **RF01**: O usuário deve poder adicionar novas tarefas a uma lista.
- **RF02**: O usuário deve poder marcar tarefas como "concluídas".
- **RF03**: O usuário deve poder remover tarefas da lista.
- **RF04**: O usuário deve poder iniciar um temporizador Pomodoro (25 minutos de foco).
- **RF05**: O usuário deve poder iniciar um temporizador de pausa curta (5 minutos).
- **RF06**: O usuário deve poder iniciar um temporizador de pausa longa (15 minutos, a cada 4 Pomodoros).
- **RF07**: A aplicação deve notificar o usuário (sonora e/ou visualmente) quando um ciclo do temporizador terminar.
- **RF08**: O usuário deve poder selecionar uma tarefa da lista para ser a "tarefa em foco" durante um ciclo Pomodoro.
- **RF09**: A aplicação deve contabilizar quantos ciclos Pomodoro foram concluídos para cada tarefa.

#### Requisitos Não-Funcionais (RNF)
- **RNF01**: A interface deve ser limpa, moderna e intuitiva.
- **RNF02**: Os dados (tarefas) devem ser persistidos localmente em um banco de dados SQLite.
- **RNF03**: A aplicação deve ser responsiva e não travar durante a contagem do temporizador.
- **RNF04**: O código deve seguir a arquitetura MVC (Model-View-Controller) para separação de responsabilidades.
- **RNF05**: A aplicação deve ser desenvolvida em um único arquivo Python para simplicidade inicial, com posterior refatoração para múltiplos arquivos.

### 3.2. Modelagem do Banco de Dados (SQLite)

Criaremos uma única tabela para armazenar as tarefas.

**Tabela: `tarefas`**
- `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT): Identificador único da tarefa.
- `descricao` (TEXT, NOT NULL): O texto da tarefa.
- `concluida` (INTEGER, NOT NULL, DEFAULT 0): Status da tarefa (0 = pendente, 1 = concluída).
- `ciclos_pomodoro` (INTEGER, NOT NULL, DEFAULT 0): Contador de ciclos Pomodoro dedicados a esta tarefa.
- `data_criacao` (TEXT, NOT NULL): Data e hora em que a tarefa foi criada.

### 3.3. Arquitetura do Software (MVC)

- **Model (`model.py`)**:
    - Conterá a classe `TodoModel`.
    - Responsável por toda a interação com o banco de dados SQLite (adicionar, atualizar, remover, consultar tarefas).
    - Emitirá sinais (`Signal`) quando os dados mudarem (ex: `tarefas_alteradas`).

- **View (`view.py`)**:
    - Conterá a classe `PomodoroView(QMainWindow)`.
    - Responsável por construir e exibir a interface gráfica.
    - Não conterá nenhuma lógica de negócio. Apenas exibirá os dados e emitirá sinais quando o usuário interagir (ex: `botao_adicionar_clicado`).
    - Conterá os widgets da UI: lista de tarefas, botões, temporizador, etc.

- **Controller (`controller.py`)**:
    - Conterá a classe `PomodoroController`.
    - O "cérebro" da aplicação.
    - Conectará o Model e a View.
    - Ouvirá os sinais da View (ex: clique de botão), processará a lógica (ex: iniciar o temporizador, pedir ao modelo para adicionar uma tarefa) e atualizará o Model.
    - Ouvirá os sinais do Model (ex: `tarefas_alteradas`) e chamará os métodos da View para atualizar a exibição.

- **`main.py`**:
    - O ponto de entrada.
    - Instanciará o Model, a View e o Controller e iniciará a aplicação.

Este plano estabelece uma base sólida para o desenvolvimento. O próximo passo é criar a estrutura de diretórios e os arquivos iniciais.

### 3.4. Implementação e Explicação do Código

Criei a estrutura de arquivos para a aplicação Pomodoro Todo-List dentro do diretório `pomodoro_todo_app/`. A aplicação foi executada com sucesso.

Agora, vamos entender como cada parte funciona.

#### Como Executar a Aplicação

Para rodar a aplicação, navegue até o diretório `src/SistemaControleGestaoONS_Desktop_MVC` e execute o seguinte comando no seu terminal:

```bash
python -m pomodoro_todo_app.main
```

#### `model.py` - O Guardião dos Dados

- **O que faz?** Esta classe (`TodoModel`) é a única parte do seu código que "sabe" como falar com o banco de dados. Ela lida com a criação da tabela, adição, exclusão, atualização e consulta de tarefas.
- **Como funciona?** Usa o módulo `sqlite3` do Python. Funções como `add_task` e `delete_task` executam comandos SQL para manipular os dados.
- **Sinal `tasks_changed`**: Este é um ponto crucial. Sempre que os dados mudam (uma tarefa é adicionada, por exemplo), o modelo emite o sinal `tasks_changed.emit()`. Isso informa ao resto da aplicação: "Ei, os dados foram atualizados!", sem que o modelo precise saber quem está ouvindo.

#### `view.py` - A Vitrine da Aplicação

- **O que faz?** A classe `PomodoroView` constrói a interface gráfica que você vê na tela. Ela cria os botões, o campo de texto, a lista e o rótulo do temporizador.
- **Como funciona?** Herda de `QMainWindow` e usa widgets do PySide6 (`QPushButton`, `QLabel`, etc.) para montar o layout.
- **Sinais de Interação**: A View emite sinais quando o usuário faz algo. Por exemplo, `add_task_requested.emit(description)` é disparado quando o usuário pressiona Enter no campo de texto. A View não sabe o que vai acontecer com essa informação; ela apenas anuncia a intenção do usuário.
- **Métodos de Atualização**: Possui métodos como `render_tasks` e `update_timer_display` que são chamados pelo Controller para atualizar o que é exibido na tela.

#### `controller.py` - O Cérebro da Operação

- **O que faz?** A classe `PomodoroController` conecta o `Model` e a `View`. Ela contém toda a lógica de negócio.
- **Como funciona?**
    1.  **Ouve a View**: O Controller se conecta aos sinais da View. Quando a View emite `add_task_requested`, o slot `add_task` no Controller é chamado.
    2.  **Processa a Lógica**: Dentro de `add_task`, o Controller diz ao Model: `self._model.add_task(description)`.
    3.  **Ouve o Model**: O Controller também se conecta aos sinais do Model. Quando o Model emite `tasks_changed`, o slot `refresh_tasks` no Controller é chamado.
    4.  **Atualiza a View**: Dentro de `refresh_tasks`, o Controller pede os dados atualizados ao Model (`self._model.get_tasks()`) e os envia para a View para serem exibidos (`self._view.render_tasks(tasks)`).
- **Lógica do Timer**: O Controller também gerencia o `QTimer`, atualizando a contagem regressiva e chamando `update_display` na View a cada segundo.

#### `main.py` - O Ponto de Partida

- **O que faz?** É o arquivo mais simples. Sua única responsabilidade é criar as instâncias do `QApplication`, do `TodoModel`, da `PomodoroView` e do `PomodoroController`, e então iniciar a aplicação. Ele "monta" o quebra-cabeça.

# Documentação do Projeto PySide6 - PVRV

Este documento serve como um guia completo para o desenvolvimento de aplicações desktop com PySide6, cobrindo desde a análise de projetos existentes até a criação de uma nova aplicação do zero, seguindo as melhores práticas de arquitetura de software.

## 1. Resumo dos Arquivos de Estudo

(Esta seção permanece a mesma da análise inicial, servindo como referência.)

...

## 2. Objetivo do Projeto: App com Abas Dinâmicas

Após a análise inicial, o objetivo foi clarificado: usar o template `Pyside6 - Desktop/PySide6-main-desktop/` como base para criar uma nova aplicação, mas com uma mudança fundamental na arquitetura: substituir o sistema de páginas (`QStackedWidget`) por um sistema de **abas dinâmicas (`QTabWidget`)**.

Cada item do menu lateral deve abrir uma funcionalidade (um "IFrame") em sua própria aba, permitindo que várias funcionalidades fiquem abertas ao mesmo tempo.

## 3. Processo de Desenvolvimento e Refatoração

Para atingir o objetivo, seguimos os seguintes passos:

### Passo 1: Limpeza e Preparação

- O diretório `pomodoro_todo_app` da primeira tentativa (com arquitetura MVC) foi removido, pois não seguia a estrutura de template desejada.
- Um novo diretório, `pyside6_tab_app`, foi criado para abrigar o novo projeto.

### Passo 2: Copiar o Template Base

- Todo o conteúdo do projeto `Pyside6 - Desktop/PySide6-main-desktop/` foi copiado para o novo diretório `pyside6_tab_app`. Isso nos deu um ponto de partida funcional com a estética e a estrutura de menu desejadas.

### Passo 3: Refatorar a UI para Usar Abas (`QTabWidget`)

- O arquivo `pyside6_tab_app/gui/windows/main_window/ui_main_window.py` foi o principal alvo da refatoração.
- O `QStackedWidget` (chamado `self.pages`) foi removido.
- Em seu lugar, um `QTabWidget` (chamado `self.tabs`) foi instanciado.
- Propriedades importantes foram definidas para o `QTabWidget`:
    - `setTabsClosable(True)`: Permite que o usuário feche as abas.
    - `setMovable(True)`: Permite que o usuário reordene as abas.
- O diretório `gui/pages`, que continha as páginas estáticas do `QStackedWidget`, foi removido.

### Passo 4: Criar os Módulos "IFrame"

Para manter o código organizado, criamos o diretório `pyside6_tab_app/gui/iframes/`. Dentro dele, cada funcionalidade principal foi implementada como um `QWidget` autônomo.

1.  **`model.py`**: O modelo de dados da primeira tentativa foi recriado dentro de `pyside6_tab_app/` para ser usado pelo Checklist. Ele agora gerencia sua própria conexão com o banco de dados para ser mais robusto.

2.  **`gui/iframes/pomodoro_widget.py`**:
    - Contém a classe `PomodoroWidget`.
    - Encapsula toda a lógica do temporizador Pomodoro (UI e `QTimer`).
    - É completamente independente e não precisa saber nada sobre o resto da aplicação.

3.  **`gui/iframes/checklist_widget.py`**:
    - Contém a classe `ChecklistWidget`.
    - Instancia seu próprio `TodoModel` para se conectar ao banco de dados `pomodoro_tasks.db`.
    - Constrói a UI da lista de tarefas e conecta os sinais (cliques de botão) aos slots que chamam os métodos do seu modelo (`self.model.add_task()`, etc.).
    - O sinal `tasks_changed` do modelo é conectado a um slot `render_tasks` dentro do widget, atualizando a lista de tarefas automaticamente.

4.  **`gui/iframes/dashboard_widget.py`**:
    - Um widget simples que serve como a página inicial.

### Passo 5: Integrar os Módulos na Janela Principal

- O arquivo `pyside6_tab_app/main.py` foi modificado para orquestrar a nova lógica de abas.
- As classes de widget dos IFrames foram importadas.
- Foi criada a função `open_or_focus_tab(self, name, widget_class)`:
    - Ela verifica se uma aba com um determinado nome já existe.
    - Se existir, apenas foca nela.
    - Se não existir, cria uma nova instância do widget e a adiciona como uma nova aba.
- Os cliques dos botões do menu lateral (`btn_dashboard`, `btn_pomodoro`, etc.) foram conectados para chamar `open_or_focus_tab` com o widget correspondente.
- O sinal `tabCloseRequested` do `QTabWidget` foi conectado a uma função que remove a aba e limpa a referência a ela.

## 4. Código-Fonte Final e Como Executar

### Como Executar a Aplicação

Navegue até o diretório `src/SistemaControleGestaoONS_Desktop_MVC` e execute o seguinte comando no seu terminal:

```bash
python pyside6_tab_app/main.py
```
Um arquivo de banco de dados `pomodoro_tasks.db` será criado no mesmo diretório.

### Código dos Arquivos Principais

<details>
<summary>pyside6_tab_app/main.py</summary>

```python
# ///////////////////////////////////////////////////////////////
#
# BY: Pedro Victor Rodrigues Veras (based on Wanderson M. Pimenta)
# PROJECT MADE WITH: Qt Designer and PySide6
# V: 3.0.0 (Tab-based Refactor)
#
# ///////////////////////////////////////////////////////////////

# IMPORT MODULES
import sys
import os 

# IMPORT QT CORE
from qt_core import *

# IMPORT MAIN WINDOW
from gui.windows.main_window.ui_main_window import UI_MainWindow

# IMPORT IFRAME WIDGETS
from gui.iframes.dashboard_widget import DashboardWidget
from gui.iframes.pomodoro_widget import PomodoroWidget
from gui.iframes.checklist_widget import ChecklistWidget

# PLACEHOLDER for settings
# ===================================================================
class SettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("SETTINGS WIDGET", alignment=Qt.AlignCenter))
# ===================================================================


# MAIN WINDOW
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PySide6 Tab-Based App")

        # SETUP MAIN WINDOW
        self.ui = UI_MainWindow()
        self.ui.setup_ui(self)

        # Store open tabs to avoid duplicates
        # Format: { "tab_name": QWidget_instance }
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

    # TAB MANAGEMENT
    # ///////////////////////////////////////////////////////////////
    def open_or_focus_tab(self, name, widget_class):
        if name in self.open_tabs:
            # Tab already exists, just focus it
            self.ui.tabs.setCurrentWidget(self.open_tabs[name])
        else:
            # Create new tab
            widget = widget_class()
            index = self.ui.tabs.addTab(widget, name)
            self.ui.tabs.setCurrentIndex(index)
            self.open_tabs[name] = widget
        
        self.update_active_button(name)

    def close_tab(self, index):
        widget = self.ui.tabs.widget(index)
        if widget is not None:
            # Find the tab name in our dictionary
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
        # Get menu width
        menu_width = self.ui.left_menu.width()

        # Check with
        width = 50
        if menu_width == 50:
            width = 240

        # Start animation
        self.animation = QPropertyAnimation(self.ui.left_menu, b"minimumWidth")
        self.animation.setStartValue(menu_width)
        self.animation.setEndValue(width)
        self.animation.setDuration(500)
        self.animation.setEasingCurve(QEasingCurve.InOutCirc)
        self.animation.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    window = MainWindow()
    sys.exit(app.exec())
```
</details>

<details>
<summary>pyside6_tab_app/gui/iframes/pomodoro_widget.py</summary>

```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

class PomodoroWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignCenter)

        # Timer setup
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update_timer)
        self._time_left = 0

        self._create_timer_display()
        self._create_buttons()
        
        self.set_time(25 * 60) # Default to Pomodoro time

    def _create_timer_display(self):
        self.timer_label = QLabel()
        self.timer_label.setFont(QFont("Arial", 80, QFont.Bold))
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.timer_label)

    def _create_buttons(self):
        buttons_layout = QHBoxLayout()
        
        self.pomodoro_button = QPushButton("Pomodoro (25 min)")
        self.pomodoro_button.clicked.connect(self.start_pomodoro)
        
        self.short_break_button = QPushButton("Pausa Curta (5 min)")
        self.short_break_button.clicked.connect(self.start_short_break)
        
        self.long_break_button = QPushButton("Pausa Longa (15 min)")
        self.long_break_button.clicked.connect(self.start_long_break)
        
        self.stop_button = QPushButton("Parar")
        self.stop_button.clicked.connect(self.stop_timer)

        buttons_layout.addWidget(self.pomodoro_button)
        buttons_layout.addWidget(self.short_break_button)
        buttons_layout.addWidget(self.long_break_button)
        buttons_layout.addWidget(self.stop_button)
        
        self.main_layout.addLayout(buttons_layout)

    def set_time(self, seconds):
        self._time_left = seconds
        self.update_display()

    def start_timer(self):
        if not self._timer.isActive() and self._time_left > 0:
            self._timer.start(1000)

    def stop_timer(self):
        self._timer.stop()

    def start_pomodoro(self):
        self.stop_timer()
        self.set_time(25 * 60)
        self.start_timer()

    def start_short_break(self):
        self.stop_timer()
        self.set_time(5 * 60)
        self.start_timer()

    def start_long_break(self):
        self.stop_timer()
        self.set_time(15 * 60)
        self.start_timer()

    def update_timer(self):
        if self._time_left > 0:
            self._time_left -= 1
            self.update_display()
        else:
            self._timer.stop()
            # Here you can add notification logic in the future
            # For now, it just stops at 00:00

    def update_display(self):
        minutes = self._time_left // 60
        seconds = self._time_left % 60
        self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")

    def closeEvent(self, event):
        """Ensure the timer stops when the widget is closed."""
        self.stop_timer()
        super().closeEvent(event)
```
</details>

<details>
<summary>pyside6_tab_app/gui/iframes/checklist_widget.py</summary>

```python
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QListWidget, QLineEdit, QListWidgetItem, QLabel
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont

# We need to adjust the import path to find the model
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from model import TodoModel

class ChecklistWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # Each checklist has its own model instance
        self.model = TodoModel()
        
        self.main_layout = QVBoxLayout(self)
        
        self._create_input_widgets()
        self._create_list_widget()
        self._create_action_buttons()
        
        # Connect model signal to the view's slot
        self.model.tasks_changed.connect(self.render_tasks)
        
        # Initial render
        self.render_tasks()

    def _create_input_widgets(self):
        input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Adicionar nova tarefa e pressionar Enter...")
        self.task_input.returnPressed.connect(self.add_task)
        
        self.add_button = QPushButton("Adicionar")
        self.add_button.clicked.connect(self.add_task)
        
        input_layout.addWidget(self.task_input)
        input_layout.addWidget(self.add_button)
        self.main_layout.addLayout(input_layout)

    def _create_list_widget(self):
        self.task_list = QListWidget()
        self.task_list.itemChanged.connect(self.toggle_task_status)
        self.main_layout.addWidget(self.task_list)

    def _create_action_buttons(self):
        self.delete_button = QPushButton("Remover Tarefas Concluídas")
        self.delete_button.clicked.connect(self.delete_completed)
        self.main_layout.addWidget(self.delete_button)

    @Slot()
    def add_task(self):
        description = self.task_input.text().strip()
        if description:
            self.model.add_task(description)
            self.task_input.clear()

    @Slot(QListWidgetItem)
    def toggle_task_status(self, item):
        task_id = item.data(Qt.UserRole)
        is_completed = item.checkState() == Qt.Checked
        # Block signals to prevent render_tasks from re-triggering this
        self.task_list.blockSignals(True)
        self.model.update_task_status(task_id, is_completed)
        self.task_list.blockSignals(False)

    @Slot()
    def delete_completed(self):
        self.model.delete_completed_tasks()

    @Slot()
    def render_tasks(self):
        # Block signals to prevent itemChanged from firing during refresh
        self.task_list.blockSignals(True)
        self.task_list.clear()
        tasks = self.model.get_tasks()
        
        for task in tasks:
            item = QListWidgetItem(task['descricao'])
            item.setData(Qt.UserRole, task['id'])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            
            if task['concluida']:
                item.setCheckState(Qt.Checked)
                font = item.font()
                font.setStrikeOut(True)
                item.setFont(font)
                item.setForeground(Qt.gray)
            else:
                item.setCheckState(Qt.Unchecked)
            
            self.task_list.addItem(item)
            
        self.task_list.blockSignals(False)

    def closeEvent(self, event):
        """Ensure the database connection is closed when the widget is destroyed."""
        self.model.close()
        super().closeEvent(event)
```
</details>

## 5. Conclusão e Próximos Passos

Conseguimos! Agora temos uma aplicação funcional baseada no template que você queria, mas com um sistema de abas muito mais flexível e poderoso. Cada funcionalidade principal é um componente independente, o que torna o projeto muito mais fácil de manter e expandir.

**O que fazer a seguir?**

1.  **Melhorar a Interação**: Podemos fazer com que o timer Pomodoro se associe a uma tarefa selecionada no Checklist para contar os ciclos automaticamente.
2.  **Aprimorar a UI**: Podemos melhorar o design do Dashboard para exibir gráficos reais (usando Matplotlib ou Plotly) e estatísticas das tarefas.
3.  **Testes**: Agora que a estrutura está estável, podemos recriar o diretório `tests` e escrever testes para o `model.py` (desta vez, vai funcionar!) e para a lógica dos widgets.
4.  **Empacotamento**: Preparar a aplicação para distribuição usando `PyInstaller`.

Estou pronto para o próximo passo. O que você gostaria de fazer?


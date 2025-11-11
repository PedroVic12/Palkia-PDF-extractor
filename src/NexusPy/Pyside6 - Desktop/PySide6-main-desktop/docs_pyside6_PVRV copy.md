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
        
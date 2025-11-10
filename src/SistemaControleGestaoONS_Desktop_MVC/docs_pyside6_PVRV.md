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

### 3.5. Próximos Passos: Testes e Deploy

1.  **Testes Unitários**:
    - Podemos criar um diretório `tests/`.
    - **Testar o Model**: Criar `test_model.py` para testar as funções do banco de dados (adicionar, deletar, etc.) de forma isolada, sem a necessidade da interface gráfica.
    - **Testar o Controller**: Criar `test_controller.py` para simular sinais da View e verificar se o Controller chama os métodos corretos no Model.

2.  **Deploy (Empacotamento)**:
    - Para distribuir sua aplicação como um executável (`.exe` no Windows, por exemplo), podemos usar ferramentas como `PyInstaller` ou `cx_Freeze`.
    - O processo geralmente envolve:
        - Instalar a ferramenta: `pip install pyinstaller`.
        - Executar o comando: `pyinstaller --onefile --windowed pomodoro_todo_app/main.py`.
        - Isso criará um diretório `dist/` com o seu aplicativo pronto para ser compartilhado.

#### 3.5.1. Testando o Model (`tests/test_model.py`)

Acabei de criar o arquivo de teste para o nosso modelo. Testar o modelo primeiro é uma excelente prática, pois ele é o coração da lógica de dados da nossa aplicação.

**Estrutura do Arquivo de Teste:**

- **`import unittest`**: Importamos a biblioteca de testes padrão do Python.
- **`from pomodoro_todo_app.model import TodoModel`**: Importamos a classe que queremos testar. A linha `sys.path.insert(0, project_root)` é um truque para garantir que o Python encontre os módulos da nossa aplicação, já que o diretório `tests` está em um nível diferente.
- **`class TestTodoModel(unittest.TestCase)`**: Criamos uma classe de teste que herda de `unittest.TestCase`.
- **`setUp(self)`**: Este método é especial. Ele é executado **antes** de cada teste (`test_...`). Aqui, criamos um banco de dados SQLite **em memória** (`:memory:`). Isso é fantástico para testes, pois é extremamente rápido e garante que cada teste comece com um banco de dados limpo, sem interferir nos outros testes ou criar arquivos no seu disco.
- **Métodos `test_...`**: Cada método que começa com `test_` é um teste individual.
    - **`test_add_task`**: Verifica se, após chamar `add_task`, o número de tarefas no banco de dados é 1 e se a descrição está correta.
    - **`test_update_task_status`**: Adiciona uma tarefa, pega seu ID, a marca como concluída e verifica se o status foi realmente alterado para 1. Depois, desmarca e verifica se voltou para 0.
    - **`test_delete_task`**: Adiciona uma tarefa, a deleta e depois verifica se a lista de tarefas está vazia.
    - **`self.assertEqual(a, b)`**: Esta é uma "asserção". O teste passa se `a` for igual a `b`. Se não for, o teste falha e nos mostra o erro.

Agora, vamos executar esses testes para validar nosso `model.py`.

Estou à sua disposição. O que você gostaria de fazer a seguir? Podemos começar a escrever os testes, adicionar novas funcionalidades (como as notificações) ou empacotar a aplicação.


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
# Plano de Desenvolvimento: OrquestraPy (anteriormente Caixa de Ferramentas ONS)

## 1. Visão Geral e Arquitetura

**Objetivo do Projeto**: Desenvolver uma aplicação desktop (`PySide6`), o **OrquestraPy**, que funcione como um orquestrador de processos e automações para a equipe de curto prazo do ONS. O software facilitará a automação de tarefas, análise de dados e visualização de estudos de sistemas elétricos de potência (SEP).

**Arquitetura Principal**: **Model-View-Controller (MVC)**. Esta arquitetura é ideal para organizar a complexidade do projeto, separando a lógica de dados, a interface do usuário e o controle da aplicação.

-   **Model (Modelo)**: O cérebro da aplicação. Contém os parsers de arquivos, a lógica de negócio, as classes que representam os dados (ex: `Usina`, `Linha`) e os scripts de automação.
-   **View (Visão)**: A interface gráfica (GUI) construída com PySide6. Contém as janelas, abas, botões e gráficos. É responsável por exibir dados e capturar as ações do usuário.
-   **Controller (Controlador)**: O intermediário que conecta o Model e a View. Recebe ações da View, aciona a lógica no Model e atualiza a View com os resultados.

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

### **Fase 4: Polimento e Evolução**
*O objetivo é adicionar funcionalidades que melhoram a experiência do usuário e a robustez da aplicação.*

-   [ ] **Tarefa 1**: Adicionar um seletor de tema (Claro/Escuro) e fazer a aplicação trocar os estilos dinamicamente. `[50 min | Médio | 25 XP]`
-   [ ] **Tarefa 2**: Integrar uma biblioteca de gráficos (`PyQtGraph` ou `Matplotlib`) para exibir um gráfico de barras simples com os dados da Ferramenta 1. `[50 min | Difícil | 50 XP]`
-   [ ] **Tarefa 3**: Implementar uma barra de status na `MainWindow` para exibir mensagens informativas (ex: "Arquivo carregado", "Script em execução..."). `[25 min | Médio | 25 XP]`
-   [ ] **Tarefa 4**: Gerar a primeira versão executável (`.exe` ou binário) da aplicação usando `PyInstaller`. `[50 min | Médio | 25 XP]`
-   [ ] **🏆 DESAFIO 4**: Ter um executável funcional que pode ser compartilhado com um colega para teste. `[Marco | 100 XP]`
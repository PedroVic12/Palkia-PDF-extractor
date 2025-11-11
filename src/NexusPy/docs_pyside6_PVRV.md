# Documentação e Guia de Desenvolvimento PySide6

Este documento detalha a arquitetura final da aplicação que construímos e serve como um guia para seus próximos passos no desenvolvimento.

## 1. Levantamento de Requisitos da Aplicação Base

Construímos uma "casca" de aplicação (um *shell*) robusta e flexível. Estes foram os requisitos que ela cumpriu:

#### Requisitos Funcionais (RF)
- **RF01**: A aplicação deve ter uma janela principal com um menu lateral e uma área de conteúdo principal.
- **RF02**: A navegação principal para abrir diferentes módulos (ferramentas) deve estar claramente disponível.
- **RF03**: O usuário deve poder abrir múltiplos módulos em abas, podendo alternar entre eles.
- **RF04**: O usuário deve poder fechar as abas que não está mais usando.
- **RF05**: A aplicação deve fornecer acesso rápido a uma lista de links externos, que devem abrir no navegador padrão do usuário.
- **RF06**: O usuário deve poder customizar a aparência da aplicação, incluindo:
    - Mudar o tema entre claro (Light) e escuro (Dark).
    - Mudar a família da fonte da aplicação.
    - Mudar o tamanho da fonte da aplicação.
- **RF07**: As customizações de aparência devem ser salvas e persistir entre as sessões da aplicação.
- **RF08**: O menu lateral deve ser "responsivo", mostrando controles contextuais que são relevantes para a aba atualmente ativa.
- **RF09**: O usuário deve poder ocultar e re-exibir o menu lateral.

#### Requisitos Não-Funcionais (RNF)
- **RNF01**: O código-fonte deve ser organizado e modular, separando a lógica da interface.
- **RNF02**: A arquitetura deve ser extensível, facilitando a adição de novos módulos (abas/IFrames) no futuro.
- **RNF03**: A aplicação deve usar o framework PySide6 e seguir as boas práticas de desenvolvimento em Python.
- **RNF04**: A interface deve ter uma aparência moderna e profissional, baseada nos templates de referência.

## 2. Arquitetura Final: Padrão MVC e UI Dinâmica

A arquitetura final da aplicação segue de perto o padrão **Model-View-Controller (MVC)** e implementa a interface dinâmica que você solicitou.

### Mapeamento MVC

- **Model (Modelo)**: Camada de dados e lógica de negócio.
    - **`settings_model.py`**: Gerencia a lógica de carregar e salvar as configurações (tema, fonte) no arquivo `settings.json`. Ele não sabe nada sobre a interface, apenas lê/escreve dados e emite um sinal (`settings_changed`) quando os dados são salvos.
    - **`model.py`**: Gerencia os dados do Checklist (tarefas) no banco de dados `pomodoro_tasks.db`. Também é completamente independente da UI.

- **View (Visão)**: A camada de apresentação, responsável por exibir a interface.
    - **`ui_main_window.py`**: Define a estrutura esquelética da janela principal.
    - **`iframes/` (ex: `checklist_widget.py`, `settings_widget.py`)**: Cada IFrame é uma View. Eles constroem a UI de uma funcionalidade, emitem sinais baseados na interação do usuário (ex: `settings_saved`), mas não contêm a lógica principal da aplicação.
    - **`side_menus/` (ex: `checklist_sidemenu.py`)**: Os menus contextuais também são Views. Eles exibem controles e emitem sinais (ex: `filter_changed`).
    - **`styles.py`**: Pode ser considerado parte da View, pois define a aparência visual.

- **Controller (Controlador)**: A camada que conecta o Model e a View.
    - **`main.py` (Classe `MainWindow`)**: Este é o coração da aplicação, atuando como o principal Controlador.
        1.  **Ouve a View**: Ele conecta os sinais dos widgets da UI (cliques nos botões de navegação, sinal `settings_saved` do `SettingsWidget`) a seus métodos (slots).
        2.  **Atualiza o Model**: Quando o usuário salva as configurações, o `MainWindow` recebe o sinal e manda o `SettingsModel` salvar os novos dados.
        3.  **Ouve o Model**: Ele se conecta ao sinal `settings_changed` do `SettingsModel`.
        4.  **Atualiza a View**: Quando o `SettingsModel` emite o sinal de que mudou, o `MainWindow` chama seu método `apply_settings_from_model` para atualizar a fonte e o stylesheet de toda a aplicação.
        5.  **Gerencia a Lógica da UI**: Ele também contém a lógica para gerenciar a abertura/fechamento de abas e a troca dinâmica do menu lateral.

### UI Dinâmica: AppBar e Menu de Contexto

- **AppBar de Links**: O `main.py`, no método `_setup_appbar_links`, popula a barra superior com `PyTextButton`s, conectando cada um para abrir uma URL externa.
- **Menu Lateral Híbrido**: O `main.py`, através do método `on_tab_changed`, gerencia o conteúdo do menu lateral. Ele sempre garante que o menu de navegação principal (`NavigationMenu`) esteja presente e, em seguida, adiciona o menu de contexto específico da aba ativa, criando a experiência "responsiva" que você desejava.

## 3. Como Executar a Aplicação

Navegue até o diretório `src/SistemaControleGestaoONS_Desktop_MVC` e execute:
```bash
python pyside6_tab_app/main.py
```

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
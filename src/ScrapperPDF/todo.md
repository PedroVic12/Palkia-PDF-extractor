
# Sistema Controle e Gestão - PLC - ONS 2025
---

# Levantamento de requisitos do Software de Controle e Gestão MUST e Atividades SP (Dashboard)

## Refatoração e nova arquitetura
- MVC Arquitetura
- App Template com menu arvore lateral de navegação e tabs para cara Iframe em arquivos separados
- main.py compilado com .ui (futuramente) e usando pyinstaller
- Criação do Executavel com Instalador para abrir o app "pesado" depois de compilar para windwows
- Modeladem de dados e integração com Dashboard SP com análise de dados
- Deck Builder para Análise de contigencias MUST
- HTML to .PDF relatorio automatizado
- Scrapy toda segunda e sexta dados do Sharepoint
- Cada Tab é uma funcionalidade diferente (Palkia GUI, Junta Deck, Organiza Arquivos, MUST Dashboard, Controle e Gestão Fora Ponta com OBS, Deck Builder (com pyautogui simulando no AnaREDE com diagrama do SIN), Gerar Relatorio com análise de contigencia ) 
- Refatoração Análise de contigencias de Invervenção no SEP com agendamento ótimo (PandaPower + DEAP) com Lancher.py refatorado 
- [ ] Dashboard atividades SP / Dashboard Must / Relatórios (gráficos) / Palkia Extractor GUI / Deck Builder da solicitação de MUST

## Critérios de funcionamento - Outubro
- [x] ETL de arquivos PDF e Excel com pandas e PowerQuery
- [x] Controle e gestão de Banco de dados de informações de MUST de atividades SP
- [x] Aprovação com ou sem Ressalvas para criar deck de analise no anaRede e abrir com Pyautogui

- [ ] Entender a modelagem do banco de dados do SQL Server e filtrar apenas para area SP

- [ ] Atividades SP em banco Access atualizado com excel de atividades SP

- [ ] Automação em Pyautogui para abrir o SIN atualizado ja na barra ou linha de análise no AnaREDE
- [ ] Criação de relatorios docx template dá analise a partir do excel de controle

- [ ] Iniciar com deploy do app com dashbaord em HTML e Pyside6 com ferramentas e usando mvc com QT-Designer com arquivos  .ui e .py
--- 



---

## Database
- [x] Microsfit Access Configurado - python + Power Query com Scrapy em SQL SERVER ONS
- [x] Sqlite3 - python
- [x] Excel + LocalStorage em HTML 
- [ ] Supabase (Series Temporais)

## Backend
- [ ] Alterar o run.py para ajustar os intervalos de páginas e alterar apenas o Arquivo Palkia para manutenção

- [ ] Uso da planilha Excel (atividades SP) de Controle de MUST compartilhado no SharePoint para alimentar a ferramenta Desktop

## Frontend

- [ ] Refatoração do código de arquivo unico .py para um projeto MVC usando QT - Designer
- [ ] Deck Builder caso analisado com o MUST solicitado
- [ ] Template de Word (docx) para criação do relatorio final em .PDF
- [ ] Ajustar componentes react para usar no astro/nextsjs futuramente
- [ ] DEVERÁ TRAZER TODAS ESTATÍSTICAS PARA CADA UM DOS ANOS das tabelas MUST
- [ ] PONTOS APROVADOS OU RESSALVAS OU LIMITADOS DE CADA EMPRESA
- [ ] QUANTIDADE DE SOLICITAÇÕES APROVADAS POR EMPRESA OU PONTOS
- [ ] Coluna aprovado - SIM ou NAO
- [ ] Container de Tabela histórico das análises
---

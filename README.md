# Palkia-ScrapperPDF V3.1.1

- script para rodar a automação: `CLI.py`
- Lancher do ETL de arquivos MUST: `Palkia_GUI.py`
- PySide6 Controle e Gestão MUST: `desktop_Dashboard_app.py`

Use pyqt6-tools via `pip install pyqt6-tools` ou `pip install qt6-applications` and rode o comando `pyqt6-tools designer`

Convert .ui to Python Code:
Use the pyside6-uic tool to convert your .ui file into a Python class:

```sh
pyside6-uic mainwindow.ui -o ui_mainwindow.py
```

This generates a Python file (e.g., ui_mainwindow.py) containing the Python code representation of your designed UI.


## Updates e Melhorias ate 31/10/2025

- Refatoração do código de arquivo unico .py para um projeto MVC usando QT - Designer
- Deck Builder caso analisado com o MUST solicitado
- Template de Word (docx) para criação do relatorio final
- Dashboard atividades SP / Dashboard Must / Relatórios (gráficos) / Palkia Extractor GUI / Deck Builder da solicitação de MUST
- Criação de projetos PySide6 com componentes e MVC template com menu lateral de navegação e clean code para POO em Eventos para softwares Desktops.

ver arquivo @todo.md

---

--- 
## PDF Extractor

Este projeto é uma ferramenta para extrair dados de arquivos PDF usando Python. Ele utiliza diversas bibliotecas para processamento de PDFs, manipulação de dados e interação com bancos de dados.

Substitua `<URL do repositório>`, `<nome do repositório>` e `<nome_do_seu_script>.py` com as informações específicas do seu projeto. Ajuste a seção "Uso" conforme as funcionalidades do seu projeto.

## Dependências

Certifique-se de que você tem as seguintes dependências instaladas:

```toml
[tool.poetry.dependencies]
python = "^3.12"
camelot-py = "^0.11.0"
opencv-python = "^4.9.0.80"
matplotlib = "^3.8.3"
ghostscript = "^0.7"
pandas = "^2.2.2"
psycopg2-binary = "^2.9.9"
sqlalchemy = "^2.0.32"
unidecode = "^1.3.8"
```

## Variáveis de Ambiente

O projeto requer as seguintes variáveis de ambiente para configurar o acesso ao banco de dados PostgreSQL:

- `DB_NAME`: Nome do banco de dados
- `DB_USER`: Nome de usuário do banco de dados
- `DB_PASSWORD`: Senha do banco de dados
- `DB_HOST`: Host do banco de dados (ex.: `localhost` ou IP do servidor)

## Configuração do Ambiente

1. Clone o repositório:
   ```bash
   git clone <URL do repositório>
   cd <nome do repositório>
   ```

2. Instale as dependências usando Poetry:
   ```bash
   poetry install
   ```

3. Defina as variáveis de ambiente. Você pode criar um arquivo `.env` na raiz do projeto com o seguinte conteúdo:
   ```env
   DB_NAME=seu_nome_de_banco_de_dados
   DB_USER=seu_usuario
   DB_PASSWORD=sua_senha
   DB_HOST=seu_host
   ```

4. Execute o projeto:
   ```bash
   poetry run python <nome_do_seu_script>.py
   ```

## Uso

Na pasta src/files/, crie uma subpasta correspondente ao tipo de arquivo que você deseja processar. Em seguida, adicione as regras de extração de dados no arquivo src/configs/rules/notas.py. Caso precise de apoio visual para criar as regras, utilize o arquivo pdf_viz.py para obter uma referência visual da área de extração do arquivo. Após configurar as regras, faça as alterações necessárias no arquivo start.py. Com essas etapas concluídas, o sistema extrairá automaticamente todos os dados dos arquivos na pasta e os salvará no banco de dados



## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.

Este projeto é um Fork de de tecnologias de OCR e Visão Computacional para ETL de arquivos .PDF para Excel e Banco de dados. 
```


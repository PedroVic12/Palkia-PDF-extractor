from flask import Flask, render_template, send_from_directory
import os
from get_db_access_connection import get_db_connection
import pyodbc
from flask import jsonify


#gunicorn --bind 0.0.0.0:8080 app:app

class PikachuServer:
    """
    Uma classe de servidor web Flask para servir um dashboard de análise.
    Esta classe encapsula a configuração e execução do servidor.
    """

    def __init__(self):
        """
        Inicializador da classe PikachuServer.
        Chama os métodos para configurar o site e as rotas.
        """
        self.app = None
        self.setup_website()
        self.setup_routes()

    def setup_website(self):
        """
        Configura a instância principal da aplicação Flask.
        Define as pastas de templates e arquivos estáticos como o diretório atual
        para que o Flask possa encontrar 'index.html' e outros arquivos como
        'must_tables_PDF_notes_merged.json'.
        """
        # O '.' indica que a pasta raiz do projeto é o diretório atual.
        self.app = Flask(__name__, template_folder='templates', static_folder='static')

    def setup_routes(self):
        """
        Define todas as rotas da aplicação web.
        """


        @self.app.route('/')
        def index():
            """
            Rota principal que renderiza a página do dashboard.
            Retorna:
                O conteúdo renderizado de index.html.
            """
            # Renderiza o arquivo HTML principal do seu dashboard.
            return render_template('index.html')

        @self.app.route('/<path:filename>')
        def serve_static_files(filename):
            """
            Rota para servir arquivos estáticos necessários para o frontend,
            como o arquivo JSON de dados que seu script tenta carregar.
            Args:
                filename (str): O nome do arquivo a ser servido.
            Retorna:
                O arquivo solicitado do diretório raiz.
            """
            # Envia arquivos como 'must_tables_PDF_notes_merged.json' para o cliente.
            return send_from_directory(self.app.static_folder, filename)
        

        @self.app.route('/api/data')
        def get_data():
            """
            Rota de API que busca todos os dados da tabela no SQL Server
            e os retorna em formato JSON.
            """
            conn = None
            try:
                conn = get_db_connection()
                if not conn:
                    return jsonify({"error": "Falha na conexão com o banco de dados"}), 500
                
                cursor = conn.cursor()
                # O nome da tabela deve ser o mesmo definido no script de importação
                cursor.execute("SELECT * FROM MustTablesPdfNotes") 
                
                # Obtém os nomes das colunas a partir do cursor
                columns = [column[0] for column in cursor.description]
                
                # Cria uma lista de dicionários para facilitar a conversão para JSON
                rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
                return jsonify(rows)

            except pyodbc.Error as e:
                print(f"Erro ao buscar dados: {e}")
                return jsonify({"error": "Ocorreu um erro ao consultar o banco de dados"}), 500
            except Exception as e:
                print(f"Erro inesperado: {e}")
                return jsonify({"error": "Ocorreu um erro interno no servidor"}), 500
            finally:
                if conn:
                    conn.close()

    def run_server(self, host='0.0.0.0', port=8080):
        """
        Inicia o servidor de desenvolvimento do Flask.
        Args:
            host (str): O host no qual o servidor irá rodar. '0.0.0.0' o torna
                        acessível na sua rede local.
            port (int): A porta que o servidor irá escutar.
        """
        print(f" * Servidor Flask Pikachu rodando em http://{host}:{port}")
        print(f"\n* Acesse http://127.0.0.1:{port} no seu navegador para acessar o frontend")
        self.app.run(host=host, port=port, debug=True)



if __name__ == '__main__':
    # 1. Instale o Flask:
    #    pip install Flask
    #
    # 2. Coloque este arquivo (app.py) no mesmo diretório que os seus arquivos:
    #    - index.html
    #    - must_tables_PDF_notes_merged.json (IMPORTANTE: este arquivo de dados é necessário)
    #
    # 3. Execute este script no seu terminal:
    #    python app.py

    # Cria uma instância do servidor e o inicia.
    server = PikachuServer()
    server.run_server()




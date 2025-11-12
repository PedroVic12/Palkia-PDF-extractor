from flask import Flask, Response, request, send_file, render_template_string
import os
import threading
import time
import requests
from generate_pdf import RelatorioGeneratorPDF

class FlaskServer:
    def __init__(self, pdf_generator: RelatorioGeneratorPDF, host: str = '0.0.0.0', port: int = 8888, debug: bool = True):
        self.app = Flask(__name__)
        self.pdf_generator = pdf_generator
        self.host = host
        self.port = port
        self.debug = debug
        self._setup_routes()

    def _setup_routes(self):
        @self.app.route("/generate-cv", methods=["GET"])
        def generate_cv_endpoint():
            try:
                html_file_path = os.path.join(os.path.dirname(__file__), 'cv.html')
                
                if not os.path.exists(html_file_path):
                    return {"error": "cv.html não encontrado. Crie o arquivo primeiro."}, 500
                    
                with open(html_file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()

                pdf_buffer = self.pdf_generator.generate(html_content)
                pdf_byte_string = pdf_buffer.getvalue()
                pdf_buffer.close()

                response = Response(pdf_byte_string, content_type="application/pdf")
                response.headers["Content-Disposition"] = "inline; filename=cv.pdf"
                
                return response
            except RuntimeError as re:
                return { "error": f"Erro de configuração do gerador de PDF: {re}" }, 500
            except Exception as e:
                return { "error": f"Geração de PDF falhou: {e}" }, 500

    def run(self):
        server_thread = threading.Thread(target=lambda: self.app.run(host=self.host, port=self.port, debug=self.debug, use_reloader=False))
        server_thread.daemon = True
        server_thread.start()

        print(f"🚀 Servidor WeasyPrint/pdfkit rodando em http://{self.host}:{self.port}/")
        print("Aguardando o servidor iniciar para fazer a requisição GET de teste...")
        time.sleep(3)

        try:
            test_url = f"http://127.0.0.1:{self.port}/generate-cv"
            print(f"Enviando requisição GET para: {test_url}")
            response = requests.get(test_url)
            print(f"Status da requisição GET de teste: {response.status_code}")
            if response.status_code == 200:
                print("✅ Requisição GET de teste para /generate-cv bem-sucedida!")
            else:
                print(f"❌ Requisição GET de teste para /generate-cv falhou. Resposta: {response.text}")
        except requests.exceptions.ConnectionError:
            print("❌ Não foi possível conectar ao servidor Flask. Ele pode não ter iniciado corretamente.")
        except Exception as e:
            print(f"❌ Erro ao fazer a requisição GET de teste: {e}")

        #while True:
        #    time.sleep(1)

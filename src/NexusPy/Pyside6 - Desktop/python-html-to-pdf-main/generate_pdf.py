# pip install weasyprint

# pacman -S python-weasyprint

"""
On WIndows,

Install WeasyPrint in a virtual environment using pip:

python -m venv venv
venv\Scripts\activate.bat
python -m pip install weasyprint
python -m weasyprint --info

or use other lib like

pip install pdfkit

https://wkhtmltopdf.org/downloads.html

"""# -*- coding: utf-8 -*-
# Servidor Flask para conversão de HTML para PDF (v1.1 - CORRIGIDO)
# Requer: pip install weasyprint
# NOTA: O Flask rodará na porta 8888.

import os
import io
import threading
import time
import requests # Novo import

from flask import Flask, Response, request, send_file, render_template_string

# --- Configuração do gerador de PDF ---
PDF_GENERATOR = None
try:
    from weasyprint import HTML
    PDF_GENERATOR = ("weasyprint", HTML)
    print("✅ WeasyPrint carregado com sucesso.")
except (ImportError, OSError) as e:
    print(f"❌ Erro ao carregar WeasyPrint: {e}. Tentando pdfkit...")
    try:
        import pdfkit
        # --- Configurar o caminho para wkhtmltopdf no Windows ---
        # Baixe wkhtmltopdf de https://wkhtmltopdf.org/downloads.html
        # E defina o caminho para o executável (ex: C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe)
        WKHTMLTOPDF_PATH = "C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe" # <--- ATUALIZE ESTE CAMINHO NO WINDOWS!
        
        # Verifica se o executável existe antes de configurar
        if not os.path.exists(WKHTMLTOPDF_PATH):
            print(f"AVISO: wkhtmltopdf não encontrado no caminho: {WKHTMLTOPDF_PATH}. pdfkit pode falhar.")
            # Se o wkhtmltopdf não for encontrado, ainda tentamos carregar pdfkit, mas com um aviso.
            # Isso permite que o usuário o instale e configure posteriormente.
            config = None
        else:
            config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)

        PDF_GENERATOR = ("pdfkit", config)
        print("✅ pdfkit carregado com sucesso (requer wkhtmltopdf instalado e configurado).")
    except ImportError:
        print("❌ pdfkit também não encontrado. Geração de PDF desabilitada.")
# --- FIM da Configuração ---

app = Flask(__name__)

@app.route("/generate-cv", methods=["GET"])
def generate_pdf():
    """Lê o cv.html e o converte para um PDF usando o gerador disponível."""
    try:
        html_file_path = os.path.join(os.path.dirname(__file__), 'cv.html')
        
        if not os.path.exists(html_file_path):
            return {"error": "cv.html não encontrado. Crie o arquivo primeiro."}, 500
            
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        pdf_buffer = io.BytesIO()
        
        if PDF_GENERATOR[0] == "weasyprint":
            PDF_GENERATOR[1](string=html_content).write_pdf(target=pdf_buffer)
        elif PDF_GENERATOR[0] == "pdfkit":
            pdfkit_module = pdfkit
            pdfkit_config = PDF_GENERATOR[1]
            if pdfkit_config:
                pdfkit_module.from_string(html_content, pdf_buffer, configuration=pdfkit_config)
            else:
                # Se a configuração não existe (wkhtmltopdf não encontrado), tente sem ela
                # (Isso pode causar um erro se wkhtmltopdf não estiver no PATH do sistema)
                pdfkit_module.from_string(html_content, pdf_buffer)
        else:
            return {"error": "Nenhum gerador de PDF disponível (WeasyPrint ou pdfkit)."}, 500

        pdf_byte_string = pdf_buffer.getvalue()
        pdf_buffer.close()

        response = Response(pdf_byte_string, content_type="application/pdf")
        response.headers["Content-Disposition"] = "inline; filename=cv.pdf"
        
        return response
    except Exception as e:
        return { "error": f"Geração de PDF falhou: {e}" }, 500

def run_pdf_server(host='0.0.0.0', port=8888, debug=True):
    """Executa a aplicação Flask e faz um GET request na inicialização."""
    # Inicia o servidor Flask em uma thread separada
    server_thread = threading.Thread(target=lambda: app.run(host=host, port=port, debug=debug))
    server_thread.daemon = True
    server_thread.start()

    print(f"🚀 WeasyPrint/pdfkit Server (Corrigido) rodando em http://{host}:{port}/")
    print("Aguardando o servidor iniciar para fazer a requisição GET de teste...")
    time.sleep(3)  # Dê um tempo para o servidor iniciar

    try:
        test_url = f"http://127.0.0.1:{port}/generate-cv"
        print(f"Enviando requisição GET para: {test_url}")
        response = requests.get(test_url)
        print(f"Status da requisição GET de teste: {response.status_code}")
        if response.status_code == 200:
            print("✅ Requisição GET de teste para /generate-cv bem-sucedida!")
            # Você pode salvar o PDF gerado pela requisição de teste
            # with open("teste_cv.pdf", "wb") as f:
            #     f.write(response.content)
            # print("PDF de teste salvo como teste_cv.pdf")
        else:
            print(f"❌ Requisição GET de teste para /generate-cv falhou. Resposta: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao servidor Flask. Ele pode não ter iniciado corretamente.")
    except Exception as e:
        print(f"❌ Erro ao fazer a requisição GET de teste: {e}")

    # Mantém o thread principal ativo para que o servidor em segundo plano continue rodando
    # Em um ambiente de produção real, você usaria um servidor WSGI como Gunicorn ou Waitress.
    while True:
        time.sleep(1)

if __name__ == "__main__":
    run_pdf_server(debug=True)
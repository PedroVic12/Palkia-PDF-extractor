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
from flask import Flask, Response, request, send_file, render_template_string

# --- A CORREÇÃO CRÍTICA (O IMPORT) ---
# Esta linha estava faltando e causou o erro 'name HTML is not defined'.
from weasyprint import HTML
# --- FIM DA CORREÇÃO ---

app = Flask(__name__)

@app.route("/generate-cv", methods=["GET"])
def generate_pdf():
    """Lê o cv.html e o converte para um PDF."""
    try:
        html_file_path = os.path.join(os.path.dirname(__file__), 'cv.html')
        
        if not os.path.exists(html_file_path):
            return {"error": "cv.html não encontrado. Crie o arquivo primeiro."}, 500
            
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        pdf_buffer = io.BytesIO()
        
        # Esta linha AGORA FUNCIONA
        # O WeasyPrint processa o HTML e o CSS (se estiver linkado ou inline)
        HTML(string=html_content).write_pdf(target=pdf_buffer)

        pdf_byte_string = pdf_buffer.getvalue()
        pdf_buffer.close()

        response = Response(pdf_byte_string, content_type="application/pdf")
        response.headers["Content-Disposition"] = "inline; filename=cv.pdf"
        
        return response
    except Exception as e:
        # Se houver outro erro (ex: CSS inválido), ele será pego aqui.
        return { "error": f"Geração de PDF falhou (mesmo com import): {e}" }, 500

def run_pdf_server(host='0.0.0.0', port=8888, debug=True):
    """Executa a aplicação Flask."""
    print(f"🚀 WeasyPrint Server (Corrigido) rodando em http://{host}:{port}/generate-cv")
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    run_pdf_server(debug=True)
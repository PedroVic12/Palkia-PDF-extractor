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

"""

from weasyprint import HTML
import io
from flask import Flask, Response, request

app = Flask(__name__)

@app.route("/generate-cv", methods=["GET"])
def generate_pdf():
  try:
    pdf_buffer = io.BytesIO()
    
    HTML('cv.html').write_pdf(target=pdf_buffer)

    pdf_byte_string = pdf_buffer.getvalue()
    pdf_buffer.close()

    response = Response(pdf_byte_string, content_type="application/pdf")
    response.headers["Content-Disposition"] = "inline; filename=cv.pdf"
    
    return response
  except Exception as e:
    return { "error": "pdf generation failed" }, 500

if __name__ == "__main__":
  app.run(debug=True)
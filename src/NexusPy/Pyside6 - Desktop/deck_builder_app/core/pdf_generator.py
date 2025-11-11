import os
import sys
import io

class PDFReportGenerator:
    def __init__(self):
        self.generator_type = None
        self.html_class = None # For WeasyPrint
        self.pisa_module = None # For xhtml2pdf
        self._load_pdf_backend()

    def _load_pdf_backend(self):
        if sys.platform.startswith('win'):  # Priorizar xhtml2pdf no Windows
            try:
                from xhtml2pdf import pisa
                self.generator_type = "xhtml2pdf"
                self.pisa_module = pisa
                print("✅ xhtml2pdf carregado com sucesso para Windows.")
            except ImportError as e:
                print(f"❌ Erro ao carregar xhtml2pdf no Windows: {e}. Geração de PDF desabilitada.")
        else:  # Priorizar WeasyPrint em outros sistemas (Linux/macOS)
            try:
                from weasyprint import HTML, CSS
                self.generator_type = "weasyprint"
                self.html_class = HTML
                self.css_class = CSS
                print("✅ WeasyPrint carregado com sucesso para Linux/macOS.")
            except (ImportError, OSError) as e:
                print(f"❌ Erro ao carregar WeasyPrint no Linux/macOS: {e}. Geração de PDF desabilitada.")

    def generate_pdf(self, html_content: str, output_path: str) -> bool:
        if not self.generator_type:
            print("❌ Nenhum gerador de PDF disponível.")
            return False

        try:
            if self.generator_type == "weasyprint":
                css = self.css_class(string='''
                    @page {
                        size: A4;
                        margin: 2cm;
                    }
                    body {
                        font-family: 'Segoe UI', Arial, sans-serif;
                        color: #333;
                    }
                    h1 {
                        color: #005a9e;
                        text-align: center;
                        border-bottom: 2px solid #005a9e;
                        padding-bottom: 10px;
                    }
                    h2 {
                        color: #333;
                        border-bottom: 1px solid #ccc;
                        padding-bottom: 5px;
                    }
                    table {
                        width: 100%;
                        border-collapse: collapse;
                        margin-top: 20px;
                    }
                    th, td {
                        border: 1px solid #ccc;
                        padding: 8px;
                        text-align: right;
                    }
                    th {
                        background-color: #f0f0f0;
                        font-weight: bold;
                    }
                    .summary-box {
                        background-color: #f9f9f9;
                        border: 1px solid #eee;
                        padding: 15px;
                        margin-top: 20px;
                    }
                    .summary-box p {
                        margin: 5px 0;
                    }
                ''')
                self.html_class(string=html_content).write_pdf(output_path, stylesheets=[css])
            elif self.generator_type == "xhtml2pdf":
                with open(output_path, "wb") as f:
                    self.pisa_module.CreatePDF(
                        io.BytesIO(html_content.encode('utf-8')),
                        dest=f,
                        encoding='utf-8'
                    )
            return True
        except Exception as e:
            print(f"❌ Erro ao gerar PDF com {self.generator_type}: {e}")
            return False

def generate_deck_report(parsed_data, output_path):
    if not parsed_data:
        raise ValueError("No parsed data provided to generate report.")

    html_content = create_html_template(parsed_data)

    generator = PDFReportGenerator()

    return generator.generate_pdf(html_content, output_path)

def create_html_template(data):
    # --- CSS Styles (Embedded for better compatibility) ---
    css_styles = '''
        @page {
            size: A4;
            margin: 2cm;
        }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            color: #333;
        }
        h1 {
            color: #005a9e;
            text-align: center;
            border-bottom: 2px solid #005a9e;
            padding-bottom: 10px;
        }
        h2 {
            color: #333;
            border-bottom: 1px solid #ccc;
            padding-bottom: 5px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            border: 1px solid #ccc;
            padding: 8px;
            text-align: right;
        }
        th {
            background-color: #f0f0f0;
            font-weight: bold;
        }
        .summary-box {
            background-color: #f9f9f9;
            border: 1px solid #eee;
            padding: 15px;
            margin-top: 20px;
        }
        .summary-box p {
            margin: 5px 0;
        }
    '''

    # --- Summary Section ---
    summary = data.get('summary', {})
    agent = summary.get('agent', 'N/A')
    total_gen = summary.get('total_gen_p', 0.0)
    total_load_p = summary.get('total_load_p', 0.0)
    total_load_q = summary.get('total_load_q', 0.0)

    summary_html = f"""
    <div class="summary-box">
        <h2>Resumo do Deck</h2>
        <p><strong>Agente:</strong> {agent}</p>
        <p><strong>Geração Ativa Total:</strong> {total_gen:.2f} MW</p>
        <p><strong>Carga Ativa Total:</strong> {total_load_p:.2f} MW</p>
        <p><strong>Carga Reativa Total:</strong> {total_load_q:.2f} MVAr</p>
    </div>
    """

    # --- Bars Table Section ---
    bars = data.get('bars', [])
    rows_html = ""
    for bar in bars:
        rows_html += f"""
        <tr>
            <td>{bar['num']}</td>
            <td>{bar['pg']:.2f}</td>
            <td>{bar['qg']:.2f}</td>
            <td>{bar['pl']:.2f}</td>
            <td>{bar['ql']:.2f}</td>
        </tr>
        """

    table_html = f"""
    <h2>Detalhes das Barras</h2>
    <table>
        <thead>
            <tr>
                <th>Barra</th>
                <th>Pg (MW)</th>
                <th>Qg (MVAr)</th>
                <th>Pl (MW)</th>
                <th>Ql (MVAr)</th>
                
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    """

    # --- Full HTML Document ---
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Relatório de Deck AnaREDE</title>
        <style>{css_styles}</style> <!-- Embedded CSS -->
    </head>
    <body>
        <h1>Relatório de Deck</h1>
        {summary_html}
        {table_html}
    </body>
    </html>
    """
    
    return full_html

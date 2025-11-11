import os
from weasyprint import HTML, CSS

def generate_deck_report(parsed_data, output_path):
    """
    Generates a PDF report from parsed deck data.

    Args:
        parsed_data (dict): The dictionary containing 'bars' and 'summary' data.
        output_path (str): The path to save the generated PDF file.
    """
    if not parsed_data:
        raise ValueError("No parsed data provided to generate report.")

    html_content = create_html_template(parsed_data)
    
    try:
        css = CSS(string='''
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
        
        HTML(string=html_content).write_pdf(output_path, stylesheets=[css])
        return True
    except Exception as e:
        print(f"Error generating PDF with WeasyPrint: {e}")
        # This can happen if WeasyPrint dependencies (like Pango, cairo) are not installed correctly.
        return False

def create_html_template(data):
    """Creates an HTML string from the parsed data."""
    
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
    </head>
    <body>
        <h1>Relatório de Deck</h1>
        {summary_html}
        {table_html}
    </body>
    </html>
    """
    
    return full_html

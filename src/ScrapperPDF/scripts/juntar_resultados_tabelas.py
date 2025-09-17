import pandas as pd
import os
import re

def extrair_empresa(nome_arquivo: str) -> str:
    """
    Extrai o nome da empresa a partir do nome do arquivo.
    """
    # Remove extensão
    base = os.path.splitext(nome_arquivo)[0]

    # Pega o último pedaço após "_" ou "-"
    partes = re.split(r'[_-]', base)
    candidato = partes[-1].strip()

    # Tratar casos especiais com nomes longos
    if "SUL SUDESTE" in base.upper():
        return "SUL SUDESTE"
    if "PAULISTA" in base.upper():
        return "CPFL PAULISTA"
    if "PIRATININGA" in base.upper():
        return "CPFL PIRATININGA"
    if "ELEKTRO" in base.upper():
        return "NEOENERGIA ELEKTRO"
    if "ELETROPAULO" in base.upper():
        return "ELETROPAULO"
    if "JAGUARI" in base.upper():
        return "CPFL JAGUARI"

    return candidato  # fallback: usa o pedaço fatiado


def ler_todos_excel_na_pasta(pasta: str) -> pd.DataFrame:
    """
    Lê todos os arquivos Excel em uma pasta e concatena os dados em um único DataFrame,
    adicionando a empresa a partir do nome do arquivo.
    """
    arquivos = [f for f in os.listdir(pasta) if f.endswith('.xlsx')]
    dataframes = []

    for arquivo in arquivos:
        caminho_arquivo = os.path.join(pasta, arquivo)
        df = pd.read_excel(caminho_arquivo)

        empresa = extrair_empresa(arquivo)
        df["EMPRESA"] = empresa

        dataframes.append(df)

    return pd.concat(dataframes, ignore_index=True) if dataframes else pd.DataFrame()


def run():
    pasta = r"C:\Users\pedrovictor.veras\OneDrive - Operador Nacional do Sistema Eletrico\Documentos\ESTAGIO_ONS_PVRV_2025\AUTOMACÕES ONS\arquivos\anotacoes_extraidas"
    
    if not os.path.exists(pasta):
        print(f"A pasta '{pasta}' não existe.")
        return

    df_concatenado = ler_todos_excel_na_pasta(pasta)

    if df_concatenado.empty:
        print("Nenhum dado encontrado nos arquivos Excel.")
    else:
        print("Dados concatenados com sucesso!")
        print(df_concatenado.head())
        df_concatenado.to_excel(os.path.join(pasta, "todas_anotacoes_concatenadas.xlsx"), index=False)

run()

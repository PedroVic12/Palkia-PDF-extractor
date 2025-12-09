import pandas as pd 
import matplotlib.pyplot as plt

df_perdas_duplas = pd.read_excel(r"C:\Users\pedrovictor.veras\OneDrive - Operador Nacional do Sistema Eletrico\Documentos\ESTAGIO_ONS_PVRV_2025\GitHub\Palkia-PDF-extractor\src\BulbassaurQT6-ETL\Perdas-Duplas-ETL-Desktop-V4\app\assets\planilhas_PLC\PerdasDuplas - Copia.xlsm")

print(df_perdas_duplas.head())

# Agrupar por categoria (X) e contar/somar valores (Y)
distribuicao = df_perdas_duplas.groupby('Área Geoelétrica')['Volume'].sum()

plt.figure(figsize=(10, 6))
plt.pie(distribuicao.values, labels=distribuicao.index, autopct='%1.1f%%')

plt.title('Distribuição de Perdas Duplas de Linhas de Transmissão x Área Geoelétrica por cada volume')
plt.savefig("grafico_perdas_duplas.png")
plt.show()
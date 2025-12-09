import pandas as pd 
import matplotlib.pyplot as plt


df_perdas_duplas = pd.read_excel(r"C:\Users\pedrovictor.veras\OneDrive - Operador Nacional do Sistema Eletrico\Documentos\ESTAGIO_ONS_PVRV_2025\GitHub\Palkia-PDF-extractor\src\BulbassaurQT6-ETL\Perdas-Duplas-ETL-Desktop-V4\modules\Relatorio_ONS_Automate\assets\Contingências Duplas (relatorio-automate).xlsm")

plt.pie(df_perdas_duplas['Perda'], labels=df_perdas_duplas['Linha'], autopct='%1.1f%%')
plt.title('Distribuição de Perdas em Linhas de Transmissão - Perdas Duplas')
plt.savefig("grafico_perdas_duplas.png")
plt.show()
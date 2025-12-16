import pandas as pd 
import matplotlib.pyplot as plt
import plotly.io as pio

# Para exibir gráficos no Jupyter Notebook ou VS Code
pio.renderers.default = 'browser'  # Abre no navegador


from AnaliseContigenciasPyPlot import AnalisadorContingencias

df_perdas_duplas = pd.read_excel(r"C:\Users\pedrovictor.veras\OneDrive - Operador Nacional do Sistema Eletrico\Documentos\ESTAGIO_ONS_PVRV_2025\GitHub\Palkia-PDF-extractor\src\BulbassaurQT6-ETL\Perdas-Duplas-ETL-Desktop-V4\app\assets\planilhas_PLC\perdas_duplas_ETL.xlsx")

print(df_perdas_duplas.head())


def agrupar_e_somar(df, categoria, valor):
    return df.groupby(categoria)[valor].sum().reset_index()

def AgruparVolumePorAreaGeoeletrica(df):
    # Agrupar por categoria (X) e contar/somar valores (Y)
    distribuicao = df.groupby('Área Geoelétrica')['Volume'].sum()
    plt.figure(figsize=(10, 6))
    plt.pie(distribuicao.values, labels=distribuicao.index, autopct='%1.1f%%')

    plt.title('Distribuição de Perdas Duplas de Linhas de Transmissão x Área Geoelétrica por cada volume')
    plt.savefig("grafico_perdas_duplas.png")
    plt.show()


# Criar instância do analisador
print("🔧 Criando analisador de contingências...")
analisador = AnalisadorContingencias(df_perdas_duplas)

# 1. ANÁLISE DE INSIGHTS
print("\n📊 OBTENDO INSIGHTS...")
insights = analisador.analise_volume_regiao()

print(f"Total de Volumes únicos: {insights['total_volumes']}")
print(f"Total de Regiões geoelétricas: {insights['total_regioes']}")
print("\nDistribuição por Volume:")
for volume, count in insights['distribuicao_volume'].items():
    print(f"  {volume}: {count} contingências")

print("\nDistribuição por Região:")
for regiao, count in insights['distribuicao_regiao'].items():
    print(f"  {regiao}: {count} contingências")

# 2. GRÁFICOS INDIVIDUAIS
print("\n🎨 GERANDO GRÁFICOS...")

# Gráfico 1: Barras - Contingências por Volume
fig1 = analisador.gerar_grafico(
    tipo='barras',
    x_col='Volume',
    titulo='Número de Contingências por Volume'
)
fig1.show()

# Gráfico 2: Pizza - Distribuição por Área Geoelétrica
fig2 = analisador.gerar_grafico(
    tipo='pizza',
    x_col='Área Geoelétrica',
    titulo='Distribuição por Região Geoelétrica'
)
fig2.show()

# Gráfico 3: Distribuição de Tensão por Região
fig3 = analisador.plot_distribuicao_tensao_regiao(tipo_grafico='barras')
fig3.show()

# Gráfico 4: Horizonte por Volume
fig4 = analisador.plot_horizonte_por_volume(tipo_grafico='barras')
fig4.show()

# 3. DASHBOARD COMPLETO
print("\n📈 CRIANDO DASHBOARD COMPLETO...")
fig_dashboard = analisador.dashboard_completo()
fig_dashboard.show()

# 4. EXPORTAR RELATÓRIO HTML
print("\n💾 EXPORTANDO RELATÓRIO...")
analisador.exportar_relatorio('relatorio_contingencias.html')

# 5. EXEMPLOS DE USO DOS MÉTODOS DA CLASSE
print("\n🔄 EXEMPLOS DE USO DA CLASSE:")


df_perdas_duplas["Tensão_kV"] = df_perdas_duplas["Contingência Dupla"].str.extract(r'(\d+\.?\d*)kV').astype(float)


# Exemplo 1: Gráfico de dispersão (se houvesse dados numéricos)
# fig_disp = analisador.gerar_grafico(
#     tipo='dispersão',
#     x_col='Volume',
#     y_col='Tensão_kV',
#     color_col='Horizonte',
#     titulo='Tensão vs Volume por Horizonte'
# )

# Exemplo 2: Heatmap
fig_heatmap = analisador.gerar_grafico(
    tipo='heatmap',
    x_col='Volume',
    y_col='Área Geoelétrica',
    titulo='Heatmap: Volume vs Área Geoelétrica'
)
fig_heatmap.show()

# Exemplo 3: Box plot
# fig_box = analisador.gerar_grafico(
#     tipo='box',
#     x_col='Volume',
#     y_col='Tensão_kV',
#     titulo='Distribuição de Tensão por Volume'
# )

# Exemplo 4: Histograma
fig_hist = analisador.gerar_grafico(
    tipo='histograma',
    x_col='Tensão_kV',
    color_col='Volume',
    titulo='Distribuição de Tensões por Volume'
)
fig_hist.show()

print("\n✅ Análise concluída!")
print("Arquivos gerados:")
print("  - Gráficos interativos no navegador")
print("  - relatorio_contingencias.html (relatório completo)")
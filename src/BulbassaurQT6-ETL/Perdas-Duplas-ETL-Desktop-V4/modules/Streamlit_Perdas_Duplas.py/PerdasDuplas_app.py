# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from AnaliseContigenciasPyPlot import AnalisadorContingenciasPlotly

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Perdas Duplas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 20px;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .chart-container {
        border-radius: 10px;
        padding: 15px;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    .warning-box {
        border-left: 5px solid #ff9800;
        background-color: #fff3e0;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Título
st.title("📊 Dashboard de Análise de Perdas Duplas")
st.markdown("**Sistema de análise de contingências em linhas de transmissão**")

# Função para carregar dados
@st.cache_data
def carregar_dados(file_path):
    """Carrega dados do arquivo Excel."""
    try:
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

# Inicializar session state
if 'analisador' not in st.session_state:
    st.session_state.analisador = None
if 'filtros_aplicados' not in st.session_state:
    st.session_state.filtros_aplicados = False

# Sidebar
with st.sidebar:
    st.header("📁 Carregar Dados")
    
    uploaded_file = st.file_uploader("Escolha um arquivo Excel", type=['xlsx', 'xls'])
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            st.session_state.analisador = AnalisadorContingenciasPlotly(df)
            st.session_state.filtros_aplicados = False
            st.success(f"✅ Dados carregados: {len(df)} registros")
        except Exception as e:
            st.error(f"❌ Erro ao carregar arquivo: {e}")
    
    st.markdown("---")
    
    # Filtros
    if st.session_state.analisador is not None:
        st.header("🔧 Filtros")
        
        try:
            opcoes_filtro = st.session_state.analisador.get_opcoes_filtro()
            
            # Filtro de Volume
            volumes_selecionados = st.multiselect(
                "Selecione Volumes:",
                options=opcoes_filtro.get('volumes', []),
                default=opcoes_filtro.get('volumes', [])
            )
            
            # Filtro de Área
            areas_selecionadas = st.multiselect(
                "Selecione Áreas:",
                options=opcoes_filtro.get('areas', []),
                default=opcoes_filtro.get('areas', [])
            )
            
            # Filtro de Horizonte
            horizontes_selecionados = st.multiselect(
                "Selecione Horizontes:",
                options=opcoes_filtro.get('horizontes', []),
                default=opcoes_filtro.get('horizontes', [])
            )
            
            # Filtro de Tensão
            col1, col2 = st.columns(2)
            with col1:
                tensao_min = st.number_input(
                    "Tensão Mínima (kV):",
                    min_value=0.0,
                    value=opcoes_filtro.get('tensoes', {}).get('min', 0.0)
                )
            with col2:
                tensao_max = st.number_input(
                    "Tensão Máxima (kV):",
                    min_value=0.0,
                    value=opcoes_filtro.get('tensoes', {}).get('max', 1000.0)
                )
            
            # Botões
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("✅ Aplicar Filtros", type="primary", use_container_width=True):
                    try:
                        df_filtrado = st.session_state.analisador.df.copy()
                        
                        # Aplicar filtros
                        if volumes_selecionados:
                            df_filtrado = df_filtrado[df_filtrado['Volume'].isin(volumes_selecionados)]
                        if areas_selecionadas:
                            df_filtrado = df_filtrado[df_filtrado['Área Geoelétrica'].isin(areas_selecionadas)]
                        if horizontes_selecionados:
                            df_filtrado = df_filtrado[df_filtrado['Horizonte'].isin(horizontes_selecionados)]
                        
                        # Filtrar por tensão
                        df_filtrado['Tensão_kV'] = pd.to_numeric(df_filtrado['Tensão_kV'], errors='coerce')
                        df_filtrado = df_filtrado[
                            (df_filtrado['Tensão_kV'] >= tensao_min) & 
                            (df_filtrado['Tensão_kV'] <= tensao_max)
                        ]
                        
                        st.session_state.analisador = AnalisadorContingenciasPlotly(df_filtrado)
                        st.session_state.filtros_aplicados = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao aplicar filtros: {e}")
            
            with col_btn2:
                if st.button("🔄 Resetar", use_container_width=True):
                    if uploaded_file is not None:
                        df = pd.read_excel(uploaded_file)
                        st.session_state.analisador = AnalisadorContingenciasPlotly(df)
                        st.session_state.filtros_aplicados = False
                        st.rerun()
                        
        except Exception as e:
            st.warning(f"⚠️ Erro ao carregar filtros: {e}")

# Conteúdo principal
if st.session_state.analisador is None:
    # Tela inicial
    st.info("👈 **Carregue um arquivo Excel na barra lateral para começar**")
    
    # Exemplo de estrutura
    with st.expander("📋 Exemplo de estrutura esperada"):
        dados_exemplo = [
            ["Volume 1", "Elos de Corrente Contínua", "LT CC 600 kV Foz do Iguaçu – Ibiúna C1 e C2", "Curto Prazo"],
            ["Volume 1", "Elos de Corrente Contínua", "LT CC 600 kV Foz do Iguaçu – Ibiúna C3 e C4", "Curto Prazo"],
            ["Volume 2", "Interligação Sul", "LT 765 kV Foz do Iguaçu – Ivaiporã C1 e C2", "Curto Prazo"],
            ["Volume 2", "Interligação Sul", "LT 765 kV Ivaiporã – Itaberá C1 e C2", "Curto Prazo"]
        ]
        df_exemplo = pd.DataFrame(dados_exemplo, 
                                 columns=['Volume', 'Área Geoelétrica', 'Contingência Dupla', 'Horizonte'])
        st.dataframe(df_exemplo, use_container_width=True)

else:
    # Dashboard com dados carregados
    analisador = st.session_state.analisador
    
    # Seção 1: Métricas
    st.header("📈 Métricas Principais")
    
    try:
        metricas = analisador.get_metricas_principais()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            with st.container():
                st.metric(
                    label="Total de Registros",
                    value=metricas.get('total_registros', 0),
                    help="Número total de contingências"
                )
        
        with col2:
            with st.container():
                st.metric(
                    label="Volumes",
                    value=metricas.get('total_volumes', 0),
                    help="Número de volumes distintos"
                )
        
        with col3:
            with st.container():
                st.metric(
                    label="Áreas Geoelétricas",
                    value=metricas.get('total_areas', 0),
                    help="Número de áreas distintas"
                )
        
        with col4:
            with st.container():
                st.metric(
                    label="Tensão Média",
                    value=f"{metricas.get('tensao_media', 0):.1f} kV",
                    help="Tensão média das linhas"
                )
                
    except Exception as e:
        st.warning(f"⚠️ Erro ao carregar métricas: {e}")
    
    st.markdown("---")
    
    # Seção 2: Gráficos Principais em Containers
    st.header("📊 Visualizações Principais")
    
    # Container 1: Gráfico de Barras
    with st.container():
        st.subheader("📊 Contingências por Volume")
        try:
            fig_barras = analisador.plot_barras(
                x_col='Volume',
                color_col='Volume',
                titulo='Contingências por Volume e Horizonte',
                barmode='group'
            )
            st.plotly_chart(fig_barras, use_container_width=True)
        except Exception as e:
            st.warning(f"⚠️ Não foi possível gerar o gráfico de barras: {e}")
            # Tentar criar um gráfico simples como fallback
            try:
                fig_fallback = go.Figure()
                fig_fallback.add_annotation(text="Gráfico não disponível", x=0.5, y=0.5, showarrow=False)
                st.plotly_chart(fig_fallback, use_container_width=True)
            except:
                pass
    
    # Container 2: Gráfico de Pizza
    with st.container():
        st.subheader("🥧 Distribuição por Área")
        try:
            fig_pizza = analisador.plot_pizza(
                names_col='Área Geoelétrica',
                titulo='Distribuição por Área Geoelétrica'
            )
            st.plotly_chart(fig_pizza, use_container_width=True)
        except Exception as e:
            st.warning(f"⚠️ Não foi possível gerar o gráfico de pizza: {e}")
    
    # Layout de 2 colunas para os próximos gráficos
    col_left, col_right = st.columns(2)
    
    # Container 3: Tensão por Região (Coluna Esquerda)
    with col_left:
        with st.container():
            st.subheader("⚡ Tensão por Região")
            try:
                fig_tensao = analisador.plot_tensao_por_regiao(
                    tipo='barras',
                    titulo='Distribuição de Tensão por Região'
                )
                st.plotly_chart(fig_tensao, use_container_width=True)
            except Exception as e:
                st.warning(f"⚠️ Não foi possível gerar o gráfico de tensão: {e}")
    
    # Container 4: Horizonte por Volume (Coluna Direita)
    with col_right:
        with st.container():
            st.subheader("⏰ Horizonte por Volume")
            try:
                fig_horizonte = analisador.plot_horizonte_por_volume(
                    tipo='barras',
                    titulo='Horizonte por Volume'
                )
                st.plotly_chart(fig_horizonte, use_container_width=True)
            except Exception as e:
                st.warning(f"⚠️ Não foi possível gerar o gráfico de horizonte: {e}")
    
    st.markdown("---")
    
    # Seção 3: Análises Avançadas
    st.header("🔍 Análises Avançadas")
    
    # Tabs para diferentes análises
    tab1, tab2, tab3 = st.tabs(["📈 Heatmap", "📊 Histograma", "🎨 Personalizado"])
    
    with tab1:
        with st.container():
            st.subheader("Heatmap: Volume vs Área")
            try:
                fig_heatmap = analisador.plot_heatmap(
                    x_col='Área Geoelétrica',
                    y_col='Volume',
                    titulo='Heatmap: Volume vs Área Geoelétrica'
                )
                st.plotly_chart(fig_heatmap, use_container_width=True)
            except Exception as e:
                st.warning(f"⚠️ Não foi possível gerar o heatmap: {e}")
    
    with tab2:
        with st.container():
            st.subheader("Distribuição de Tensões")
            try:
                fig_hist = analisador.plot_histograma(
                    x_col='Tensão_kV',
                    nbins=10,
                    color_col='Volume',
                    titulo='Distribuição de Tensões'
                )
                st.plotly_chart(fig_hist, use_container_width=True)
            except Exception as e:
                st.warning(f"⚠️ Não foi possível gerar o histograma: {e}")
    
    with tab3:
        with st.container():
            st.subheader("Crie seu próprio gráfico")
            
            # Opções para gráfico personalizado
            col_opt1, col_opt2, col_opt3 = st.columns(3)
            
            with col_opt1:
                try:
                    tipo_personalizado = st.selectbox(
                        "Tipo de gráfico:",
                        options=['barras', 'pizza', 'histograma', 'box', 'scatter', 'heatmap']
                    )
                except:
                    tipo_personalizado = 'barras'
            
            with col_opt2:
                try:
                    colunas_disponiveis = analisador.df.columns.tolist()
                    x_col_personalizado = st.selectbox(
                        "Eixo X:",
                        options=colunas_disponiveis
                    )
                except:
                    x_col_personalizado = 'Volume'
            
            with col_opt3:
                y_col_personalizado = None
                try:
                    if tipo_personalizado in ['barras', 'box', 'scatter']:
                        colunas_numericas = analisador.df.select_dtypes(include=['number']).columns.tolist()
                        y_col_personalizado = st.selectbox(
                            "Eixo Y:",
                            options=[''] + colunas_numericas
                        )
                        if y_col_personalizado == '':
                            y_col_personalizado = None
                except:
                    pass
            
            color_col_personalizado = st.selectbox(
                "Colorir por (opcional):",
                options=[''] + (analisador.df.columns.tolist() if hasattr(analisador.df, 'columns') else [])
            )
            if color_col_personalizado == '':
                color_col_personalizado = None
            
            titulo_personalizado = st.text_input("Título do gráfico:", value="")
            
            # Gerar gráfico
            if st.button("Gerar Gráfico Personalizado", type="secondary"):
                try:
                    fig_personalizado = None
                    
                    if tipo_personalizado == 'barras':
                        fig_personalizado = analisador.plot_barras(
                            x_col=x_col_personalizado,
                            y_col=y_col_personalizado,
                            color_col=color_col_personalizado,
                            titulo=titulo_personalizado or f"{x_col_personalizado} por {y_col_personalizado}"
                        )
                    
                    elif tipo_personalizado == 'pizza':
                        fig_personalizado = analisador.plot_pizza(
                            names_col=x_col_personalizado,
                            titulo=titulo_personalizado or f"Distribuição por {x_col_personalizado}"
                        )
                    
                    elif tipo_personalizado == 'histograma':
                        fig_personalizado = analisador.plot_histograma(
                            x_col=x_col_personalizado,
                            color_col=color_col_personalizado,
                            titulo=titulo_personalizado or f"Histograma de {x_col_personalizado}"
                        )
                    
                    elif tipo_personalizado == 'box':
                        if y_col_personalizado is None:
                            st.warning("⚠️ Para gráfico Box, selecione uma coluna numérica para o eixo Y")
                        else:
                            fig_personalizado = analisador.plot_box(
                                x_col=x_col_personalizado,
                                y_col=y_col_personalizado,
                                color_col=color_col_personalizado,
                                titulo=titulo_personalizado or f"Box Plot: {y_col_personalizado} por {x_col_personalizado}"
                            )
                    
                    elif tipo_personalizado == 'scatter':
                        if y_col_personalizado is None:
                            st.warning("⚠️ Para gráfico de Dispersão, selecione uma coluna numérica para o eixo Y")
                        else:
                            fig_personalizado = analisador.plot_scatter(
                                x_col=x_col_personalizado,
                                y_col=y_col_personalizado,
                                color_col=color_col_personalizado,
                                titulo=titulo_personalizado or f"Dispersão: {y_col_personalizado} vs {x_col_personalizado}"
                            )
                    
                    elif tipo_personalizado == 'heatmap':
                        st.warning("⚠️ Para heatmap, selecione duas colunas categóricas")
                    
                    # Exibir gráfico
                    if fig_personalizado is not None:
                        st.plotly_chart(fig_personalizado, use_container_width=True)
                        
                except Exception as e:
                    st.warning(f"⚠️ Erro ao gerar gráfico personalizado: {e}")
    
    st.markdown("---")
    
    # Seção 4: Insights e Dados
    st.header("💡 Insights e Dados")
    
    insights_tab1, insights_tab2 = st.tabs(["📋 Insights", "📄 Dados Brutos"])
    
    with insights_tab1:
        with st.container():
            try:
                insights = analisador.get_insights()
                
                col_ins1, col_ins2 = st.columns(2)
                
                with col_ins1:
                    st.markdown("#### 📊 Distribuição")
                    st.markdown(f"- **Volume mais comum:** {insights['insights'].get('volume_mais_comum', 'N/A')}")
                    st.markdown(f"- **Área mais comum:** {insights['insights'].get('area_mais_comum', 'N/A')}")
                    st.markdown(f"- **Horizonte mais comum:** {insights['insights'].get('horizonte_mais_comum', 'N/A')}")
                
                with col_ins2:
                    st.markdown("#### ⚡ Características")
                    st.markdown(f"- **Tensão dominante:** {insights['insights'].get('tensao_dominante', 'N/A')}")
                    st.markdown(f"- **Proporção CC/CA:** {insights['insights'].get('proporcao_cc_ca', 'N/A')}")
                    st.markdown(f"- **Tensão máxima:** {metricas.get('tensao_maxima', 0):.1f} kV")
                    st.markdown(f"- **Tensão mínima:** {metricas.get('tensao_minima', 0):.1f} kV")
                
                # Recomendações
                st.markdown("#### 🎯 Recomendações")
                st.markdown("""
                1. **Foco em manutenção:** Priorize áreas com maior número de contingências
                2. **Planejamento:** Considere reforços em linhas de alta tensão (> 700 kV)
                3. **Monitoramento:** Acompanhe contingências de curto prazo para ações preventivas
                4. **Análise:** Investigue causas comuns em volumes com múltiplas ocorrências
                """)
            except Exception as e:
                st.warning(f"⚠️ Erro ao gerar insights: {e}")
    
    with insights_tab2:
        with st.container():
            try:
                st.dataframe(analisador.df, use_container_width=True)
                
                # Opções de download
                csv = analisador.df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Baixar como CSV",
                    data=csv,
                    file_name="dados_contingencias.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.warning(f"⚠️ Erro ao exibir dados: {e}")

# Rodapé
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; padding: 20px;'>
        <p>Desenvolvido para análise de perdas duplas • ONS 2025</p>
    </div>
    """,
    unsafe_allow_html=True
)
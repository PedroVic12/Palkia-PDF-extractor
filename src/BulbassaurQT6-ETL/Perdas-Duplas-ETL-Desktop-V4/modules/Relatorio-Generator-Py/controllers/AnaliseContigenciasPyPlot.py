# analisador_contingencias.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
from typing import Optional, Dict, List
import numpy as np


class AnalisadorContingenciasPlotly:
    """
    Classe especializada para geração de gráficos Plotly Express.
    Foco em gráficos offline para uso no Streamlit.
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Inicializa o analisador com um DataFrame.
        
        Args:
            df: DataFrame com colunas ['Volume', 'Área Geoelétrica', 
                                      'Contingência Dupla', 'Horizonte']
        """
        self.df = df.copy()
        self._preprocessar_dados()
        
    def _preprocessar_dados(self) -> None:
        """Preprocessa os dados extraindo informações adicionais."""
        # Garantir que colunas críticas sejam strings
        self.df['Volume'] = self.df['Volume'].astype(str).fillna('Desconhecido')
        self.df['Área Geoelétrica'] = self.df['Área Geoelétrica'].astype(str).fillna('Desconhecido')
        self.df['Horizonte'] = self.df['Horizonte'].astype(str).fillna('Desconhecido')
        self.df['Contingência Dupla'] = self.df['Contingência Dupla'].astype(str).fillna('Desconhecido')
        
        # Extrair tensão (kV) da coluna de contingência
        self.df['Tensão_kV'] = self.df['Contingência Dupla'].apply(self._extrair_tensao)
        
        # Extrair tipo de contingência
        self.df['Tipo_Contingência'] = self.df['Contingência Dupla'].apply(
            lambda x: 'CC' if 'CC' in x else ('CA' if 'CA' in x else 'Desconhecido')
        )
        
        # Contar ocorrências
        self.df['Contagem'] = 1
    
    @staticmethod
    def _extrair_tensao(texto: str) -> Optional[float]:
        """Extrai o valor da tensão em kV do texto."""
        if not isinstance(texto, str):
            return None
            
        padrao = r'(\d+\.?\d*)\s*kV'
        match = re.search(padrao, texto, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        return None
    
    def get_metricas_principais(self) -> Dict:
        """Retorna métricas principais dos dados."""
        try:
            # Converter tensão para float, ignorando valores não numéricos
            tensao_series = pd.to_numeric(self.df['Tensão_kV'], errors='coerce')
            
            return {
                'total_registros': len(self.df),
                'total_volumes': self.df['Volume'].nunique(),
                'total_areas': self.df['Área Geoelétrica'].nunique(),
                'tensao_media': float(tensao_series.mean()) if not tensao_series.isnull().all() else 0,
                'tensao_maxima': float(tensao_series.max()) if not tensao_series.isnull().all() else 0,
                'tensao_minima': float(tensao_series.min()) if not tensao_series.isnull().all() else 0,
                'distribuicao_volume': self.df['Volume'].value_counts().to_dict(),
                'distribuicao_area': self.df['Área Geoelétrica'].value_counts().to_dict(),
                'distribuicao_horizonte': self.df['Horizonte'].value_counts().to_dict()
            }
        except Exception as e:
            print(f"Erro ao calcular métricas: {e}")
            return {}
    
    def get_opcoes_filtro(self) -> Dict:
        """Retorna opções disponíveis para filtros com tipos consistentes."""
        try:
            # Garantir que todos os valores sejam strings para ordenação
            volumes = sorted(self.df['Volume'].astype(str).unique().tolist())
            areas = sorted(self.df['Área Geoelétrica'].astype(str).unique().tolist())
            horizontes = sorted(self.df['Horizonte'].astype(str).unique().tolist())
            
            # Filtrar tensões válidas
            tensoes_validas = pd.to_numeric(self.df['Tensão_kV'], errors='coerce').dropna()
            
            return {
                'volumes': volumes,
                'areas': areas,
                'horizontes': horizontes,
                'tensoes': {
                    'min': float(tensoes_validas.min()) if len(tensoes_validas) > 0 else 0.0,
                    'max': float(tensoes_validas.max()) if len(tensoes_validas) > 0 else 1000.0
                }
            }
        except Exception as e:
            print(f"Erro ao obter opções de filtro: {e}")
            return {}
    
    def plot_barras(self, x_col: str, y_col: Optional[str] = None, 
                   color_col: Optional[str] = None, 
                   titulo: str = "", barmode: str = 'relative') -> go.Figure:
        """
        Gera gráfico de barras com tratamento de erro.
        """
        try:
            if y_col is None:
                # Contar ocorrências
                df_agg = self.df.groupby(x_col).size().reset_index(name='Contagem')
                fig = px.bar(df_agg, x=x_col, y='Contagem', 
                            color=color_col if color_col else None,
                            title=titulo or f'Distribuição por {x_col}',
                            barmode=barmode)
            else:
                # Usar valores específicos
                fig = px.bar(self.df, x=x_col, y=y_col,
                            color=color_col if color_col else None,
                            title=titulo,
                            barmode=barmode)
            
            fig.update_layout(
                xaxis_title=x_col,
                yaxis_title=y_col if y_col else 'Contagem',
                showlegend=color_col is not None
            )
            return fig
        except Exception as e:
            print(f"Erro ao gerar gráfico de barras: {e}")
            return self._criar_figura_erro(f"Erro ao gerar gráfico de barras: {str(e)[:50]}")
    
    def plot_pizza(self, values_col: Optional[str] = None, 
                  names_col: Optional[str] = None,
                  titulo: str = "") -> go.Figure:
        """
        Gera gráfico de pizza (torta) com tratamento de erro.
        """
        try:
            if values_col is None:
                if names_col is None:
                    raise ValueError("names_col é obrigatório quando values_col é None")
                
                df_agg = self.df[names_col].value_counts().reset_index()
                df_agg.columns = [names_col, 'Contagem']
                fig = px.pie(df_agg, values='Contagem', names=names_col,
                            title=titulo or f'Distribuição por {names_col}')
            else:
                fig = px.pie(self.df, values=values_col, names=names_col,
                            title=titulo)
            
            fig.update_traces(textposition='inside', textinfo='percent+label')
            return fig
        except Exception as e:
            print(f"Erro ao gerar gráfico de pizza: {e}")
            return self._criar_figura_erro(f"Erro ao gerar gráfico de pizza: {str(e)[:50]}")
    
    def plot_histograma(self, x_col: str, nbins: int = 20, 
                       color_col: Optional[str] = None,
                       titulo: str = "") -> go.Figure:
        """
        Gera histograma com tratamento de erro.
        """
        try:
            fig = px.histogram(self.df, x=x_col, nbins=nbins,
                              color=color_col,
                              title=titulo or f'Histograma de {x_col}')
            
            fig.update_layout(
                xaxis_title=x_col,
                yaxis_title='Frequência'
            )
            return fig
        except Exception as e:
            print(f"Erro ao gerar histograma: {e}")
            return self._criar_figura_erro(f"Erro ao gerar histograma: {str(e)[:50]}")
    
    def plot_box(self, x_col: str, y_col: str,
                color_col: Optional[str] = None,
                titulo: str = "") -> go.Figure:
        """
        Gera box plot com tratamento de erro.
        """
        try:
            # Converter coluna y para numérica
            df_temp = self.df.copy()
            df_temp[y_col] = pd.to_numeric(df_temp[y_col], errors='coerce')
            
            # Remover NaN
            df_temp = df_temp.dropna(subset=[x_col, y_col])
            
            if df_temp.empty:
                return self._criar_figura_erro("Dados insuficientes para box plot")
            
            fig = px.box(df_temp, x=x_col, y=y_col,
                        color=color_col,
                        title=titulo or f'Box Plot: {y_col} por {x_col}')
            return fig
        except Exception as e:
            print(f"Erro ao gerar box plot: {e}")
            return self._criar_figura_erro(f"Erro ao gerar box plot: {str(e)[:50]}")
    
    def plot_heatmap(self, x_col: str, y_col: str,
                    titulo: str = "", colorscale: str = 'Viridis') -> go.Figure:
        """
        Gera mapa de calor (heatmap) com tratamento de erro.
        """
        try:
            # Criar tabela cruzada
            df_cross = pd.crosstab(self.df[x_col], self.df[y_col])
            
            if df_cross.empty:
                return self._criar_figura_erro("Dados insuficientes para heatmap")
            
            fig = px.imshow(df_cross,
                           title=titulo or f'Heatmap: {x_col} vs {y_col}',
                           labels=dict(x=x_col, y=y_col, color='Contagem'),
                           color_continuous_scale=colorscale)
            
            return fig
        except Exception as e:
            print(f"Erro ao gerar heatmap: {e}")
            return self._criar_figura_erro(f"Erro ao gerar heatmap: {str(e)[:50]}")
    
    def plot_scatter(self, x_col: str, y_col: str,
                    color_col: Optional[str] = None,
                    size_col: Optional[str] = None,
                    titulo: str = "") -> go.Figure:
        """
        Gera gráfico de dispersão com tratamento de erro.
        """
        try:
            # Converter colunas para numéricas se possível
            df_temp = self.df.copy()
            df_temp[x_col] = pd.to_numeric(df_temp[x_col], errors='ignore')
            df_temp[y_col] = pd.to_numeric(df_temp[y_col], errors='ignore')
            
            fig = px.scatter(df_temp, x=x_col, y=y_col,
                            color=color_col,
                            size=size_col,
                            title=titulo or f'Dispersão: {y_col} vs {x_col}')
            
            fig.update_layout(
                xaxis_title=x_col,
                yaxis_title=y_col
            )
            return fig
        except Exception as e:
            print(f"Erro ao gerar gráfico de dispersão: {e}")
            return self._criar_figura_erro(f"Erro ao gerar gráfico de dispersão: {str(e)[:50]}")
    
    def plot_tensao_por_regiao(self, tipo: str = 'barras', 
                              titulo: str = "Distribuição de Tensão por Região") -> go.Figure:
        """
        Plota distribuição de tensão por região geoelétrica.
        """
        try:
            # Filtrar apenas linhas com tensão extraída
            df_tensao = self.df.copy()
            df_tensao['Tensão_kV'] = pd.to_numeric(df_tensao['Tensão_kV'], errors='coerce')
            df_tensao = df_tensao.dropna(subset=['Tensão_kV', 'Área Geoelétrica'])
            
            if df_tensao.empty:
                return self._criar_figura_erro("Não foi possível extrair tensões dos dados")
            
            # Criar categorias de tensão
            df_tensao['Faixa_Tensão'] = pd.cut(
                df_tensao['Tensão_kV'],
                bins=[0, 500, 700, 900, float('inf')],
                labels=['< 500 kV', '500-700 kV', '700-900 kV', '> 900 kV']
            )
            
            if tipo == 'pizza':
                # Distribuição geral de faixas de tensão
                faixa_counts = df_tensao['Faixa_Tensão'].value_counts().reset_index()
                fig = px.pie(faixa_counts, values='count', names='Faixa_Tensão',
                            title=titulo)
            else:  # barras
                # Agrupar por região e faixa de tensão
                df_agrupado = df_tensao.groupby(['Área Geoelétrica', 'Faixa_Tensão']).size().reset_index(name='Contagem')
                fig = px.bar(df_agrupado, x='Área Geoelétrica', y='Contagem', 
                            color='Faixa_Tensão',
                            title=titulo,
                            barmode='stack')
            
            return fig
        except Exception as e:
            print(f"Erro ao gerar gráfico de tensão: {e}")
            return self._criar_figura_erro(f"Erro ao gerar gráfico de tensão: {str(e)[:50]}")
    
    def plot_horizonte_por_volume(self, tipo: str = 'barras',
                                 titulo: str = "Distribuição de Horizonte por Volume") -> go.Figure:
        """
        Plota distribuição de horizonte por volume.
        """
        try:
            # Agrupar por Volume e Horizonte
            df_agrupado = self.df.groupby(['Volume', 'Horizonte']).size().reset_index(name='Contagem')
            
            if tipo == 'pizza':
                # Subplots para cada volume
                volumes = df_agrupado['Volume'].unique()
                if len(volumes) == 0:
                    return self._criar_figura_erro("Nenhum volume encontrado")
                    
                n_cols = min(3, len(volumes))
                n_rows = (len(volumes) + n_cols - 1) // n_cols
                
                fig = make_subplots(
                    rows=n_rows, cols=n_cols,
                    subplot_titles=[f'Volume: {v}' for v in volumes],
                    specs=[[{'type': 'domain'}] * n_cols] * n_rows
                )
                
                for i, volume in enumerate(volumes):
                    row = i // n_cols + 1
                    col = i % n_cols + 1
                    
                    df_volume = df_agrupado[df_agrupado['Volume'] == volume]
                    
                    fig.add_trace(
                        go.Pie(labels=df_volume['Horizonte'], 
                              values=df_volume['Contagem'],
                              name=f'Volume {volume}'),
                        row=row, col=col
                    )
                
                fig.update_layout(title_text=titulo, height=300 * n_rows)
                
            else:  # barras
                fig = px.bar(df_agrupado, x='Volume', y='Contagem', 
                            color='Horizonte',
                            title=titulo,
                            barmode='group')
            
            return fig
        except Exception as e:
            print(f"Erro ao gerar gráfico de horizonte: {e}")
            return self._criar_figura_erro(f"Erro ao gerar gráfico de horizonte: {str(e)[:50]}")
    
    def plot_volume_por_area(self, tipo: str = 'heatmap',
                            titulo: str = "Volume por Área Geoelétrica") -> go.Figure:
        """
        Plota relação entre volume e área geoelétrica.
        """
        try:
            if tipo == 'heatmap':
                # Heatmap
                heatmap_data = pd.crosstab(self.df['Volume'], self.df['Área Geoelétrica'])
                if heatmap_data.empty:
                    return self._criar_figura_erro("Dados insuficientes para heatmap")
                    
                fig = px.imshow(heatmap_data,
                               title=titulo,
                               labels=dict(x="Área Geoelétrica", y="Volume", color="Contagem"),
                               color_continuous_scale='Viridis')
            else:
                # Barras agrupadas
                df_agrupado = self.df.groupby(['Volume', 'Área Geoelétrica']).size().reset_index(name='Contagem')
                fig = px.bar(df_agrupado, x='Volume', y='Contagem',
                            color='Área Geoelétrica',
                            title=titulo,
                            barmode='group')
            
            return fig
        except Exception as e:
            print(f"Erro ao gerar gráfico volume por área: {e}")
            return self._criar_figura_erro(f"Erro ao gerar gráfico volume por área: {str(e)[:50]}")
    
    def get_insights(self) -> Dict:
        """
        Retorna insights principais dos dados.
        """
        try:
            metricas = self.get_metricas_principais()
            
            if not metricas:
                return {
                    'metricas': {},
                    'insights': {
                        'volume_mais_comum': "Nenhum dado disponível",
                        'area_mais_comum': "Nenhum dado disponível",
                        'horizonte_mais_comum': "Nenhum dado disponível",
                        'tensao_dominante': "Nenhum dado disponível",
                        'proporcao_cc_ca': "Nenhum dado disponível"
                    }
                }
            
            # Insights adicionais
            distribuicao_volume = metricas.get('distribuicao_volume', {})
            distribuicao_area = metricas.get('distribuicao_area', {})
            distribuicao_horizonte = metricas.get('distribuicao_horizonte', {})
            
            volume_mais_comum = max(distribuicao_volume.items(), key=lambda x: x[1]) if distribuicao_volume else ("Nenhum", 0)
            area_mais_comum = max(distribuicao_area.items(), key=lambda x: x[1]) if distribuicao_area else ("Nenhum", 0)
            horizonte_mais_comum = max(distribuicao_horizonte.items(), key=lambda x: x[1]) if distribuicao_horizonte else ("Nenhum", 0)
            
            return {
                'metricas': metricas,
                'insights': {
                    'volume_mais_comum': f"{volume_mais_comum[0]} ({volume_mais_comum[1]} contingências)",
                    'area_mais_comum': f"{area_mais_comum[0]} ({area_mais_comum[1]} contingências)",
                    'horizonte_mais_comum': f"{horizonte_mais_comum[0]} ({horizonte_mais_comum[1]} contingências)",
                    'tensao_dominante': f"{metricas.get('tensao_media', 0):.1f} kV (média)",
                    'proporcao_cc_ca': f"CC: {self.df[self.df['Tipo_Contingência'] == 'CC'].shape[0]}, "
                                     f"CA: {self.df[self.df['Tipo_Contingência'] == 'CA'].shape[0]}"
                }
            }
        except Exception as e:
            print(f"Erro ao gerar insights: {e}")
            return {
                'metricas': {},
                'insights': {}
            }
    
    def _criar_figura_erro(self, mensagem: str) -> go.Figure:
        """Cria uma figura de erro quando não é possível gerar o gráfico."""
        fig = go.Figure()
        fig.add_annotation(
            text=mensagem,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color="red")
        )
        fig.update_layout(
            title="Erro ao gerar gráfico",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white'
        )
        return fig
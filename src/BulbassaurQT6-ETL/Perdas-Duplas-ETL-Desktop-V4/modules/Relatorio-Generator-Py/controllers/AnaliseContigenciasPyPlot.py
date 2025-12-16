import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
from typing import Optional, List, Dict, Union
import numpy as np

class AnalisadorContingencias:
    """
    Classe para análise de dados de contingências duplas.
    Gera gráficos e insights a partir de dados estruturados.
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
        self.cor_paleta = px.colors.qualitative.Set3  # Paleta de cores consistente
        
    def _preprocessar_dados(self) -> None:
        """Preprocessa os dados extraindo informações adicionais."""
        # Extrair tensão (kV) da coluna de contingência
        self.df['Tensão_kV'] = self.df['Contingência Dupla'].apply(self._extrair_tensao)
        
        # Extrair tipo de contingência
        self.df['Tipo_Contingência'] = self.df['Contingência Dupla'].apply(
            lambda x: 'CC' if 'CC' in x else 'CA'
        )
        
        # Criar coluna simplificada para análise
        self.df['Contingência_Simplificada'] = self.df['Contingência Dupla'].apply(
            self._simplificar_contingencia
        )
        
        # Contar ocorrências
        self.df['Contagem'] = 1
        
    @staticmethod
    def _extrair_tensao(texto: str) -> Optional[float]:
        """Extrai o valor da tensão em kV do texto."""
        padrao = r'(\d+)\s*kV'
        match = re.search(padrao, texto, re.IGNORECASE)
        return float(match.group(1)) if match else None
    
    @staticmethod
    def _simplificar_contingencia(texto: str) -> str:
        """Simplifica o nome da contingência para análise."""
        # Remover detalhes específicos (C1, C2, etc)
        texto = re.sub(r'C\d+\s+e\s+C\d+', '', texto)
        texto = re.sub(r'C\d+', '', texto)
        # Manter apenas a parte principal
        partes = texto.split('-')
        if len(partes) > 1:
            return f"{partes[0].strip()} - {partes[1].split()[0]}"
        return texto[:40] + '...' if len(texto) > 40 else texto
    
    def gerar_grafico(self, 
                     tipo: str = 'barras',
                     x_col: Optional[str] = None,
                     y_col: Optional[str] = None,
                     color_col: Optional[str] = None,
                     titulo: str = '',
                     **kwargs) -> go.Figure:
        """
        Gera gráficos de diferentes tipos.
        
        Args:
            tipo: 'barras', 'linhas', 'pizza', 'dispersão', 'box', 'violino', 'histograma', 'heatmap'
            x_col: Coluna para eixo X
            y_col: Coluna para eixo Y
            color_col: Coluna para colorir
            titulo: Título do gráfico
            **kwargs: Argumentos adicionais para Plotly Express
            
        Returns:
            go.Figure: Objeto de figura do Plotly
        """
        # Configurações padrão
        configs = {
            'barras': self._gerar_barras,
            'linhas': self._gerar_linhas,
            'pizza': self._gerar_pizza,
            'dispersão': self._gerar_dispersao,
            'box': self._gerar_box,
            'violino': self._gerar_violino,
            'histograma': self._gerar_histograma,
            'heatmap': self._gerar_heatmap
        }
        
        if tipo not in configs:
            raise ValueError(f"Tipo '{tipo}' não suportado. Use: {list(configs.keys())}")
        
        return configs[tipo](x_col, y_col, color_col, titulo, **kwargs)
    
    def _gerar_barras(self, x_col, y_col, color_col, titulo, **kwargs) -> go.Figure:
        """Gera gráfico de barras."""
        if y_col is None:
            # Contar ocorrências se y_col não for especificado
            df_agg = self.df.groupby(x_col).size().reset_index(name='Contagem')
            fig = px.bar(df_agg, x=x_col, y='Contagem', 
                        color=color_col if color_col else None,
                        title=titulo or f'Distribuição por {x_col}',
                        color_discrete_sequence=self.cor_paleta,
                        **kwargs)
        else:
            fig = px.bar(self.df, x=x_col, y=y_col, 
                        color=color_col if color_col else None,
                        title=titulo,
                        color_discrete_sequence=self.cor_paleta,
                        **kwargs)
        
        # Melhorar layout
        fig.update_layout(
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title=y_col.replace('_', ' ').title() if y_col else 'Contagem',
            showlegend=color_col is not None
        )
        return fig
    
    def _gerar_linhas(self, x_col, y_col, color_col, titulo, **kwargs) -> go.Figure:
        """Gera gráfico de linhas."""
        if y_col is None:
            raise ValueError("Para gráfico de linhas, y_col é obrigatório")
        
        fig = px.line(self.df, x=x_col, y=y_col, 
                     color=color_col if color_col else None,
                     title=titulo,
                     color_discrete_sequence=self.cor_paleta,
                     **kwargs)
        
        fig.update_layout(
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title=y_col.replace('_', ' ').title()
        )
        return fig
    
    def _gerar_pizza(self, x_col, y_col, color_col, titulo, **kwargs) -> go.Figure:
        """Gera gráfico de pizza."""
        if y_col is None:
            # Contar ocorrências
            df_agg = self.df[x_col].value_counts().reset_index()
            df_agg.columns = [x_col, 'Contagem']
            fig = px.pie(df_agg, values='Contagem', names=x_col,
                        title=titulo or f'Distribuição por {x_col}',
                        color_discrete_sequence=self.cor_paleta,
                        **kwargs)
        else:
            fig = px.pie(self.df, values=y_col, names=x_col,
                        color=color_col if color_col else None,
                        title=titulo,
                        color_discrete_sequence=self.cor_paleta,
                        **kwargs)
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        return fig
    
    def _gerar_dispersao(self, x_col, y_col, color_col, titulo, **kwargs) -> go.Figure:
        """Gera gráfico de dispersão."""
        if y_col is None:
            raise ValueError("Para gráfico de dispersão, y_col é obrigatório")
        
        fig = px.scatter(self.df, x=x_col, y=y_col,
                        color=color_col if color_col else None,
                        title=titulo,
                        color_discrete_sequence=self.cor_paleta,
                        **kwargs)
        
        fig.update_layout(
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title=y_col.replace('_', ' ').title()
        )
        return fig
    
    def _gerar_box(self, x_col, y_col, color_col, titulo, **kwargs) -> go.Figure:
        """Gera gráfico box plot."""
        if y_col is None:
            raise ValueError("Para gráfico box, y_col é obrigatório")
        
        fig = px.box(self.df, x=x_col, y=y_col,
                    color=color_col if color_col else None,
                    title=titulo,
                    color_discrete_sequence=self.cor_paleta,
                    **kwargs)
        
        return fig
    
    def _gerar_violino(self, x_col, y_col, color_col, titulo, **kwargs) -> go.Figure:
        """Gera gráfico violin plot."""
        if y_col is None:
            raise ValueError("Para gráfico violino, y_col é obrigatório")
        
        fig = px.violin(self.df, x=x_col, y=y_col,
                       color=color_col if color_col else None,
                       title=titulo,
                       color_discrete_sequence=self.cor_paleta,
                       **kwargs)
        
        return fig
    
    def _gerar_histograma(self, x_col, y_col, color_col, titulo, **kwargs) -> go.Figure:
        """Gera histograma."""
        fig = px.histogram(self.df, x=x_col,
                          color=color_col if color_col else None,
                          title=titulo,
                          color_discrete_sequence=self.cor_paleta,
                          **kwargs)
        
        fig.update_layout(
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title='Frequência'
        )
        return fig
    
    def _gerar_heatmap(self, x_col, y_col, color_col, titulo, **kwargs) -> go.Figure:
        """Gera mapa de calor."""
        if x_col is None or y_col is None:
            raise ValueError("Para heatmap, x_col e y_col são obrigatórios")
        
        # Criar tabela cruzada
        df_cross = pd.crosstab(self.df[x_col], self.df[y_col])
        
        fig = px.imshow(df_cross,
                       title=titulo,
                       labels=dict(x=x_col.replace('_', ' ').title(),
                                  y=y_col.replace('_', ' ').title(),
                                  color='Contagem'),
                       color_continuous_scale='Viridis',
                       **kwargs)
        
        return fig
    
    def analise_volume_regiao(self) -> Dict:
        """
        Retorna insights sobre Volume por Região.
        
        Returns:
            Dict: Dicionário com métricas e DataFrame agregado
        """
        # Agrupar por Volume e Área Geoelétrica
        df_agrupado = self.df.groupby(['Volume', 'Área Geoelétrica']).agg({
            'Contagem': 'sum',
            'Horizonte': lambda x: x.mode()[0] if not x.mode().empty else None,
            'Contingência Dupla': 'count'
        }).reset_index()
        
        df_agrupado = df_agrupado.rename(columns={
            'Contingência Dupla': 'Total_Contingencias',
            'Horizonte': 'Horizonte_Mais_Comum'
        })
        
        insights = {
            'total_regioes': self.df['Área Geoelétrica'].nunique(),
            'total_volumes': self.df['Volume'].nunique(),
            'distribuicao_volume': self.df['Volume'].value_counts().to_dict(),
            'distribuicao_regiao': self.df['Área Geoelétrica'].value_counts().to_dict(),
            'dados_agrupados': df_agrupado
        }
        
        return insights
    
    def plot_distribuicao_tensao_regiao(self, tipo_grafico: str = 'pizza') -> go.Figure:
        """
        Plota distribuição de tensão por região geoelétrica.
        
        Args:
            tipo_grafico: 'pizza', 'barras' ou 'heatmap'
            
        Returns:
            go.Figure: Gráfico da distribuição
        """
        # Filtrar apenas linhas com tensão extraída
        df_tensao = self.df.dropna(subset=['Tensão_kV'])
        
        if df_tensao.empty:
            raise ValueError("Não foi possível extrair tensões dos dados")
        
        # Criar categorias de tensão
        df_tensao['Faixa_Tensão'] = pd.cut(
            df_tensao['Tensão_kV'],
            bins=[0, 500, 700, 900, float('inf')],
            labels=['< 500 kV', '500-700 kV', '700-900 kV', '> 900 kV']
        )
        
        # Agrupar por região e faixa de tensão
        df_agrupado = df_tensao.groupby(['Área Geoelétrica', 'Faixa_Tensão']).size().reset_index(name='Contagem')
        
        if tipo_grafico == 'pizza':
            fig = px.pie(df_agrupado, values='Contagem', names='Faixa_Tensão',
                        title='Distribuição de Tensão por Faixa',
                        color_discrete_sequence=self.cor_paleta)
            
        elif tipo_grafico == 'barras':
            fig = px.bar(df_agrupado, x='Área Geoelétrica', y='Contagem', color='Faixa_Tensão',
                        title='Distribuição de Tensão por Região',
                        barmode='stack',
                        color_discrete_sequence=self.cor_paleta)
            
        elif tipo_grafico == 'heatmap':
            # Pivot para heatmap
            df_pivot = df_agrupado.pivot(index='Área Geoelétrica', 
                                       columns='Faixa_Tensão', 
                                       values='Contagem').fillna(0)
            
            fig = px.imshow(df_pivot,
                           title='Heatmap: Tensão por Região',
                           labels=dict(color='Número de Contingências'),
                           color_continuous_scale='Viridis')
        
        return fig
    
    def plot_horizonte_por_volume(self, tipo_grafico: str = 'barras') -> go.Figure:
        """
        Plota distribuição de horizonte (curto/médio/longo prazo) por volume.
        
        Args:
            tipo_grafico: 'barras', 'pizza' ou 'violino'
            
        Returns:
            go.Figure: Gráfico da distribuição
        """
        # Agrupar por Volume e Horizonte
        df_agrupado = self.df.groupby(['Volume', 'Horizonte']).size().reset_index(name='Contagem')
        
        if tipo_grafico == 'barras':
            fig = px.bar(df_agrupado, x='Volume', y='Contagem', color='Horizonte',
                        title='Distribuição de Horizonte por Volume',
                        barmode='group',
                        color_discrete_sequence=px.colors.qualitative.Pastel)
            
        elif tipo_grafico == 'pizza':
            # Para pizza, criar subplots por volume
            volumes = df_agrupado['Volume'].unique()
            n_cols = min(3, len(volumes))
            n_rows = (len(volumes) + n_cols - 1) // n_cols
            
            fig = make_subplots(
                rows=n_rows, cols=n_cols,
                subplot_titles=[f'Volume {v}' for v in volumes],
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
            
            fig.update_layout(title_text='Distribuição de Horizonte por Volume (Subplots)')
            
        elif tipo_grafico == 'violino':
            # Para violino, precisamos de dados numéricos
            # Criar mapeamento numérico para horizonte
            ordem_horizonte = {'Curto Prazo': 1, 'Médio Prazo': 2, 'Longo Prazo': 3}
            df_num = self.df.copy()
            df_num['Horizonte_Num'] = df_num['Horizonte'].map(ordem_horizonte)
            
            fig = px.violin(df_num, x='Volume', y='Horizonte_Num', color='Horizonte',
                           title='Distribuição de Horizonte por Volume',
                           box=True,
                           color_discrete_sequence=px.colors.qualitative.Pastel)
            
            fig.update_yaxes(title='Horizonte (1=Curto, 2=Médio, 3=Longo)')
        
        return fig
    
    def dashboard_completo(self) -> go.Figure:
        """
        Cria um dashboard completo com múltiplos gráficos.
        
        Returns:
            go.Figure: Dashboard com subplots
        """
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=(
                'Contingências por Volume',
                'Distribuição por Área Geoelétrica',
                'Tensão por Região',
                'Horizonte por Volume',
                'Tipo de Contingência',
                'Mapa de Calor: Volume vs Área'
            ),
            specs=[
                [{'type': 'bar'}, {'type': 'pie'}, {'type': 'bar'}],
                [{'type': 'bar'}, {'type': 'pie'}, {'type': 'heatmap'}]
            ]
        )
        
        # 1. Contingências por Volume
        vol_counts = self.df['Volume'].value_counts().reset_index()
        fig.add_trace(
            go.Bar(x=vol_counts['Volume'], y=vol_counts['count'], 
                  name='Por Volume', marker_color='lightblue'),
            row=1, col=1
        )
        
        # 2. Distribuição por Área Geoelétrica
        area_counts = self.df['Área Geoelétrica'].value_counts().reset_index()
        fig.add_trace(
            go.Pie(labels=area_counts['Área Geoelétrica'], 
                  values=area_counts['count'],
                  name='Por Área'),
            row=1, col=2
        )
        
        # 3. Tensão por Região
        df_tensao = self.df.dropna(subset=['Tensão_kV'])
        if not df_tensao.empty:
            df_tensao_agg = df_tensao.groupby(['Área Geoelétrica', 'Tensão_kV']).size().reset_index(name='Contagem')
            for area in df_tensao_agg['Área Geoelétrica'].unique():
                df_area = df_tensao_agg[df_tensao_agg['Área Geoelétrica'] == area]
                fig.add_trace(
                    go.Bar(x=df_area['Tensão_kV'], y=df_area['Contagem'],
                          name=area, showlegend=True),
                    row=1, col=3
                )
        
        # 4. Horizonte por Volume
        horizonte_counts = pd.crosstab(self.df['Volume'], self.df['Horizonte'])
        for horizonte in horizonte_counts.columns:
            fig.add_trace(
                go.Bar(x=horizonte_counts.index, y=horizonte_counts[horizonte],
                      name=horizonte, showlegend=True),
                row=2, col=1
            )
        
        # 5. Tipo de Contingência
        tipo_counts = self.df['Tipo_Contingência'].value_counts().reset_index()
        fig.add_trace(
            go.Pie(labels=tipo_counts['Tipo_Contingência'], 
                  values=tipo_counts['count'],
                  name='Tipo Contingência'),
            row=2, col=2
        )
        
        # 6. Heatmap: Volume vs Área
        heatmap_data = pd.crosstab(self.df['Volume'], self.df['Área Geoelétrica'])
        fig.add_trace(
            go.Heatmap(z=heatmap_data.values,
                      x=heatmap_data.columns,
                      y=heatmap_data.index,
                      colorscale='Viridis',
                      name='Volume vs Área'),
            row=2, col=3
        )
        
        fig.update_layout(
            height=900,
            title_text="Dashboard de Análise de Contingências",
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        return fig
    
    def exportar_relatorio(self, caminho_arquivo: str = 'relatorio_insights.html'):
        """
        Exporta um relatório HTML completo com gráficos.
        
        Args:
            caminho_arquivo: Caminho para salvar o relatório HTML
        """
        import plotly.io as pio
        
        # Criar figura com todos os gráficos
        fig_dashboard = self.dashboard_completo()
        
        # Gerar insights textuais
        insights = self.analise_volume_regiao()
        
        # Criar HTML
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Relatório de Análise de Contingências</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ text-align: center; margin-bottom: 40px; }}
                .insights {{ background: #f5f5f5; padding: 20px; border-radius: 10px; margin-bottom: 30px; }}
                .graph {{ margin: 30px 0; }}
                .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }}
                .metric-card {{ background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                .highlight {{ color: #e74c3c; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Relatório de Análise de Contingências Duplas</h1>
                    <p>Gerado em: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}</p>
                </div>
                
                <div class="insights">
                    <h2>📈 Insights Principais</h2>
                    <div class="metrics">
                        <div class="metric-card">
                            <h3>📁 Volumes Analisados</h3>
                            <p>Total: <span class="highlight">{insights['total_volumes']}</span></p>
                            <ul>
                                {''.join([f'<li>{vol}: {count} contingências</li>' for vol, count in insights['distribuicao_volume'].items()])}
                            </ul>
                        </div>
                        
                        <div class="metric-card">
                            <h3>🌍 Regiões Geoelétricas</h3>
                            <p>Total: <span class="highlight">{insights['total_regioes']}</span></p>
                            <ul>
                                {''.join([f'<li>{regiao}: {count} contingências</li>' for regiao, count in list(insights['distribuicao_regiao'].items())[:5]])}
                            </ul>
                        </div>
                        
                        <div class="metric-card">
                            <h3>⏰ Distribuição Temporal</h3>
                            <p>Horizonte mais comum por volume:</p>
                            {self._gerar_tabela_horizonte()}
                        </div>
                    </div>
                </div>
                
                <div class="graph">
                    <h2>🎯 Dashboard Interativo</h2>
                    <div id="dashboard"></div>
                </div>
                
                <div class="graph">
                    <h2>🔌 Distribuição de Tensão por Região</h2>
                    <div id="tensao"></div>
                </div>
                
                <div class="graph">
                    <h2>📅 Horizonte por Volume</h2>
                    <div id="horizonte"></div>
                </div>
            </div>
            
            <script>
                // Dashboard
                var dashboard = {pio.to_json(fig_dashboard)};
                Plotly.newPlot('dashboard', dashboard.data, dashboard.layout);
                
                // Gráfico de tensão
                var figTensao = {pio.to_json(self.plot_distribuicao_tensao_regiao('barras'))};
                Plotly.newPlot('tensao', figTensao.data, figTensao.layout);
                
                // Gráfico de horizonte
                var figHorizonte = {pio.to_json(self.plot_horizonte_por_volume('barras'))};
                Plotly.newPlot('horizonte', figHorizonte.data, figHorizonte.layout);
            </script>
        </body>
        </html>
        """
        
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            f.write(html_template)
        
        print(f"✅ Relatório exportado: {caminho_arquivo}")
    
    def _gerar_tabela_horizonte(self) -> str:
        """Gera HTML para tabela de horizonte."""
        df_horizonte = self.df.groupby(['Volume', 'Horizonte']).size().reset_index(name='Contagem')
        
        html = '<table style="width:100%; border-collapse: collapse;">'
        html += '<tr><th>Volume</th><th>Horizonte</th><th>Contagem</th></tr>'
        
        for _, row in df_horizonte.iterrows():
            html += f'<tr><td>{row["Volume"]}</td><td>{row["Horizonte"]}</td><td>{row["Contagem"]}</td></tr>'
        
        html += '</table>'
        return html
import pandas as pd
import re
import fitz

# ===============================================================
# CLASSE: ETLRepository (MODEL - Camada de Acesso a Dados)
# ===============================================================

class ETLRepository:
    """Gerencia a lógica de Extração de dados de baixo nível para documentos PDF."""

    def __init__(self):
        """Inicializa o ETLRepository."""
        pass

    def extract_text_from_pdf(self, pdf_path, page_range=None):
        """
        Extrai texto de um arquivo PDF, opcionalmente limitando a um intervalo de páginas.

        Args:
            pdf_path (str): O caminho para o arquivo PDF.
            page_range (list, optional): Uma lista de índices de páginas (base 0) a serem processadas. Se None, todas as páginas são processadas. Defaults to None.

        Returns:
            str: O texto concatenado das páginas extraídas, com marcadores de página.
        """
        doc = fitz.open(pdf_path)
        full_text = ""
        
        # Determina as páginas a serem processadas
        if page_range is None:
            pages_to_process = range(len(doc))
        else:
            # Filtra páginas para garantir que estão dentro do limite do documento
            pages_to_process = [p for p in page_range if p < len(doc)]
        
        for page_num in pages_to_process:
            page = doc.load_page(page_num)
            full_text += f"\n--- Página {page_num + 1} ---\n" # Adiciona marcador de página
            full_text += page.get_text()
        
        doc.close()
        return full_text

    def _clean_contingency_name(self, contingency_name, add_lt_option, prev_part_ends_with_lt=False):
        """
        Limpa e padroniza o nome de uma contingência, removendo termos desnecessários e adicionando 'LT' se aplicável.

        Args:
            contingency_name (str): O nome original da contingência.
            add_lt_option (bool): Se True, tenta adicionar 'LT' se 'kV' estiver presente e 'LT' não for duplicado.
            prev_part_ends_with_lt (bool, optional): Indica se a parte anterior da contingência (em caso de múltiplas) termina com 'LT'. Usado para evitar duplicação. Defaults to False.

        Returns:
            str: O nome da contingência limpo e padronizado.
        """
        # Remove o texto "Contingência Dupla" e variações (ex: "Contingência Dupla da", "Contingência Dupla das")
        cleaned_name = re.sub(r'Contingência Dupla (da|das)?\s*', '', contingency_name).strip()
        
        # Adiciona "LT" se necessário, evitando duplicações e garantindo formato
        if add_lt_option:
            if not cleaned_name.startswith('LT ') and ' kV ' in cleaned_name:
                # Se não começa com 'LT ' e contém ' kV ', adiciona 'LT '
                cleaned_name = 'LT ' + cleaned_name
            elif cleaned_name.startswith('LT LT '):
                # Corrige caso haja "LT LT " duplicado no início
                cleaned_name = cleaned_name.replace('LT LT ', 'LT ')
            elif prev_part_ends_with_lt and cleaned_name.startswith('LT '):
                # Remove 'LT ' duplicado se a parte anterior já terminou com 'LT'
                cleaned_name = cleaned_name[3:].strip() # Remove apenas o primeiro 'LT ' 
        return cleaned_name

# ===============================================================
# CLASSE: ETLController (CONTROLLER - Camada de Lógica de Negócio)
# ===============================================================

class ETLController:
    """Orquestra as operações de ETL, utilizando o ETLRepository para acesso a dados."""
    def __init__(self):
        """Inicializa o ETLController e seu repositório de dados."""
        self._etl_repository = ETLRepository()

    def extract_pdf_text(self, pdf_path, page_range=None):
        """
        Extrai texto de um arquivo PDF usando o ETLRepository.

        Args:
            pdf_path (str): O caminho para o arquivo PDF.
            page_range (list, optional): Uma lista de índices de páginas (base 0) a serem processadas. Se None, todas as páginas são processadas. Defaults to None.

        Returns:
            str: O texto concatenado das páginas extraídas.
        """
        return self._etl_repository.extract_text_from_pdf(pdf_path, page_range)

    def process_outro_script(self, texto):
        """
        Função placeholder para outros scripts de processamento.
        Retorna um DataFrame de exemplo.

        Args:
            texto (str): O texto a ser processado.

        Returns:
            pd.DataFrame: DataFrame de exemplo.
        """
        return pd.DataFrame({"Exemplo": ["Script 2 em desenvolvimento"]})

    def process_contingencias_duplas(self, texto, process_options=None):
        """
        Processa o texto extraído do PDF para identificar e tabular contingências duplas.

        Args:
            texto (str): O texto completo extraído do PDF.
            process_options (dict, optional): Opções de processamento, como 'separar_duplas' e 'adicionar_lt'.
                                             Defaults to {'separar_duplas': True, 'adicionar_lt': True}.

        Returns:
            pd.DataFrame: Um DataFrame contendo as contingências identificadas e seus atributos.
        """
        if process_options is None:
            process_options = {'separar_duplas': True, 'adicionar_lt': True}

        dados = []
        volume_atual = None
        area_geoelerica_atual = None
        prazo_atual = None

        # Itera sobre cada linha do texto para extrair informações
        for linha in texto.strip().split('\n'):
            linha = linha.strip()
            # Ignora linhas vazias ou marcadores de página
            if not linha or linha.startswith('--- Página'):
                continue
            
            # Identifica Volume e Área Geoelétrica
            match_volume = re.match(r'(\d+\.\d+)\s+Volume\s+\d+\s*-\s*(.+)', linha)
            if match_volume:
                volume_atual = f"Volume {match_volume.group(1)}"
                area_geoelerica_atual = match_volume.group(2)
                continue
            
            # Identifica Prazo (Curto Prazo ou Médio Prazo)
            match_prazo = re.match(r'\d+\.\d+\.\d+\s+(Curto\s+Prazo|Médio\s+Prazo)', linha)
            if match_prazo:
                prazo_atual = match_prazo.group(1)
                continue
            
            # Identifica contingências marcadas com '•' ou '-'
            if linha.startswith('•') or linha.startswith('-'):
                contingencia = linha.replace('•', '').replace('-','').strip()
                
                # VERIFICAÇÃO DE CONTINGÊNCIAS DUPLAS
                if 'Contingência Dupla' in contingencia and process_options['separar_duplas']:
                    # Processa contingências que contêm o termo "Contingência Dupla"
                    contingencia_limpa = re.sub(r'Contingência Dupla (da|das)?\s*', '', contingencia).strip()
                    
                    # Verifica se há múltiplas contingências separadas por " e "
                    if ' e ' in contingencia_limpa:
                        partes = contingencia_limpa.split(' e ')
                        
                        # Processa cada parte da contingência individualmente
                        for i, parte in enumerate(partes):
                            parte = parte.strip()
                            
                            # Determina se a parte anterior terminou com 'LT' para evitar duplicação
                            prev_part_ends_with_lt = (i > 0 and partes[i-1].strip().endswith('LT'))
                            # Usa o repositório para limpar o nome da contingência
                            cleaned_part = self._etl_repository._clean_contingency_name(parte, process_options['adicionar_lt'], prev_part_ends_with_lt)
                            
                            futura = "SIM" if prazo_atual == "Curto Prazo" else "NÃO"
                            
                            dados.append({
                                'Volume': volume_atual,
                                'Área Geoelétrica': area_geoelerica_atual,
                                'Perda Dupla': cleaned_part,
                                'Prazo': prazo_atual,
                                'Futura': futura,
                                'Contingência Dupla Mesma Linha': 'SIM' # Marcado como contingência dupla na mesma linha
                            })
                    else:
                        # É uma única contingência "dupla" (no termo, mas não separada por " e ")
                        # Usa o repositório para limpar o nome da contingência
                        cleaned_contingency = self._etl_repository._clean_contingency_name(contingencia, process_options['adicionar_lt'])
                        
                        futura = "SIM" if prazo_atual == "Curto Prazo" else "NÃO"
                        
                        dados.append({
                            'Volume': volume_atual,
                            'Área Geoelétrica': area_geoelerica_atual,
                            'Perda Dupla': cleaned_contingency,
                            'Prazo': prazo_atual,
                            'Futura': futura,
                            'Contingência Dupla Mesma Linha': 'NÃO'
                        })
                else:
                    # Não é uma "Contingência Dupla" explícita, processa normalmente
                    # Usa o repositório para limpar o nome da contingência
                    cleaned_contingency = self._etl_repository._clean_contingency_name(contingencia, process_options['adicionar_lt'])
                    
                    futura = "SIM" if prazo_atual == "Curto Prazo" else "NÃO"
                    
                    dados.append({
                        'Volume': volume_atual,
                        'Área Geoelétrica': area_geoelerica_atual,
                        'Perda Dupla': cleaned_contingency,
                        'Prazo': prazo_atual,
                        'Futura': futura,
                        'Contingência Dupla Mesma Linha': 'NÃO'
                    })

        # Cria DataFrame a partir dos dados extraídos
        df = pd.DataFrame(dados)
        
        # Reorganiza e padroniza as colunas do DataFrame
        colunas = ['Volume', 'Área Geoelétrica', 'Perda Dupla', 'Prazo', 'Futura', 'Contingência Dupla Mesma Linha']
        if not df.empty:
            df = df[colunas]
            # Padroniza a capitalização das colunas de texto usando o método privado
            df = self._standardize_dataframe_text_columns(df, ['Volume', 'Área Geoelétrica', 'Perda Dupla', 'Prazo'])
        
        return df

    def _standardize_dataframe_text_columns(self, df, columns_to_standardize):
        """
        Padroniza a capitalização das strings em colunas específicas de um DataFrame para o formato de título.

        Args:
            df (pd.DataFrame): O DataFrame a ser processado.
            columns_to_standardize (list): Uma lista de nomes de colunas cujos valores de string devem ser padronizados.

        Returns:
            pd.DataFrame: O DataFrame com as colunas de texto padronizadas.
        """
        for col in columns_to_standardize:
            # Verifica se a coluna existe e se é do tipo 'object' (geralmente strings)
            if col in df.columns and df[col].dtype == 'object': 
                # Aplica a função .title() a cada string na coluna
                df[col] = df[col].apply(lambda x: x.title() if isinstance(x, str) else x)
        return df



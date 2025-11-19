import pandas as pd
import re
import fitz

class ETLRepository:
    def __init__(self):
        pass

    def extract_text_from_pdf(self, pdf_path, page_range=None):
        doc = fitz.open(pdf_path)
        full_text = ""
        
        if page_range is None:
            pages_to_process = range(len(doc))
        else:
            pages_to_process = [p for p in page_range if p < len(doc)]
        
        for page_num in pages_to_process:
            page = doc.load_page(page_num)
            full_text += f"\n--- Página {page_num + 1} ---\n"
            full_text += page.get_text()
        
        doc.close()
        return full_text

    def _clean_contingency_name(self, contingency_name, add_lt_option, prev_part_ends_with_lt=False):
        # Remove o texto "Contingência Dupla" e variações
        cleaned_name = re.sub(r'Contingência Dupla (da|das)?\s*', '', contingency_name).strip()
        
        # Adiciona "LT" se necessário, evitando duplicações e garantindo formato
        if add_lt_option:
            if not cleaned_name.startswith('LT ') and ' kV ' in cleaned_name:
                # Se não começa com LT e tem kV, adiciona LT
                cleaned_name = 'LT ' + cleaned_name
            elif cleaned_name.startswith('LT LT '):
                # Corrige "LT LT" duplicado
                cleaned_name = cleaned_name.replace('LT LT ', 'LT ')
            elif prev_part_ends_with_lt and cleaned_name.startswith('LT '):
                # Remove LT duplicado se a parte anterior já terminou com LT
                cleaned_name = cleaned_name[3:].strip() # Remove apenas o primeiro 'LT ' 
        return cleaned_name

    def process_contingencias_duplas(self, texto, process_options=None):
        if process_options is None:
            process_options = {'separar_duplas': True, 'adicionar_lt': True}

        dados = []
        volume_atual = None
        area_geoelerica_atual = None
        prazo_atual = None

        for linha in texto.strip().split('\n'):
            linha = linha.strip()
            if not linha or linha.startswith('--- Página'):
                continue
            
            # Identifica Volume
            match_volume = re.match(r'(\d+\.\d+)\s+Volume\s+\d+\s*-\s*(.+)', linha)
            if match_volume:
                volume_atual = f"Volume {match_volume.group(1)}"
                area_geoelerica_atual = match_volume.group(2)
                continue
            
            # Identifica Prazo
            match_prazo = re.match(r'\d+\.\d+\.\d+\s+(Curto\s+Prazo|Médio\s+Prazo)', linha)
            if match_prazo:
                prazo_atual = match_prazo.group(1)
                continue
            
            # Identifica contingências
            if linha.startswith('•') or linha.startswith('-'):
                contingencia = linha.replace('•', '').replace('-','').strip()
                
                # VERIFICAÇÃO DAS CONTINGÊNCIAS DUPLAS
                if 'Contingência Dupla' in contingencia and process_options['separar_duplas']:
                    # Remove o texto "Contingência Dupla" e variações
                    contingencia_limpa = re.sub(r'Contingência Dupla (da|das)?\s*', '', contingencia).strip()
                    
                    # Verifica se tem múltiplas contingências separadas por " e "
                    if ' e ' in contingencia_limpa:
                        # Separa as contingências múltiplas
                        partes = contingencia_limpa.split(' e ')
                        
                        # Processa cada contingência individualmente
                        for i, parte in enumerate(partes):
                            parte = parte.strip()
                            
                            # Determina se a parte anterior termina com 'LT' para evitar duplicação
                            prev_part_ends_with_lt = (i > 0 and partes[i-1].strip().endswith('LT'))
                            cleaned_part = self._clean_contingency_name(parte, process_options['adicionar_lt'], prev_part_ends_with_lt)
                            
                            # Determina se é Futura baseado no prazo
                            futura = "SIM" if prazo_atual == "Curto Prazo" else "NÃO"
                            
                            dados.append({
                                'Volume': volume_atual,
                                'Área Geoelétrica': area_geoelerica_atual,
                                'Perda Dupla': cleaned_part,
                                'Prazo': prazo_atual,
                                'Futura': futura,
                                'Contingência Dupla Mesma Linha': 'SIM'
                            })
                    else:
                        # É uma única contingência
                        cleaned_contingency = self._clean_contingency_name(contingencia, process_options['adicionar_lt'])
                        
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
                    # Não é uma "Contingência Dupla", processa normalmente
                    cleaned_contingency = self._clean_contingency_name(contingencia, process_options['adicionar_lt'])
                    
                    futura = "SIM" if prazo_atual == "Curto Prazo" else "NÃO"
                    
                    dados.append({
                        'Volume': volume_atual,
                        'Área Geoelétrica': area_geoelerica_atual,
                        'Perda Dupla': cleaned_contingency,
                        'Prazo': prazo_atual,
                        'Futura': futura,
                        'Contingência Dupla Mesma Linha': 'NÃO'
                    })

        # Cria DataFrame
        df = pd.DataFrame(dados)
        
        # Reorganiza as colunas
        colunas = ['Volume', 'Área Geoelétrica', 'Perda Dupla', 'Prazo', 'Futura', 'Contingência Dupla Mesma Linha']
        if not df.empty:
            df = df[colunas]
            df = self._standardize_dataframe_text_columns(df, ['Volume', 'Área Geoelétrica', 'Perda Dupla', 'Prazo'])
        
        return df

    def _standardize_dataframe_text_columns(self, df, columns_to_standardize):
        for col in columns_to_standardize:
            if col in df.columns and df[col].dtype == 'object': # Verifica se a coluna existe e é do tipo objeto (string)
                df[col] = df[col].apply(lambda x: x.title() if isinstance(x, str) else x)
        return df

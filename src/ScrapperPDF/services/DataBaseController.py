# scripts/DataBaseController.py

import pandas as pd
import re
from abc import ABC, abstractmethod
from pathlib import Path
import sqlite3
import pyodbc

# --- 1. Mapeamento e Funções de Preparação de Dados (fora das classes) ---

COLUMN_MAPPING = {
    'EMPRESA': 'empresa', 'Cód ONS': 'cod_ons', 'Tensão (kV)': 'tensao_kv', 'De': 'ponto_de',
    'Até': 'ponto_ate', 'Ponta 2025 Valor': 'ponta_2025_valor', 'Ponta 2025 Anotacao': 'ponta_2025_anotacao',
    'Fora Ponta 2025 Valor': 'fora_ponta_2025_valor', 'Fora Ponta 2025 Anotacao': 'fora_ponta_2025_anotacao',
    'Ponta 2026 Valor': 'ponta_2026_valor', 'Ponta 2026 Anotacao': 'ponta_2026_anotacao',
    'Fora Ponta 2026 Valor': 'fora_ponta_2026_valor', 'Fora Ponta 2026 Anotacao': 'fora_ponta_2026_anotacao',
    'Ponta 2027 Valor': 'ponta_2027_valor', 'Ponta 2027 Anotacao': 'ponta_2027_anotacao',
    'Fora Ponta 2027 Valor': 'fora_ponta_2027_valor', 'Fora Ponta 2027 Anotacao': 'fora_ponta_2027_anotacao',
    'Ponta 2028 Valor': 'ponta_2028_valor', 'Ponta 2028 Anotacao': 'ponta_2028_anotacao',
    'Fora Ponta 2028 Valor': 'fora_ponta_2028_valor', 'Fora Ponta 2028 Anotacao': 'fora_ponta_2028_anotacao',
    'Anotacao': 'anotacao_geral'
}

def prepare_and_normalize_data(df_source: pd.DataFrame):
    """
    Orquestra a limpeza e normalização dos dados UMA ÚNICA VEZ.
    Retorna três DataFrames prontos para serem inseridos no banco.
    """
    print("1. Renomeando e limpando colunas...")
    df_source.rename(columns=COLUMN_MAPPING, inplace=True)
    
    print("2. Normalizando a estrutura de dados...")
    
    # Tabela de Empresas
    empresas_unicas = df_source['empresa'].unique()
    df_empresas = pd.DataFrame(empresas_unicas, columns=['nome_empresa'])
    df_empresas.insert(0, 'id_empresa', range(1, len(df_empresas) + 1))
    
    # Tabela de Equipamentos
    df_merged = pd.merge(df_source, df_empresas, left_on='empresa', right_on='nome_empresa')
    cols_equip = ['cod_ons', 'tensao_kv', 'ponto_de', 'ponto_ate', 'anotacao_geral', 'id_empresa']
    df_equipamentos = df_merged[cols_equip].drop_duplicates(subset=['cod_ons']).reset_index(drop=True)
    df_equipamentos.insert(0, 'id_conexao', range(1, len(df_equipamentos) + 1))
    
    # Tabela de Valores MUST (com a correção do RegEx)
    id_vars = ['cod_ons']
    value_vars = [col for col in df_source.columns if '_valor' in col]
    df_melted = df_source.melt(id_vars=id_vars, value_vars=value_vars, var_name='medicao', value_name='valor')
    df_melted.dropna(subset=['valor'], inplace=True)
    
    pattern = r'(fora_ponta|ponta)_(\d{4})_valor'
    extracted_data = df_melted['medicao'].str.extract(pattern)
    df_melted['periodo'] = extracted_data[0]
    df_melted['ano'] = extracted_data[1]
    df_melted.dropna(subset=['ano', 'periodo'], inplace=True)
    df_melted['ano'] = df_melted['ano'].astype(int)
    
    df_valores_must = pd.merge(df_melted[['cod_ons', 'ano', 'periodo', 'valor']], df_equipamentos[['id_conexao', 'cod_ons']], on='cod_ons')
    df_valores_must = df_valores_must[['id_conexao', 'ano', 'periodo', 'valor']]

    print(f"  -> Normalização concluída: {len(df_empresas)} empresas, {len(df_equipamentos)} equipamentos, {len(df_valores_must)} registros de valores.")
    return df_empresas, df_equipamentos, df_valores_must

# --- 2. Classe Base Abstrata (agora mais simples) ---

class DataBaseController(ABC):
    def __init__(self, db_path: Path, df_empresas, df_equipamentos, df_valores_must):
        self.db_path = db_path
        self.df_empresas = df_empresas
        self.df_equipamentos = df_equipamentos
        self.df_valores_must = df_valores_must
        self.conn = None
        self.cursor = None

    @abstractmethod
    def connect(self): pass
    @abstractmethod
    def close(self): pass
    @abstractmethod
    def _create_tables(self): pass
    @abstractmethod
    def _insert_data(self): pass

    def load_data(self):
        try:
            self.connect()
            self._create_tables()
            self._insert_data()
            print(f"\n✅ Carga de dados para '{self.db_path.name}' concluída com sucesso!")
        except Exception as e:
            print(f"\n❌ ERRO GERAL no processo de carga para {self.db_path.name}: {e}")
        finally:
            self.close()

# --- 3. Implementações Específicas (SQLite e Access) ---

class SQLiteController(DataBaseController):
    def connect(self):
        print("3. Conectando ao banco de dados SQLite...")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def close(self):
        if self.conn: self.conn.close(); print("Conexão SQLite fechada.")
    def _create_tables(self):
        print("4. Criando tabelas (se não existirem)...")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS empresas (id_empresa INTEGER PRIMARY KEY, nome_empresa TEXT NOT NULL UNIQUE)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS anotacao (id_conexao INTEGER PRIMARY KEY, cod_ons TEXT NOT NULL UNIQUE, tensao_kv INTEGER, ponto_de TEXT, ponto_ate TEXT, anotacao_geral TEXT, id_empresa_fk INTEGER, FOREIGN KEY (id_empresa_fk) REFERENCES empresas(id_empresa))")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS valores_must (id_valor INTEGER PRIMARY KEY, id_equipamento_fk INTEGER, ano INTEGER, periodo TEXT, valor REAL, FOREIGN KEY (id_equipamento_fk) REFERENCES equipamentos(id_conexao))")
        self.conn.commit()
    def _insert_data(self):
        print("5. Inserindo dados...")
        self.df_empresas.to_sql('empresas', self.conn, if_exists='replace', index=False)
        self.df_equipamentos.to_sql('anotacao', self.conn, if_exists='replace', index=False)
        self.df_valores_must.to_sql('valores_must', self.conn, if_exists='replace', index=False)
        self.conn.commit()

    def list_tables(self):
        """Lista todas as tabelas no banco de dados SQLite."""
        if not self.conn:
            self.connect()

        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [table[0] for table in self.cursor.fetchall()]

    def select_from_table(self, table_name):

        if not self.conn:
            self.connect()

        self.cursor.execute(f"SELECT * FROM {table_name};")
        columns = [description[0] for description in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]


class AccessController(DataBaseController):
    def connect(self):
        print("3. Conectando ao banco de dados MS Access...")
        if not self.db_path.exists():
            raise FileNotFoundError(f"O arquivo de banco de dados Access não foi encontrado: {self.db_path}.")
        conn_str = (r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};" fr"DBQ={self.db_path};")
        self.conn = pyodbc.connect(conn_str)
        self.cursor = self.conn.cursor()

    def close(self):
        if self.conn: self.conn.close(); print("Conexão Access fechada.")

    def _create_tables(self):
        print("4. Verificando tabelas existentes no Access (não serão recriadas)...")
        # Como as tabelas foram criadas manualmente, este método não precisa fazer nada.
        # No máximo, podemos verificar se elas existem.
        required_tables = ['empresas', 'anotacoes', 'valores_must']
        existing_tables = [table.table_name for table in self.cursor.tables(tableType='TABLE')]
        
        for table in required_tables:
            if table not in existing_tables:
                raise ValueError(f"Tabela '{table}' não encontrada no banco de dados Access! Crie-a manualmente primeiro.")
        
        # É uma boa prática limpar as tabelas antes de inserir novos dados
        print("   -> Limpando tabelas para nova carga...")
        self.cursor.execute("DELETE FROM valores_must")
        self.cursor.execute("DELETE FROM anotacoes")
        self.cursor.execute("DELETE FROM empresas")
        self.conn.commit()

    def _insert_data(self):
        print("5. Inserindo dados no Access...")
        # (A lógica de inserção complexa para o Access, com @@IDENTITY, permanece aqui)
        empresa_id_map = {}
        for index, row in self.df_empresas.iterrows():
            self.cursor.execute("INSERT INTO empresas (nome_empresa) VALUES (?)", row['nome_empresa'])
            self.cursor.execute("SELECT @@IDENTITY")
            empresa_id_map[row['id_empresa']] = self.cursor.fetchone()[0]
        
        self.df_equipamentos['id_empresa_fk_access'] = self.df_equipamentos['id_empresa'].map(empresa_id_map)

        equipamento_id_map = {}
        for index, row in self.df_equipamentos.iterrows():
            cols = ['cod_ons', 'tensao_kv', 'ponto_de', 'ponto_ate', 'anotacao_geral', 'id_empresa_fk_access']
            self.cursor.execute("INSERT INTO equipamentos (cod_ons, tensao_kv, ponto_de, ponto_ate, anotacao_geral, id_empresa_fk) VALUES (?, ?, ?, ?, ?, ?)", *(row[c] for c in cols))
            self.cursor.execute("SELECT @@IDENTITY")
            equipamento_id_map[row['id_equipamento']] = self.cursor.fetchone()[0]
            
        self.df_valores_must['id_equipamento_fk_access'] = self.df_valores_must['id_equipamento'].map(equipamento_id_map)
        
        valores_data = [tuple(row) for row in self.df_valores_must[['id_equipamento_fk_access', 'ano', 'periodo', 'valor']].itertuples(index=False)]
        self.cursor.executemany("INSERT INTO valores_must (id_equipamento_fk, ano, periodo, valor) VALUES (?, ?, ?, ?)", valores_data)
        self.conn.commit()


# --- 5. Exemplo de Execução Refatorado ---

if __name__ == '__main__':
    print("--- INICIANDO TESTE DO DATABASE CONTROLLER (REATORADO) ---")
    
    EXCEL_PATH = Path(r"C:\Users\pedrovictor.veras\OneDrive - Operador Nacional do Sistema Eletrico\Documentos\ESTAGIO_ONS_PVRV_2025\AUTOMACÕES ONS\arquivos\database\must_tables_PDF_notes_merged.xlsx")
    
    DB_OUTPUT_FOLDER = EXCEL_PATH.parent
    SQLITE_DB_PATH = DB_OUTPUT_FOLDER / "database_consolidado.db"
    ACCESS_DB_PATH = DB_OUTPUT_FOLDER / "database_consolidado.accdb"

    if not EXCEL_PATH.exists():
        print(f"ERRO: O arquivo Excel de entrada não foi encontrado em '{EXCEL_PATH}'")
    else:
        df_consolidado = pd.read_excel(EXCEL_PATH)
        
        # 1. Prepara os dados UMA ÚNICA VEZ
        df_empresas, df_equipamentos, df_valores_must = prepare_and_normalize_data(df_consolidado)
        
        # --- Processar para SQLite ---
        print("\n" + "="*50 + "\nPROCESSANDO PARA SQLITE\n" + "="*50)
        sqlite_controller = SQLiteController(SQLITE_DB_PATH, df_empresas, df_equipamentos, df_valores_must)
        
        tabelas = sqlite_controller.list_tables()
        print("\nTabelas no Banco: ", tabelas)

        data_json = sqlite_controller.select_from_table(tabelas[0])
        print(f"\nDados da Tabela {tabelas[0]}:\n{data_json}")
        
        print("\nInserindo os dados das tabelas MUST no banco de dados SQLite...")
        sqlite_controller.load_data()



        
        # --- Processar para MS Access ---
        # Descomente para executar
        try:
            print("\n" + "="*50 + "\nPROCESSANDO PARA MS ACCESS\n" + "="*50)

            access_controller = AccessController(ACCESS_DB_PATH, df_empresas, df_equipamentos, df_valores_must)
            access_controller.load_data()
        except Exception as e:
            print(f"Falha na execução do Access Controller: {e}")
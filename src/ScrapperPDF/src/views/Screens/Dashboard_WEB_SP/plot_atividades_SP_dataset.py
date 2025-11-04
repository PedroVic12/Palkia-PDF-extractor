import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Ler o arquivo Excel
df = pd.read_excel("Controle_PVRV_ONS.xlsx", sheet_name="Planejador AI de Projetos", skiprows=2)

print(f"DataFrame original: {df.shape[0]} linhas x {df.shape[1]} colunas")

# Garantir que as colunas de duração são numéricas (strings -> NaN)
for col in ["DURAÇÃO DO PLANO", "DURAÇÃO REAL"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    else:
        print(f"WARN: coluna esperada '{col}' nao encontrada no DataFrame")

# Filtrar uma fatia que contenha apenas as linhas de atividade
# Aqui assumimos que as linhas de interesse tem a palavra 'Atividade' no campo 'ATIVIDADE'
if "ATIVIDADE" in df.columns:
    mask = df["ATIVIDADE"].astype(str).str.strip().str.startswith("Atividade")
    df_slice = df[mask].copy()
    print(f"Usando fatia com {df_slice.shape[0]} linhas (linhas que comecam com 'Atividade')")
else:
    # fallback: selecionar linhas com valores numericos nas colunas de duracao
    mask = df["DURAÇÃO DO PLANO"].notna() | df["DURAÇÃO REAL"].notna()
    df_slice = df[mask].copy()
    print(f"Usando fallback: fatia com {df_slice.shape[0]} linhas (linhas com duracao)")

# Calcular porcentagem concluida de forma vetorizada, tratando divisao por zero e NaNs
if "DURAÇÃO DO PLANO" in df_slice.columns and "DURAÇÃO REAL" in df_slice.columns:
    plano = df_slice["DURAÇÃO DO PLANO"].fillna(0)
    real = df_slice["DURAÇÃO REAL"].fillna(0)
    concl = np.where(plano == 0, 0, (real / plano) * 100)
    # limitar a 100
    concl = np.minimum(concl, 100)
    df_slice["CONCLUÍDA (%)"] = concl
else:
    df_slice["CONCLUÍDA (%)"] = 0

# Criar status Kanban com base na porcentagem
def status(percent):
    try:
        if percent == 0:
            return "Backlog"
        elif percent < 100:
            return "In Progress"
        else:
            return "Completed"
    except Exception:
        return "Unknown"

df_slice["STATUS"] = df_slice["CONCLUÍDA (%)"].apply(status)

kanban_counts = df_slice["STATUS"].value_counts()
percent_medio = df_slice["CONCLUÍDA (%)"].mean()

print("Resumo Kanban:")
print(kanban_counts)
print(f"\nMédia geral de conclusão (fatia): {percent_medio:.2f}%")


# graficos usando a fatia filtrada
if "ATIVIDADE" in df_slice.columns:
    labels = df_slice["ATIVIDADE"]
else:
    labels = df_slice.index.astype(str)

plt.figure(figsize=(8, max(4, len(df_slice) * 0.25)))
plt.barh(labels, df_slice["CONCLUÍDA (%)"], color="#8a2be2")
plt.xlabel("Progresso (%)")
plt.title("Andamento dos Projetos")
plt.tight_layout()
plt.show()


# Salvar apenas a fatia atualizada
out_file = "Planejador_AI_Projetos_atualizado_fatia.xlsx"
with pd.ExcelWriter(out_file, engine="openpyxl", mode="w") as writer:
    df_slice.to_excel(writer, index=False)

print(f"Arquivo salvo: {out_file}")

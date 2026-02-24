# Automação para corrigir as barras ausentes no SISBAR SECO

Arquivo de referência: "C:\Users\pedrovictor.veras\Downloads\Corrige_Barras_SECO_Fev26.xlsx"

# - Abrir o ultimo excel da pasta Mensal SISBAR Barras ausentes. Ex: Mensal - Jan26.xlsx

# - Pegar e acumular na planilha atual o Nº Barra, Nome, Agente, Área

# - Colocar a nova planilha do mes consequentemente com o nome do mes e o ano autualizado. Ex: Mensal - Fev26.xlsx

# - Pegar pelo ID da barra e nome da barra com PROCV e procurar a resposta do "Parecer da Área" do caso do mês anterior

# - Pegar o parecer da área e verificar nas abas do excel: ["Futuras Ligadas", "Futuras Desligadas", "Desativadas","Ativas Desligadas 01 ", "Ativas Desligadas 02","Ativas Faltantes 01", "Ativas Faltantes 02"]

# - Pegar a resposta de cada Aba na cell A1 de cada aba do excel selecionada

# - Formula para coluna "Questionamento SISBAR": =SEERRO(PROCV([@[Nº Barra]];'Parecer da Área Janeiro 2026'!$A$3:$F$70;5;FALSO); "<texto da cell A1 da aba selecionada>")

# - Formula para coluna "Parecer da Área": =SEERRO(PROCV([@[Nº Barra]];'Parecer da Área Janeiro 2026'!$A$3:$F$70;6;FALSO); " "))

# - Pegar o número da Área da região de cada barra com ID e filtrar as do SECO (Sudeste e Centro Oeste)

# - Formula 1 para coluna "Área": =PROCV([@[Nº Barra]];Parecer!$A$2:$D$70;4;FALSO)

# - Formula 2 para coluna "Área": =ESQUERDA(DIREITA(A1;5);2) -> Onde A1 é a cell do nome da barra

# app.py

# -_- coding: utf-8 -_-

"""
App GUI (PySide6) para automatizar a geração do arquivo "Mensal - <Mês><aa>.xlsx"

Requisitos no ambiente local do usuário:
pip install pandas openpyxl PySide6

Observações importantes:

- O Excel é quem calcula as fórmulas. O openpyxl apenas grava as fórmulas.
- As fórmulas estão em PT-BR (SEERRO, PROCV, FALSO) e usam separador ";" por padrão.
- Referências externas em fórmulas exigem caminho + [arquivo.xlsx]aba!intervalo.
- Para fallback do "Questionamento SISBAR", o app permite escolher uma das abas
  e pegar o texto da célula A1 desta aba; o texto é gravado dentro da fórmula SEERRO.
- Opcionalmente é possível filtrar as barras para SECO antes de gravar (é necessário
  informar o arquivo e a aba que contém o mapeamento Nº Barra -> Área, além de
  quais números de Área pertencem ao SECO).

Classes principais:

- CorrigeBarrasSeco (controller): executa as operações de I/O, fórmulas e geração.
- PlannerMensalWidget (tela): interface PySide6 para o fluxo descrito.
  """

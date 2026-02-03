
"""
03/02/2026
Versão: 1.1.3

# Automação para corrigir as barras ausentes no SISBAR SECO 

Arquivo de referência: "C:\Users\pedrovictor.veras\Downloads\Corrige_Barras_SECO_Fev26.xlsx"

- Abrir o ultimo excel da pasta Mensal SISBAR Barras ausentes. Ex: Mensal - Jan26.xlsx
- Pegar e acumular na planilha atual o id barra, nome, agente, área 
- Colocar a nova planilha do mes consequentemente com o nome do mes e o ano autualizado. Ex: Mensal - Fev26.xlsx

- Pegar pelo ID da barra e nome da barra com PROCV e procurar a resposta do "Parecer da Área" do caso do mês anterior
- Pegar o parecer da área e verificar nas abas do excel: ["Futuras Ligadas", "Futuras Desligadas", "Desativadas","Ativas Desligadas 01 ", "Ativas Desligadas 02","Ativas Faltantes 01", "Ativas Faltantes 02"]
- Pegar a resposta de cada Aba na cell A1 de cada aba do excel selecionada 
- Formula para coluna "Questionamento SISBAR": =SEERRO(PROCV([@[Nº Barra]];'Parecer da Área Janeiro 2026'!$A$3:$F$70;5;FALSO); "<texto da cell A1 da aba selecionada>")
- Formula para coluna "Parecer da Área": =SEERRO(PROCV([@[Nº Barra]];'Parecer da Área Janeiro 2026'!$A$3:$F$70;6;FALSO); " "))
- Pegar o número da Área da região de cada barra com ID e filtrar as do SECO (Sudeste e Centro Oeste)
- Formula para coluna "Área": =PROCV([@[Nº Barra]];Parecer!$A$2:$D$70;4;FALSO)

"""
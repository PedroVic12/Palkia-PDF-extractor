'==============================================================================
' GERADOR DE RELATÓRIOS PERDAS DUPLAS ETL V6 - Versão Final (21/01/2026)
'==============================================================================


' Controle de versão:
' V3: 11/12/2025
' - [x] Configuração de formatação do relatório por variáveis globais   1'2
' - [x] Implementação da função de log
' - [x] Implementação da função de erro
' - [x] Implementação da função de teste rápido
' - [x] Implementação da função de formatação de células horizonte, volume, área, contingência
' V4: 12/01/2026
' - [x] Implementação da função de download do template Word direto do sharepoint
' - [x] Mesma versão do V3, mas com o template Word já baixado na pasta de downloads e usando as funcoes corretas
' V5: 13/01/2026
' - [x] Organizacao do codigo em modulos para facilitar a leitura e manutencao e debug em VBA
' V6: 13/01/2026
' - [x] Implementação da função que pega as informações da aba Modificações do excel
' - [x] Implementação da funcao que coloca a revisão e data correta no relatório
' V6: 14/01/2026
' - [x] Correção da aba modificações e altura das linhas corretamente pelo tamanho do texto. 3 graficos na mesma planilha

' V6: 21/01/2026
' - [x] Formatacao da tabela principal corretamente sem texto negrito e altura das linhas corretamente pelo tamanho do texto
' - [x] Formtação correta da aba Modificações para aparecer corretamente no relatório como Seção do documento (ExcluirAnterior = False)
' - [ ] Teste da função da aba Modificações com parametro True ou False para retirar a antiga e colocar a nova no formato correto


' V6: ultimo Update: 04/02/2026

' V6.1: Testes e correções na aba modificações

Option Explicit

' ======================
' CONFIGURAÇÕES GLOBAIS
' ======================

' --- Configurações do SharePoint ---
Public Const URL_SHAREPOINT_TEMPLATE As String = "https://onsbr.sharepoint.com/sites/soumaisons/OnsIntranetCentralArquivos/PL/19%20Diretrizes%20para%20Opera%C3%A7%C3%A3o/00%20Padroniza%C3%A7%C3%A3o/Lista%20de%20Conting%C3%AAncias%20Duplas%20Analisadas_Modelo.docx"

' --- DADOS VARIÁVEIS (Capa) ---
' Verifique essas váriáveis se estão iguais no Word Template
Public Const TAG_DATA_ANTIGA As String = "DEZEMBRO 2025"
Public Const TEXTO_DATA_NOVO As String = "JANEIRO 2026 - 21/01/2026"

Public Const TAG_REVISAO_ANTIGA As String = "REVISÃO 9"

' --- Configurações Gerais ---
Public Const AJUSTAR_QUEBRA_LINHA As Boolean = True
Public Const REPETIR_CABECALHO As Boolean = True
Public Const DEBUG_MODE As Boolean = False '! Ativado para ver qual linha exata trava
Public Const CABECALHO_AZUL As Boolean = False
Public Const CONVERTER_PDF As Boolean = False

' --- Configurações Visuais ---
Public Const FONTE_CABECALHO As String = "Calibri"
Public Const TAMANHO_CABECALHO As Integer = 16
Public Const FONTE_DADOS As String = "Calibri"
Public Const TAMANHO_DADOS As Integer = 10
Public Const ALTURA_LINHA As Integer = 15
Public Const ESPESSURA_BORDA As Integer = 1

' Cores
Public Const COR_VERDE_CURTO As Long = 25600
Public Const COR_LARANJA_MEDIO As Long = 42495
Public Const COR_AZUL_ONS As Long = 10092543
Public Const COR_TEXTO_BRANCO As Long = 16777215
Public Const COR_TEXTO_PRETO As Long = 0

' Larguras (cm)
Public Const LARGURA_VOLUME As Double = 2.5
Public Const LARGURA_AREA As Double = 8#
Public Const LARGURA_CONTINGENCIA As Double = 12#
Public Const LARGURA_HORIZONTE As Double = 4#
Public Const LARGURA_PADRAO As Double = 5#

' ==============================================================================
' [MÓDULO 1] Função Principal
' ==============================================================================

Sub GerarRelatorioPerdasDuplasETL()
    On Error GoTo ErroHandler
    
    Dim caminhoTemplate As String
    Dim pagina As Long
    Dim txtRevisaoNova As String
    
    Call Log("=== INICIANDO GERAÇÃO DE RELATÓRIO DE PERDAS DUPLAS V6 ===")
    
    ' 1. TEXTO DO NÚMERO DE REVISÃO
    txtRevisaoNova = GerarStringRevisaoDoExcel()
    If txtRevisaoNova = "ERRO" Then
        If MsgBox("Aviso: Revisão não detectada no nome do Excel. Continuar?", vbYesNo + vbExclamation) = vbNo Then Exit Sub
    Else
        Call Log("Revisão detectada: " & txtRevisaoNova)
    End If
    
    ' 2. DOWNLOAD DO WORD NO SHAREPOINT
    Call Log("Baixando template Word do Sharepoint...")
    caminhoTemplate = BaixarTemplateDoSharePoint()
    If caminhoTemplate = "" Then Exit Sub
    
    ' 3. PÁGINA DA TABELA
    Dim respostaPagina As String
    respostaPagina = InputBox("Em qual página deseja inserir a TABELA PRINCIPAL?", "Configuração", "7")
    If respostaPagina = "" Or Not IsNumeric(respostaPagina) Then Exit Sub
    pagina = CLng(respostaPagina)
    If pagina < 1 Then pagina = 1
    
    ' 4. EXECUTAR PARA CRIAR O RELATÓRIO
    Call CriarRelatorioCorrigido(caminhoTemplate, pagina, txtRevisaoNova, CONVERTER_PDF)
    
    Exit Sub
    
ErroHandler:
    Call LogErro(Err.Description, Err.Number)
    MsgBox "? ERRO FATAL: " & Err.Description, vbCritical
End Sub

' ==============================================================================
' [MÓDULO 2] FUNÇÃO CORE (GERA O RELATÓRIO EM WORD)
' ==============================================================================

Sub CriarRelatorioCorrigido(caminhoWord As String, paginaPrincipal As Long, novaRevisao As String, converterPDF As Boolean)
    
    Dim wordApp As Object, wordDoc As Object, tabela As Object
    Dim ws As Worksheet
    Dim ultimaLinha As Long, ultimaColuna As Long
    Dim i As Long, j As Long
    Dim caminhoSalvar As String
    Dim sucesso As Boolean
    
    On Error GoTo ErroHandler
    
    Call Log("Iniciando processamento...")
    
    ' --- A. PREPARAÇÃO DO EXCEL ---
    On Error Resume Next
    Set ws = ThisWorkbook.Worksheets("Contingências Duplas")
    If ws Is Nothing Then Set ws = ThisWorkbook.Worksheets(1)
    On Error GoTo ErroHandler
    
    ultimaLinha = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
    ultimaColuna = ws.Cells(1, ws.Columns.Count).End(xlToLeft).Column
    

    ' ! Rever esta parte
    ' SEGURANÇA: Limite do Word é 63 colunas. Proteção contra colunas fantasmas.
    If ultimaColuna > 63 Then
        Call Log("AVISO: Excel tem " & ultimaColuna & " colunas. Word limita a 63. Ajustando.")
        ultimaColuna = 63
    End If
    
    Call Log("Dimensões Validadas: " & ultimaLinha & " Linhas x " & ultimaColuna & " Colunas")
    
    If ultimaLinha < 2 Then MsgBox "Planilha vazia!", vbExclamation: Exit Sub
    
    ' --- B. SALVAR COMO ---
    caminhoSalvar = Application.GetSaveAsFilename(InitialFileName:="Relatorio_Perdas_" & Format(Now, "ddmm_hhmm") & ".docx", FileFilter:="Word (*.docx), *.docx")
    If caminhoSalvar = "False" Then Exit Sub
    
    ' --- C. ABRIR WORD ---
    Application.StatusBar = "Abrindo Word..."
    Set wordApp = CreateObject("Word.Application")
    wordApp.Visible = True
    Set wordDoc = wordApp.Documents.Open(caminhoWord)
    
    ' --- D. CAPA E MODIFICAÇÕES ---
    Call Log("Atualizando Capa...")
    Call SubstituirTextoNoWord(wordDoc, TAG_DATA_ANTIGA, TEXTO_DATA_NOVO)
    If novaRevisao <> "ERRO" Then Call SubstituirTextoNoWord(wordDoc, TAG_REVISAO_ANTIGA, novaRevisao)
    
    ' TODO 21/01 AQUI
    Call Log("Inserindo Informações na Aba de Modificações...")
    'Call InserirTabelaModificacoes(wordDoc, wordApp)
    Call InserirAbaModificacoesComoLista(wordDoc, wordApp, False)
    
    ' --- F. INSERIR TABELA PRINCIPAL (NAVEGAÇÃO SEGURA) ---
    Call Log("Navegando para página " & paginaPrincipal)
    
    wordDoc.Repaginate ' Força atualização da paginação
    
    Dim totalPaginas As Long
    On Error Resume Next
    totalPaginas = wordDoc.ComputeStatistics(2) ' wdStatisticPages
    If Err.Number <> 0 Then totalPaginas = 1
    On Error GoTo ErroHandler
    
    If paginaPrincipal > totalPaginas Then
        wordApp.Selection.EndKey Unit:=6
    Else
        On Error Resume Next
        wordApp.Selection.GoTo What:=1, Which:=1, Count:=paginaPrincipal
        If Err.Number <> 0 Then wordApp.Selection.EndKey Unit:=6
        On Error GoTo ErroHandler
    End If
    
    ' Adicionar título e data do relatório para DEBUG
    If DEBUG_MODE Then
        Call Log("Adicionando título e data do relatório para DEBUG...")
        wordApp.Selection.TypeText "RELATÓRIO DE PERDAS DUPLAS" & vbCrLf
        wordApp.Selection.TypeText "Gerado em: " & Format(Now, "dd/mm/yyyy HH:MM") & vbCrLf & vbCrLf
    End If

    ' --- CRIAR TABELA ---
    Call Log("Criando Tabela (" & ultimaLinha & "x" & ultimaColuna & ")...")
    Set tabela = wordDoc.Tables.Add(wordApp.Selection.Range, ultimaLinha, ultimaColuna)
    
    ' --- G. FORMATAÇÃO E PREENCHIMENTO (LOOP SEGURO) ---
    ' O erro acontecia aqui pois tentava iterar mais colunas/linhas do que existiam na tabela criada
    
    Dim maxLinhasTbl As Long, maxColsTbl As Long
    maxLinhasTbl = tabela.Rows.Count
    maxColsTbl = tabela.Columns.Count
    
    ' G1. Formatação Larguras
    Call Log("Formatando Larguras...")
    For j = 1 To maxColsTbl
        Dim cabecalho As String, larguraCm As Double
        
        ' Pega cabeçalho do Excel com segurança
        If j <= ultimaColuna Then
            cabecalho = LCase(Trim(ws.Cells(1, j).Value))
        Else
            cabecalho = ""
        End If
        
        larguraCm = LARGURA_PADRAO
        If InStr(cabecalho, "volume") > 0 Then larguraCm = LARGURA_VOLUME
        If InStr(cabecalho, "área") > 0 Or InStr(cabecalho, "area") > 0 Then larguraCm = LARGURA_AREA
        If InStr(cabecalho, "contingencia") > 0 Or InStr(cabecalho, "contingência") > 0 Then larguraCm = LARGURA_CONTINGENCIA
        If InStr(cabecalho, "horizonte") > 0 Then larguraCm = LARGURA_HORIZONTE
        
        tabela.Columns(j).Width = larguraCm * 28.35
    Next j
    
    ' G2. Bordas
    tabela.Borders.InsideLineStyle = 1: tabela.Borders.OutsideLineStyle = 1
    
    ' G3. Preenchimento Dados (Loop Seguro: Usa limites da tabela criada)
    Application.StatusBar = "Preenchendo tabela..."
    Call Log("Iniciando preenchimento...")
    
    For i = 1 To maxLinhasTbl
        ' Altura
        tabela.Rows(i).HeightRule = IIf(AJUSTAR_QUEBRA_LINHA, 1, 2)
        tabela.Rows(i).Height = ALTURA_LINHA
        
        For j = 1 To maxColsTbl
            ' Verifica se estamos dentro dos limites do Excel antes de ler
            Dim txt As String
            If i <= ultimaLinha And j <= ultimaColuna Then
                txt = Trim(ws.Cells(i, j).Text)
                If txt = "" Then txt = "-"
            Else
                txt = "-"
            End If
            
            tabela.Cell(i, j).Range.Text = txt
            
            ' Formatação
            If i = 1 Then
                tabela.Cell(i, j).Range.Bold = True
                tabela.Cell(i, j).Range.ParagraphFormat.Alignment = 1
                If CABECALHO_AZUL Then tabela.Cell(i, j).Range.Shading.BackgroundPatternColor = COR_AZUL_ONS
            Else
                tabela.Cell(i, j).Range.ParagraphFormat.Alignment = 0
                tabela.Cell(i, j).Range.Font.Size = TAMANHO_DADOS
                
                ' Cor Horizonte (com segurança)
                If j <= ultimaColuna Then
                    If InStr(LCase(ws.Cells(1, j).Text), "horizonte") > 0 Then
                        Call FormatarCelulaHorizonte(tabela.Cell(i, j), txt)
                    End If
                End If
            End If
        Next j
        If i Mod 10 = 0 Then DoEvents
    Next i
    
    If REPETIR_CABECALHO Then tabela.Rows(1).HeadingFormat = True
    
    ' --- H. FINALIZAR ---
    wordDoc.SaveAs2 caminhoSalvar
    If converterPDF Then wordDoc.SaveAs2 Left(caminhoSalvar, InStrRev(caminhoSalvar, ".")) & "pdf", 17
    
    Call Log("Relatório gerado com sucesso!")
    
    sucesso = True
    MsgBox "? Relatório Word gerado com sucesso!", vbInformation
    
Limpeza:
    On Error Resume Next
    If Not wordDoc Is Nothing Then If Not sucesso Then wordDoc.Close False
    If Not wordApp Is Nothing Then If Not sucesso Then wordApp.Quit
    Set wordDoc = Nothing: Set wordApp = Nothing
    Application.StatusBar = False
    Exit Sub

ErroHandler:
    sucesso = False
    Call LogErro(Err.Description, Err.Number)
    MsgBox "? ERRO: " & Err.Description, vbCritical
    Resume Limpeza
End Sub

' ==============================================================================
' [MÓDULO 3] FUNÇÕES AUXILIARES
' ==============================================================================

Function BaixarTemplateDoSharePoint() As String
    Dim wordApp As Object, wordDoc As Object
    Dim caminhoLocal As String, nomeArquivo As String
    On Error GoTo ErroDownload
    
    nomeArquivo = "Relatorio_perdas_duplas_template_" & Format(Date, "dd_mm_yy") & ".docx"
    caminhoLocal = Environ("USERPROFILE") & "\Downloads\" & nomeArquivo
    If Dir(caminhoLocal) <> "" Then Kill caminhoLocal
    
    Set wordApp = CreateObject("Word.Application")
    wordApp.Visible = False
    Set wordDoc = wordApp.Documents.Open(Filename:=Replace(URL_SHAREPOINT_TEMPLATE, "?web=1", ""), ReadOnly:=True, Visible:=False)
    wordDoc.SaveAs2 Filename:=caminhoLocal, FileFormat:=16
    wordDoc.Close False: wordApp.Quit
    BaixarTemplateDoSharePoint = caminhoLocal
    Set wordDoc = Nothing: Set wordApp = Nothing
    Exit Function
ErroDownload:
    Call LogErro("Download Falhou: " & Err.Description)
    MsgBox "Erro no Download.", vbCritical: If Not wordApp Is Nothing Then wordApp.Quit
    BaixarTemplateDoSharePoint = ""
End Function

Function GerarStringRevisaoDoExcel() As String
    Dim nome As String, pos As Integer, i As Integer, num As String
    nome = ThisWorkbook.Name
    pos = InStr(1, nome, "Rev", vbTextCompare)
    If pos = 0 Then GerarStringRevisaoDoExcel = "ERRO": Exit Function
    Dim resto As String: resto = Mid(nome, pos + 3)
    For i = 1 To Len(resto)
        If IsNumeric(Mid(resto, i, 1)) Then num = num & Mid(resto, i, 1) Else Exit For
    Next i
    If num <> "" Then GerarStringRevisaoDoExcel = "REVISÃO " & num Else GerarStringRevisaoDoExcel = "ERRO"
End Function

Sub SubstituirTextoNoWord(doc As Object, antigo As String, novo As String)
    Dim rng As Object: Set rng = doc.Content
    With rng.Find: .ClearFormatting: .Text = antigo: .Replacement.Text = novo: .Forward = True: .Wrap = 1: .Execute Replace:=2: End With
End Sub


Sub InserirTabelaModificacoes(doc As Object, app As Object)
    Dim ws As Worksheet, tbl As Object
    Dim ultL As Long, ultC As Long, i As Long, j As Long
    On Error Resume Next: Set ws = ThisWorkbook.Worksheets("Modificações"): On Error GoTo 0
    If ws Is Nothing Then Exit Sub
    
    ultL = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
    ultC = ws.Cells(1, ws.Columns.Count).End(xlToLeft).Column
    If ultL < 1 Then ultL = 1
    If ultC < 1 Then ultC = 1
    
    app.Selection.HomeKey Unit:=6
    With app.Selection.Find: .Text = "Revisões do relatório": .Execute: End With
    If app.Selection.Find.Found Then
        app.Selection.MoveDown Unit:=5, Count:=1: app.Selection.TypeParagraph
    Else
        app.Selection.EndKey Unit:=6: app.Selection.TypeText vbCrLf & "HISTÓRICO DE MODIFICAÇÕES" & vbCrLf
    End If
    
    Set tbl = doc.Tables.Add(app.Selection.Range, ultL, ultC)
    tbl.Borders.InsideLineStyle = 1: tbl.Borders.OutsideLineStyle = 1
    tbl.Rows(1).Range.Font.Bold = True: tbl.Rows(1).Range.Shading.BackgroundPatternColor = 14277081
    
    For i = 1 To ultL
        For j = 1 To ultC: tbl.Cell(i, j).Range.Text = ws.Cells(i, j).Text: Next j
    Next i
    app.Selection.EndKey Unit:=6
End Sub

' ======================
' FUNÇÃO DA ABA MODIFICAÇÕES - PROCURA A SEÇÃO DE REVISÕES DO RELATÓRIO E INSERE A ABA MODIFICAÇÕES EM LISTA
' ======================
' ======================
' FUNÇÃO - ADICIONA APÓS A TABELA EXISTENTE
' ======================
Sub InserirAbaModificacoesComoLista(doc As Object, app As Object, Optional excluirAnterior As Boolean = False)
    Dim ws As Worksheet
    Dim ultL As Long, i As Long
    Dim textoItem As String
    Dim contador As Long
    
    ' OBTER DADOS
    Set ws = ThisWorkbook.Worksheets("Modificações")
    If ws Is Nothing Then Exit Sub
    
    ultL = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
    If ultL < 2 Then Exit Sub
    
    ' IR PARA O INÍCIO
    app.Selection.HomeKey Unit:=6
    
    ' PROCURAR "REVISÕES DO RELATÓRIO"
    With app.Selection.Find
        .ClearFormatting
        .Text = "Revisões do relatório"
        .Forward = True
        .Wrap = 0
        If Not .Execute Then
            ' Não encontrou - criar no final
            app.Selection.EndKey Unit:=6
            app.Selection.TypeText vbCrLf & vbCrLf & "Revisões do relatório" & vbCrLf & vbCrLf
        End If
    End With
    
    ' AGORA ESTAMOS NO "REVISÕES DO RELATÓRIO"
    ' PRECISAMOS IR PARA O FINAL DA TABELA EXISTENTE
    
    ' Mover para baixo 7 vezes (título + linha da tabela com "2")
    ' Isso nos coloca APÓS a última linha da tabela
    For i = 1 To 7
        app.Selection.MoveDown Unit:=5, Count:=1
    Next i
    
    ' SE EXCLUIRANTERIOR = TRUE, APAGAR TUDO DAQUI EM DIANTE
    If excluirAnterior Then
        Dim inicio As Long
        inicio = app.Selection.Start
        doc.Range(inicio, doc.Content.End).Delete
        app.Selection.Start = inicio
    End If
    
    ' ADICIONAR SEPARADOR (sempre)
    app.Selection.TypeText vbCrLf & "---" & vbCrLf & vbCrLf
    
    ' INSERIR ITENS (começando do 1)
    contador = 1
    For i = 2 To ultL
        textoItem = Trim(ws.Cells(i, 1).Value)
        If textoItem <> "" Then
            app.Selection.TypeText contador & ". " & textoItem & vbCrLf
            contador = contador + 1
        End If
    Next i
    
    ' ADICIONAR SEPARADOR FINAL E DATA
    app.Selection.TypeText vbCrLf & "---" & vbCrLf
    app.Selection.TypeText "Atualizado em: " & Format(Date, "dd/mm/yyyy") & vbCrLf
    
    MsgBox "Dados inseridos após a tabela existente!", vbInformation
End Sub

' ======================
' FUNÇÃO AUXILIAR PARA CONTAR ITENS EXISTENTES
' ======================
Function ContarItensLista(textoLista As String) As Long
    ' Conta quantos itens já existem na lista (linhas que começam com número e ponto)
    
    Dim linhas() As String
    Dim i As Long, contador As Long
    Dim linha As String
    Dim partes() As String
    
    If Len(Trim(textoLista)) = 0 Then
        ContarItensLista = 0
        Exit Function
    End If
    
    linhas = Split(textoLista, vbCrLf)
    contador = 0
    
    For i = 0 To UBound(linhas)
        linha = Trim(linhas(i))
        
        ' Ignorar linhas vazias ou separadores
        If linha <> "" And linha <> "---" Then
            ' Verificar se linha começa com número seguido de ponto e espaço
            If Len(linha) > 2 Then
                partes = Split(linha, ".")
                If UBound(partes) >= 1 Then
                    If IsNumeric(Trim(partes(0))) Then
                        contador = contador + 1
                    End If
                End If
            End If
        End If
    Next i
    
    ContarItensLista = contador
End Function


' ======================
' FUNÇÃO PARA FORMATAR CÉLULA HORIZONTE
' ======================
Private Sub FormatarCelulaHorizonte(celula As Object, valor As String)
    On Error Resume Next: Dim h As String: h = LCase(Trim(valor))
    celula.Range.ParagraphFormat.Alignment = 1: celula.Range.Bold = True
    If h = "curto prazo" Then celula.Range.Font.Color = COR_VERDE_CURTO
    If InStr(h, "médio") > 0 Or InStr(h, "medio") > 0 Then celula.Range.Font.Color = COR_LARANJA_MEDIO
End Sub


' ======================
' FUNÇÃO PARA LOG
' ======================

Private Sub Log(msg As String)
    Debug.Print "[" & Format(Now, "hh:mm:ss") & "] " & msg
    If DEBUG_MODE Then MsgBox msg, vbInformation, "DEBUG"
End Sub

Private Sub LogErro(erroDesc As String, Optional erroNum As Long = 0)
    Log "ERRO " & erroNum & ": " & erroDesc
End Sub



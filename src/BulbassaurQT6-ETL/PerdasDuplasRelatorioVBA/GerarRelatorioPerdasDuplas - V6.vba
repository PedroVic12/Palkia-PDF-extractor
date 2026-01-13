'==============================================================================
' GERADOR DE RELATÓRIOS PERDAS DUPLAS - V9 (ESTÁVEL + ENTREGA)
'==============================================================================
Option Explicit

' ==============================================================================
' [SEÇÃO 1] CONFIGURAÇÕES
' ==============================================================================

' --- Configurações do SharePoint ---
Public Const URL_SHAREPOINT_TEMPLATE As String = "https://onsbr.sharepoint.com/sites/soumaisons/OnsIntranetCentralArquivos/PL/19%20Diretrizes%20para%20Opera%C3%A7%C3%A3o/00%20Padroniza%C3%A7%C3%A3o/Lista%20de%20Conting%C3%AAncias%20Duplas%20Analisadas_Modelo.docx"

' --- DADOS VARIÁVEIS (O que será substituído na CAPA) ---
' Data:
Public Const TAG_DATA_ANTIGA As String = "DEZEMBRO 2025"
Public Const TEXTO_DATA_NOVO As String = "JANEIRO 2026"

' Revisão:
Public Const TAG_REVISAO_ANTIGA As String = "REVISÃO 9"
' A nova revisão será calculada automaticamente do nome do arquivo Excel.

' --- Configurações Gerais ---
Public Const AJUSTAR_QUEBRA_LINHA As Boolean = True
Public Const REPETIR_CABECALHO As Boolean = True
Public Const DEBUG_MODE As Boolean = False
Public Const CABECALHO_AZUL As Boolean = False

' --- Configurações Visuais ---
Public Const FONTE_CABECALHO As String = "Calibri"
Public Const TAMANHO_CABECALHO As Integer = 14
Public Const FONTE_DADOS As String = "Calibri"
Public Const TAMANHO_DADOS As Integer = 10
Public Const ALTURA_LINHA As Integer = 20
Public Const ESPESSURA_BORDA As Integer = 1

' Cores
Public Const COR_VERDE_CURTO As Long = 25600
Public Const COR_LARANJA_MEDIO As Long = 42495
Public Const COR_AZUL_ONS As Long = 10092543
Public Const COR_TEXTO_BRANCO As Long = 16777215
Public Const COR_TEXTO_PRETO As Long = 0

' Larguras (cm)
Public Const LARGURA_VOLUME As Double = 2.5
Public Const LARGURA_AREA As Double = 8.0
Public Const LARGURA_CONTINGENCIA As Double = 12.0
Public Const LARGURA_HORIZONTE As Double = 4.0
Public Const LARGURA_PADRAO As Double = 5.0

' ==============================================================================
' [SEÇÃO 2] ORQUESTRADOR PRINCIPAL
' ==============================================================================

Sub Main_GerarRelatorio()
    On Error GoTo ErroGeral
    
    Dim caminhoTemplate As String
    Dim paginaDestino As Long
    Dim respostaPagina As String
    Dim txtRevisaoNova As String
    
    ' 1. Calcular a Nova Revisão (do nome do arquivo Excel)
    txtRevisaoNova = GerarStringRevisaoDoExcel()
    If txtRevisaoNova = "ERRO" Then
        If MsgBox("Não foi possível identificar a revisão no nome do arquivo Excel (ex: _Rev10.xlsm)." & vbCrLf & _
               "O sistema não substituirá a revisão na capa. Continuar?", vbYesNo + vbExclamation) = vbNo Then Exit Sub
    End If
    
    ' 2. Baixar Template
    caminhoTemplate = BaixarTemplateDoSharePoint()
    If caminhoTemplate = "" Then Exit Sub
    
    ' 3. Input do Usuário
    respostaPagina = InputBox("Em qual página do Word deseja inserir a tabela PRINCIPAL?", "Configuração", "4")
    If Not IsNumeric(respostaPagina) Then Exit Sub
    paginaDestino = CLng(respostaPagina)
    
    ' 4. Processar Relatório
    Call ProcessarRelatorioWord(caminhoTemplate, paginaDestino, txtRevisaoNova)
    
    Exit Sub

ErroGeral:
    MsgBox "Erro fatal: " & Err.Description, vbCritical
End Sub

' ==============================================================================
' [SEÇÃO 3] PROCESSAMENTO (Lógica Estável V3)
' ==============================================================================

Sub ProcessarRelatorioWord(caminhoTemplate As String, paginaPrincipal As Long, novaRevisao As String)
    Dim wordApp As Object, wordDoc As Object, tabela As Object
    Dim wsPrincipal As Worksheet
    Dim ultLin As Long, ultCol As Long, i As Long, j As Long
    Dim caminhoSalvar As String
    
    On Error GoTo ErroProcessamento
    
    ' --- 1. Preparação Excel ---
    Set wsPrincipal = ThisWorkbook.Worksheets("Contingências Duplas")
    ultLin = wsPrincipal.Cells(wsPrincipal.Rows.Count, "A").End(xlUp).Row
    ultCol = wsPrincipal.Cells(1, wsPrincipal.Columns.Count).End(xlToLeft).Column
    
    caminhoSalvar = Application.GetSaveAsFilename(InitialFileName:="Relatorio_Final.docx", FileFilter:="Word (*.docx), *.docx")
    If caminhoSalvar = "False" Then Exit Sub
    
    Application.StatusBar = "Abrindo Word..."
    Set wordApp = CreateObject("Word.Application")
    wordApp.Visible = True
    Set wordDoc = wordApp.Documents.Open(caminhoTemplate)
    
    ' --- 2. Atualizar Capa (Find & Replace) ---
    Call Log("Atualizando Capa...")
    Call SubstituirTextoNoWord(wordDoc, TAG_DATA_ANTIGA, TEXTO_DATA_NOVO)
    
    If novaRevisao <> "ERRO" Then
        Call SubstituirTextoNoWord(wordDoc, TAG_REVISAO_ANTIGA, novaRevisao)
    End If
    
    ' --- 3. Inserir Modificações (Pág 3) ---
    Call Log("Inserindo Modificações...")
    Call InserirTabelaModificacoes(wordDoc, wordApp)
    
    ' --- 4. Inserir Tabela Principal ---
    Call Log("Configurando Tabela Principal...")
    
    ' Navegar para a página correta
    If paginaPrincipal > wordDoc.ComputeStatistics(2) Then
        wordApp.Selection.EndKey Unit:=6
    Else
        wordApp.Selection.GoTo What:=1, Which:=1, Count:=paginaPrincipal
    End If
    
    wordApp.Selection.TypeText "RELATÓRIO DE PERDAS DUPLAS" & vbCrLf
    wordApp.Selection.TypeText "Gerado em: " & Format(Now, "dd/mm/yyyy HH:MM") & vbCrLf & vbCrLf
    
    ' CRIAR TABELA
    Set tabela = wordDoc.Tables.Add(wordApp.Selection.Range, ultLin, ultCol)
    
    ' A. Configurar Larguras (Loop separado para clareza)
    For j = 1 To ultCol
        Dim cabecalho As String, larguraCm As Double
        cabecalho = LCase(Trim(wsPrincipal.Cells(1, j).Value))
        
        larguraCm = LARGURA_PADRAO
        If InStr(cabecalho, "volume") > 0 Then larguraCm = LARGURA_VOLUME
        If InStr(cabecalho, "area") > 0 Or InStr(cabecalho, "área") > 0 Then larguraCm = LARGURA_AREA
        If InStr(cabecalho, "contingencia") > 0 Or InStr(cabecalho, "contingência") > 0 Then larguraCm = LARGURA_CONTINGENCIA
        If InStr(cabecalho, "horizonte") > 0 Then larguraCm = LARGURA_HORIZONTE
        
        tabela.Columns(j).Width = larguraCm * 28.35
    Next j
    
    ' B. Configurar Alturas e Bordas
    With tabela.Borders
        .InsideLineStyle = 1: .OutsideLineStyle = 1
        .InsideLineWidth = ESPESSURA_BORDA: .OutsideLineWidth = ESPESSURA_BORDA
    End With
    
    For i = 1 To ultLin
        tabela.Rows(i).HeightRule = IIf(AJUSTAR_QUEBRA_LINHA, 1, 2) ' 1=Auto/Min, 2=Exato
        tabela.Rows(i).Height = ALTURA_LINHA
    Next i
    
    If REPETIR_CABECALHO Then tabela.Rows(1).HeadingFormat = True
    
    ' --- 5. Preenchimento (LÓGICA V3 ESTÁVEL - SEPARADA) ---
    
    ' Passo 5.1: Apenas Cabeçalho (Linha 1)
    Application.StatusBar = "Preenchendo Cabeçalho..."
    For j = 1 To ultCol
        tabela.Cell(1, j).Range.Text = Trim(wsPrincipal.Cells(1, j).Value)
        
        With tabela.Cell(1, j).Range
            .Bold = True
            .Font.Name = FONTE_CABECALHO
            .Font.Size = TAMANHO_CABECALHO
            .ParagraphFormat.Alignment = 1 ' Centro
            If CABECALHO_AZUL Then
                .Font.Color = COR_TEXTO_BRANCO
                .Shading.BackgroundPatternColor = COR_AZUL_ONS
            Else
                .Font.Color = COR_TEXTO_PRETO
            End If
        End With
    Next j
    
    ' Passo 5.2: Dados (Linha 2 até Fim)
    Application.StatusBar = "Preenchendo Dados..."
    For i = 2 To ultLin
        For j = 1 To ultCol
            Dim texto As String
            texto = Trim(wsPrincipal.Cells(i, j).Text)
            If texto = "" Then texto = "-"
            
            tabela.Cell(i, j).Range.Text = texto
            
            ' Formatação
            With tabela.Cell(i, j).Range
                .Font.Name = FONTE_DADOS
                .Font.Size = TAMANHO_DADOS
                .ParagraphFormat.Alignment = 0 ' Esquerda
            End With
            
            ' Formatação Condicional
            If InStr(LCase(wsPrincipal.Cells(1, j).Text), "horizonte") > 0 Then
                AplicarCorHorizonte tabela.Cell(i, j), texto
            End If
        Next j
        If i Mod 20 = 0 Then DoEvents
    Next i
    
    ' --- 6. Finalizar ---
    wordDoc.SaveAs2 caminhoSalvar
    MsgBox "Relatório gerado com sucesso!", vbInformation
    Application.StatusBar = False
    Exit Sub

ErroProcessamento:
    Application.StatusBar = False
    MsgBox "Erro no processamento (Linha " & Erl & "): " & Err.Description, vbCritical
    If Not wordDoc Is Nothing Then wordDoc.Close False
    If Not wordApp Is Nothing Then wordApp.Quit
End Sub

' ==============================================================================
' [SEÇÃO 4] FUNÇÕES AUXILIARES
' ==============================================================================

Function BaixarTemplateDoSharePoint() As String
    Dim wordApp As Object, wordDoc As Object
    Dim caminhoLocal As String, nomeArquivo As String
    Dim dataHoje As String
    On Error GoTo ErroDownload
    
    dataHoje = Format(Date, "yy_mm_dd")
    nomeArquivo = "word_template_" & dataHoje & ".docx"
    caminhoLocal = Environ("USERPROFILE") & "\Downloads\" & nomeArquivo
    If Dir(caminhoLocal) <> "" Then Kill caminhoLocal
    
    Set wordApp = CreateObject("Word.Application")
    wordApp.Visible = False
    Set wordDoc = wordApp.Documents.Open(FileName:=Replace(URL_SHAREPOINT_TEMPLATE, "?web=1", ""), ReadOnly:=True, Visible:=False)
    wordDoc.SaveAs2 FileName:=caminhoLocal, FileFormat:=16
    wordDoc.Close False: wordApp.Quit
    
    BaixarTemplateDoSharePoint = caminhoLocal
    Set wordDoc = Nothing: Set wordApp = Nothing
    Exit Function
ErroDownload:
    MsgBox "Erro download: " & Err.Description, vbCritical
    If Not wordApp Is Nothing Then wordApp.Quit
    BaixarTemplateDoSharePoint = ""
End Function

Function GerarStringRevisaoDoExcel() As String
    ' Extrai numero depois de "Rev" no nome do arquivo Excel atual
    Dim nome As String, pos As Integer, i As Integer, num As String
    nome = ThisWorkbook.Name
    pos = InStr(1, nome, "Rev", vbTextCompare)
    If pos = 0 Then GerarStringRevisaoDoExcel = "ERRO": Exit Function
    
    Dim resto As String
    resto = Mid(nome, pos + 3) ' Pega tudo depois de Rev
    For i = 1 To Len(resto)
        If IsNumeric(Mid(resto, i, 1)) Then num = num & Mid(resto, i, 1) Else Exit For
    Next i
    If num <> "" Then GerarStringRevisaoDoExcel = "REVISÃO " & num Else GerarStringRevisaoDoExcel = "ERRO"
End Function

Sub SubstituirTextoNoWord(doc As Object, antigo As String, novo As String)
    Dim rng As Object
    Set rng = doc.Content
    With rng.Find
        .ClearFormatting: .Text = antigo: .Replacement.Text = novo
        .Forward = True: .Wrap = 1: .Execute Replace:=2
    End With
End Sub

Sub InserirTabelaModificacoes(doc As Object, app As Object)
    Dim ws As Worksheet, tbl As Object
    Dim ultL As Long, ultC As Long, i As Long, j As Long
    On Error Resume Next
    Set ws = ThisWorkbook.Worksheets("Modificações")
    On Error GoTo 0
    If ws Is Nothing Then Exit Sub
    
    ultL = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
    ultC = ws.Cells(1, ws.Columns.Count).End(xlToLeft).Column
    
    app.Selection.HomeKey Unit:=6
    With app.Selection.Find: .Text = "Revisões do relatório": .Execute: End With
    If app.Selection.Find.Found Then
        app.Selection.MoveDown Unit:=5, Count:=1: app.Selection.TypeParagraph
    Else
        app.Selection.EndKey Unit:=6: app.Selection.TypeText vbCrLf & "HISTÓRICO DE MODIFICAÇÕES" & vbCrLf
    End If
    
    Set tbl = doc.Tables.Add(app.Selection.Range, ultL, ultC)
    tbl.Borders.InsideLineStyle = 1: tbl.Borders.OutsideLineStyle = 1
    tbl.Rows(1).Range.Font.Bold = True
    tbl.Rows(1).Range.Shading.BackgroundPatternColor = 14277081
    
    For i = 1 To ultL
        For j = 1 To ultC: tbl.Cell(i, j).Range.Text = ws.Cells(i, j).Text: Next j
    Next i
    app.Selection.EndKey Unit:=6
End Sub

Sub AplicarCorHorizonte(celula As Object, valor As String)
    valor = LCase(Trim(valor))
    celula.Range.Bold = True: celula.Range.ParagraphFormat.Alignment = 1
    If valor = "curto prazo" Then celula.Range.Font.Color = COR_VERDE_CURTO
    If InStr(valor, "médio") > 0 Or InStr(valor, "medio") > 0 Then celula.Range.Font.Color = COR_LARANJA_MEDIO
End Sub

Sub Log(msg As String)
    Debug.Print "[" & Format(Now, "hh:mm:ss") & "] " & msg
End Sub
'==============================================================================
' GERADOR DE RELATÓRIOS PERDAS DUPLAS - V5 (FORMATO CLÁSSICO + AUTO HEIGHT + Aba Modificações)
'==============================================================================
Option Explicit

' ==============================================================================
' [SEÇÃO 1] CONFIGURAÇÕES (O "config.py" do VBA)
' ==============================================================================

' --- Configurações do SharePoint ---
Public Const URL_SHAREPOINT_TEMPLATE As String = "https://onsbr.sharepoint.com/sites/soumaisons/OnsIntranetCentralArquivos/PL/19%20Diretrizes%20para%20Opera%C3%A7%C3%A3o/00%20Padroniza%C3%A7%C3%A3o/Lista%20de%20Conting%C3%AAncias%20Duplas%20Analisadas_Modelo.docx"

' --- DADOS VARIÁVEIS (Atualize mensalmente aqui) ---
Public Const TAG_DATA As String = "[DATA_MES]"
Public Const TEXTO_DATA_NOVO As String = "JANEIRO 2026"

Public Const TAG_REVISAO As String = "[NUM_REV]"
Public Const TEXTO_REVISAO_NOVO As String = "REVISÃO 10"

' --- Configurações de Comportamento ---
Public Const CABECALHO_AZUL As Boolean = False
Public Const DEBUG_MODE As Boolean = False
Public Const CONVERTER_PDF As Boolean = False
Public Const REPETIR_CABECALHO As Boolean = True

' --- [NOVA] Configuração de Quebra de Linha ---
' True: A linha cresce se o texto for grande (Quebra de linha)
' False: A linha tem altura fixa e corta o texto
Public Const AJUSTAR_QUEBRA_LINHA As Boolean = True

' --- Configurações Visuais e Dimensões ---
Public Const FONTE_CABECALHO As String = "Calibri"
Public Const TAMANHO_CABECALHO As Integer = 14
Public Const FONTE_DADOS As String = "Calibri"
Public Const TAMANHO_DADOS As Integer = 10

' Cores
Public Const COR_VERDE_CURTO As Long = 25600
Public Const COR_LARANJA_MEDIO As Long = 42495
Public Const COR_AZUL_ONS As Long = 10092543
Public Const COR_TEXTO_BRANCO As Long = 16777215
Public Const COR_TEXTO_PRETO As Long = 0

' Tabela
Public Const ALTURA_LINHA As Integer = 20      ' Altura mínima
Public Const ESPESSURA_BORDA As Integer = 1

' Larguras (cm)
Public Const LARGURA_VOLUME As Double = 2.5
Public Const LARGURA_AREA As Double = 8.0
Public Const LARGURA_CONTINGENCIA As Double = 12.0
Public Const LARGURA_HORIZONTE As Double = 4.0
Public Const LARGURA_PADRAO As Double = 5.0

' ==============================================================================
' [SEÇÃO 2] ORQUESTRADOR
' ==============================================================================

Sub Main_GerarRelatorio()
    On Error GoTo ErroGeral
    
    Dim caminhoTemplate As String
    Dim paginaDestino As Long
    Dim respostaPagina As String
    
    Call Log("=== INICIANDO PROCESSO V6 ===")
    
    ' 1. Baixar Template
    caminhoTemplate = BaixarTemplateDoSharePoint()
    If caminhoTemplate = "" Then Exit Sub
    
    ' 2. Input do Usuário
    respostaPagina = InputBox("Em qual página do Word deseja inserir a tabela PRINCIPAL?", "Configuração", "4")
    If Not IsNumeric(respostaPagina) Then Exit Sub
    paginaDestino = CLng(respostaPagina)
    
    ' 3. Processar Relatório
    Call ProcessarRelatorioWord(caminhoTemplate, paginaDestino)
    
    Exit Sub

ErroGeral:
    MsgBox "Erro fatal no orquestrador: " & Err.Description, vbCritical
End Sub

' ==============================================================================
' [SEÇÃO 3] FUNÇÕES DE TRABALHO
' ==============================================================================

Function BaixarTemplateDoSharePoint() As String
    Dim wordApp As Object, wordDoc As Object
    Dim caminhoLocal As String, nomeArquivo As String
    Dim dataHoje As String
    
    On Error GoTo ErroDownload
    
    Call Log("Iniciando download...")
    dataHoje = Format(Date, "yy_mm_dd")
    nomeArquivo = "word_template_" & dataHoje & ".docx"
    caminhoLocal = Environ("USERPROFILE") & "\Downloads\" & nomeArquivo
    
    If Dir(caminhoLocal) <> "" Then Kill caminhoLocal
    
    Set wordApp = CreateObject("Word.Application")
    wordApp.Visible = False
    
    Dim urlFinal As String
    urlFinal = Replace(URL_SHAREPOINT_TEMPLATE, "?web=1", "")
    
    Set wordDoc = wordApp.Documents.Open(FileName:=urlFinal, ReadOnly:=True, Visible:=False)
    wordDoc.SaveAs2 FileName:=caminhoLocal, FileFormat:=16
    wordDoc.Close SaveChanges:=False
    wordApp.Quit
    
    BaixarTemplateDoSharePoint = caminhoLocal
    
    Set wordDoc = Nothing
    Set wordApp = Nothing
    Exit Function

ErroDownload:
    Call Log("ERRO DOWNLOAD: " & Err.Description)
    MsgBox "Erro ao baixar template. Verifique login.", vbCritical
    If Not wordApp Is Nothing Then wordApp.Quit
    BaixarTemplateDoSharePoint = ""
End Function


Sub ProcessarRelatorioWord(caminhoTemplate As String, paginaPrincipal As Long)
    Dim wordApp As Object, wordDoc As Object, tabela As Object
    Dim wsPrincipal As Worksheet
    Dim ultLin As Long, ultCol As Long, i As Long, j As Long
    Dim caminhoSalvar As String
    
    On Error GoTo ErroProcessamento
    
    ' --- 1. Preparação ---
    Set wsPrincipal = ThisWorkbook.Worksheets("Contingências Duplas")
    ultLin = wsPrincipal.Cells(wsPrincipal.Rows.Count, "A").End(xlUp).Row
    ultCol = wsPrincipal.Cells(1, wsPrincipal.Columns.Count).End(xlToLeft).Column
    
    caminhoSalvar = Application.GetSaveAsFilename(InitialFileName:="Relatorio_Final.docx", FileFilter:="Word (*.docx), *.docx")
    If caminhoSalvar = "False" Then Exit Sub
    
    Application.StatusBar = "Abrindo Word..."
    Set wordApp = CreateObject("Word.Application")
    wordApp.Visible = True
    Set wordDoc = wordApp.Documents.Open(caminhoTemplate)
    
    ' --- 2. Atualizar Capa e Rodapés ---
    Call Log("Atualizando Tags...")
    Call SubstituirTextoNoWord(wordDoc, TAG_DATA, TEXTO_DATA_NOVO)
    Call SubstituirTextoNoWord(wordDoc, TAG_REVISAO, TEXTO_REVISAO_NOVO)
    
    ' --- 3. Inserir Tabela de Modificações ---
    Call Log("Inserindo Modificações na pág 3...")
    Call InserirTabelaModificacoes(wordDoc, wordApp)
    
    ' --- 4. Inserir Tabela Principal ---
    Call Log("Inserindo Tabela Principal na pág " & paginaPrincipal & "...")
    
    ' Ir para página específica
    wordApp.Selection.GoTo What:=1, Which:=1, Count:=paginaPrincipal
    wordApp.Selection.TypeText "RELATÓRIO DE PERDAS DUPLAS" & vbCrLf
    wordApp.Selection.TypeText "Gerado em: " & Format(Now, "dd/mm/yyyy HH:MM") & vbCrLf & vbCrLf
    
    ' Cria Tabela
    Set tabela = wordDoc.Tables.Add(wordApp.Selection.Range, ultLin, ultCol)
    
    ' ==========================================================================
    ' BLOCO DE FORMATAÇÃO DETALHADA (Restaurado do seu código original)
    ' ==========================================================================
    
    ' A. Largura das Colunas
    For j = 1 To ultCol
        Dim cabecalho As String
        Dim larguraCm As Double
        cabecalho = LCase(Trim(wsPrincipal.Cells(1, j).Value))
        
        If InStr(cabecalho, "volume") > 0 Then
            larguraCm = LARGURA_VOLUME
        ElseIf InStr(cabecalho, "área") > 0 Or InStr(cabecalho, "area") > 0 Then
            larguraCm = LARGURA_AREA
        ElseIf InStr(cabecalho, "contingência") > 0 Or InStr(cabecalho, "contingencia") > 0 Then
            larguraCm = LARGURA_CONTINGENCIA
        ElseIf InStr(cabecalho, "horizonte") > 0 Then
            larguraCm = LARGURA_HORIZONTE
        Else
            larguraCm = LARGURA_PADRAO
        End If
        
        tabela.Columns(j).Width = larguraCm * 28.35 ' Conversão cm -> points
    Next j
    
    ' B. Bordas
    With tabela.Borders
        .InsideLineStyle = 1
        .OutsideLineStyle = 1
        .InsideLineWidth = ESPESSURA_BORDA
        .OutsideLineWidth = ESPESSURA_BORDA
    End With
    
    ' C. Altura das Linhas (AQUI ESTÁ O TRUQUE DO AUTO-FIT)
    For i = 1 To ultLin
        If AJUSTAR_QUEBRA_LINHA Then
            ' wdRowHeightAtLeast = 1: A linha tem MINIMO de 20, mas cresce se precisar
            tabela.Rows(i).HeightRule = 1
            tabela.Rows(i).Height = ALTURA_LINHA
        Else
            ' wdRowHeightExactly = 2: A linha tem EXATAMENTE 20 (corta texto)
            tabela.Rows(i).HeightRule = 2
            tabela.Rows(i).Height = ALTURA_LINHA
        End If
    Next i
    
    If REPETIR_CABECALHO Then tabela.Rows(1).HeadingFormat = True
    
    ' D. Preenchimento de Dados e Cabeçalho
    For i = 1 To ultLin
        For j = 1 To ultCol
            Dim texto As String
            texto = Trim(wsPrincipal.Cells(i, j).Text)
            If texto = "" Then texto = "-"
            
            tabela.Cell(i, j).Range.Text = texto
            
            ' Formatação Específica para Cabeçalho (Linha 1)
            If i = 1 Then
                 With tabela.Cell(i, j).Range
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
            Else
                ' Formatação de Dados (Linha > 1)
                 With tabela.Cell(i, j).Range
                    .Font.Name = FONTE_DADOS
                    .Font.Size = TAMANHO_DADOS
                    .ParagraphFormat.Alignment = 0 ' Esquerda
                End With
                
                ' Formatação Condicional (Horizonte)
                If InStr(LCase(wsPrincipal.Cells(1, j).Text), "horizonte") > 0 Then
                    AplicarCorHorizonte tabela.Cell(i, j), texto
                End If
            End If
        Next j
        
        If i Mod 10 = 0 Then DoEvents ' Evita travar tela
    Next i
    
    ' --- 5. Finalizar ---
    wordDoc.SaveAs2 caminhoSalvar
    MsgBox "Relatório gerado com sucesso!", vbInformation
    Application.StatusBar = False
    Exit Sub

ErroProcessamento:
    Application.StatusBar = False
    MsgBox "Erro: " & Err.Description, vbCritical
    If Not wordDoc Is Nothing Then wordDoc.Close False
    If Not wordApp Is Nothing Then wordApp.Quit
End Sub

' ==============================================================================
' [SEÇÃO 4] FUNÇÕES AUXILIARES
' ==============================================================================

Sub SubstituirTextoNoWord(doc As Object, textoAntigo As String, textoNovo As String)
    Dim myRange As Object
    Set myRange = doc.Content
    With myRange.Find
        .ClearFormatting
        .Replacement.ClearFormatting
        .Text = textoAntigo
        .Replacement.Text = textoNovo
        .Forward = True
        .Wrap = 1
        .Execute Replace:=2
    End With
End Sub

Sub InserirTabelaModificacoes(doc As Object, app As Object)
    Dim wsMod As Worksheet
    Dim ultLinMod As Long, ultColMod As Long
    Dim tblMod As Object
    Dim i As Long, j As Long
    
    On Error Resume Next
    Set wsMod = ThisWorkbook.Worksheets("Modificações")
    On Error GoTo 0
    
    If wsMod Is Nothing Then
        Call Log("Aviso: Aba 'Modificações' não encontrada.")
        Exit Sub
    End If
    
    ultLinMod = wsMod.Cells(wsMod.Rows.Count, "A").End(xlUp).Row
    ultColMod = wsMod.Cells(1, wsMod.Columns.Count).End(xlToLeft).Column
    
    app.Selection.GoTo What:=1, Which:=1, Count:=3
    app.Selection.TypeText "HISTÓRICO DE MODIFICAÇÕES" & vbCrLf
    
    Set tblMod = doc.Tables.Add(app.Selection.Range, ultLinMod, ultColMod)
    
    With tblMod
        .Borders.InsideLineStyle = 1
        .Borders.OutsideLineStyle = 1
        .Rows(1).Range.Font.Bold = True
        .Rows(1).Range.Shading.BackgroundPatternColor = 14277081
    End With
    
    For i = 1 To ultLinMod
        For j = 1 To ultColMod
            tblMod.Cell(i, j).Range.Text = wsMod.Cells(i, j).Text
        Next j
    Next i
    
    app.Selection.EndKey Unit:=6
End Sub

Sub AplicarCorHorizonte(celula As Object, valor As String)
    valor = LCase(Trim(valor))
    celula.Range.Bold = True
    celula.Range.ParagraphFormat.Alignment = 1
    If valor = "curto prazo" Then
        celula.Range.Font.Color = COR_VERDE_CURTO
    ElseIf InStr(valor, "médio") > 0 Or InStr(valor, "medio") > 0 Then
        celula.Range.Font.Color = COR_LARANJA_MEDIO
    End If
End Sub

Sub Log(msg As String)
    Debug.Print "[" & Format(Now, "hh:mm:ss") & "] " & msg
    If DEBUG_MODE Then MsgBox msg
End Sub
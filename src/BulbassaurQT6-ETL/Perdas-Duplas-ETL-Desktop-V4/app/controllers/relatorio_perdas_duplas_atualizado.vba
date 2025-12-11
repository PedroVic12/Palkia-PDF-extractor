'============================================
' GERADOR DE RELATÓRIOS PERDAS DUPLAS - VERSÃO FINAL COM AJUSTES
'============================================
Option Explicit

' ======================
' SUB PRINCIPAL - BOTÃO
' ======================
Sub GerarRelatorioPerdasDuplasETL()
    On Error GoTo ErroHandler
    
    Dim templateWord As String
    Dim pagina As Long
    Dim incluirTeste As Boolean
    Dim converterPDF As Boolean
    
    ' 1. ESCOLHER ARQUIVO WORD
    templateWord = Application.GetOpenFilename( _
        FileFilter:="Arquivos Word (*.docx; *.doc), *.docx; *.doc", _
        Title:="Selecione o Template Word")
    
    If templateWord = "False" Then Exit Sub
    
    ' 2. PERGUNTAR NÚMERO DA PÁGINA
    Dim respostaPagina As String
    respostaPagina = InputBox("Em qual página deseja inserir a tabela?" & vbCrLf & _
                            "Digite um número (ex: 1, 2, 3...):", _
                            "Número da Página", "1")
    
    If respostaPagina = "" Then Exit Sub
    
    If Not IsNumeric(respostaPagina) Then
        MsgBox "Por favor, digite um número válido!", vbExclamation
        Exit Sub
    End If
    
    pagina = CLng(respostaPagina)
    
    ' 3. PERGUNTAR SE INCLUI TABELA DE TESTE
    If MsgBox("Deseja incluir tabela de teste de formatação?", _
              vbYesNo + vbQuestion, "Tabela de Teste") = vbYes Then
        incluirTeste = True
    Else
        incluirTeste = False
    End If
    
    ' 4. PERGUNTAR SE CONVERTE PARA PDF
    If MsgBox("Deseja converter para PDF após gerar?", _
              vbYesNo + vbQuestion, "Converter para PDF") = vbYes Then
        converterPDF = True
    Else
        converterPDF = False
    End If
    
    ' 5. EXECUTAR FUNÇÃO PRINCIPAL
    Call CriarRelatorioComAjustes(templateWord, pagina, incluirTeste, converterPDF)
    
    Exit Sub
    
ErroHandler:
    MsgBox "❌ ERRO: " & Err.Description, vbCritical, "Erro no Processamento"
End Sub

' ======================
' FUNÇÃO PRINCIPAL COM AJUSTES
' ======================
Sub CriarRelatorioComAjustes(caminhoWord As String, pagina As Long, _
                            incluirTeste As Boolean, converterPDF As Boolean)
    
    ' Declaração de variáveis
    Dim wordApp As Object, wordDoc As Object
    Dim tabela As Object
    Dim ws As Worksheet
    Dim ultimaLinha As Long, ultimaColuna As Long
    Dim i As Long, j As Long
    Dim caminhoSalvar As String
    Dim sucesso As Boolean
    
    On Error GoTo ErroHandler
    
    ' ========== VALIDAÇÃO INICIAL ==========
    If Dir(caminhoWord) = "" Then
        MsgBox "Arquivo Word não encontrado!", vbExclamation
        Exit Sub
    End If
    
    ' ========== OBTER DADOS DA ABA ESPECÍFICA ==========
    On Error Resume Next
    Set ws = ThisWorkbook.Worksheets("Contingências Duplas")
    If ws Is Nothing Then
        Set ws = ThisWorkbook.Worksheets(1)
        MsgBox "Aba 'Contingências Duplas' não encontrada. Usando primeira aba.", vbExclamation
    End If
    On Error GoTo ErroHandler
    
    ultimaLinha = ws.Cells(ws.Rows.Count, 1).End(xlUp).Row
    ultimaColuna = ws.Cells(1, ws.Columns.Count).End(xlToLeft).Column
    
    If ultimaLinha < 2 Then
        MsgBox "Não há dados na planilha!", vbExclamation
        Exit Sub
    End If
    
    ' ========== PERGUNTAR ONDE SALVAR ==========
    caminhoSalvar = Application.GetSaveAsFilename( _
        InitialFileName:="Relatorio_Perdas_Duplas_" & Format(Now, "ddmmyyyy_hhmm") & ".docx", _
        FileFilter:="Documentos Word (*.docx), *.docx")
    
    If caminhoSalvar = "False" Then Exit Sub
    
    ' Garantir extensão .docx
    If LCase(Right(caminhoSalvar, 5)) <> ".docx" Then
        caminhoSalvar = caminhoSalvar & ".docx"
    End If
    
    ' ========== INICIAR WORD ==========
    Application.StatusBar = "Abrindo Microsoft Word..."
    Set wordApp = CreateObject("Word.Application")
    wordApp.Visible = True ' Deixar visível para acompanhar
    
    ' Abrir template
    Set wordDoc = wordApp.Documents.Open(caminhoWord)
    
    ' ========== NAVEGAR PARA PÁGINA ESPECÍFICA ==========
    Application.StatusBar = "Navegando para página " & pagina & "..."
    
    ' Tentar ir para a página especificada
    On Error Resume Next
    wordApp.Selection.GoTo What:=1, Which:=2, Name:=pagina ' wdGoToPage
    
    ' Se falhou ou a página não existe, adicionar páginas
    If Err.Number <> 0 Then
        On Error GoTo ErroHandler
        
        ' Vai para o final do documento
        wordApp.Selection.EndKey Unit:=6
        
        ' Adiciona páginas até chegar na página desejada
        Dim paginasAtuais As Long
        paginasAtuais = wordDoc.ComputeStatistics(2) ' wdStatisticPages
        
        If pagina > paginasAtuais Then
            For i = paginasAtuais To pagina - 1
                wordApp.Selection.InsertBreak 7 ' wdPageBreak
            Next i
        End If
    Else
        On Error GoTo ErroHandler
    End If
    
    ' ========== INSERIR DADOS PRINCIPAIS ==========
    Application.StatusBar = "Criando tabela principal..."
    
    ' Adicionar título
    wordApp.Selection.TypeText "RELATÓRIO DE PERDAS DUPLAS" & vbCrLf
    wordApp.Selection.TypeText "Gerado em: " & Format(Now, "dd/mm/yyyy HH:MM") & vbCrLf & vbCrLf
    
    ' Criar tabela principal
    ' Verificar se há seleção ativa
    If wordApp.Selection.Range Is Nothing Then
        wordApp.Selection.EndKey Unit:=6
    End If
    
    ' Criar tabela
    On Error Resume Next
    Set tabela = wordDoc.Tables.Add(wordApp.Selection.Range, ultimaLinha, ultimaColuna)
    If Err.Number <> 0 Then
        MsgBox "Erro ao criar tabela: " & Err.Description, vbCritical
        GoTo Limpeza
    End If
    On Error GoTo ErroHandler
    
    ' ========== CONFIGURAR LARGURAS DAS COLUNAS ==========
    Application.StatusBar = "Configurando larguras das colunas..."
    
    ' Aplicar larguras (converter cm para pontos: 1 cm = 28.35 pontos)
    For j = 1 To ultimaColuna
        Dim cabecalho As String
        cabecalho = LCase(Trim(ws.Cells(1, j).Value))
        Dim larguraCm As Double
        
        ' Definir larguras específicas
        If InStr(cabecalho, "volume") > 0 Then
            larguraCm = 2.0 ' 2.0 cm
        ElseIf InStr(cabecalho, "área") > 0 Or InStr(cabecalho, "area") > 0 Then
            larguraCm = 8.0 ' 8.0 cm
        ElseIf InStr(cabecalho, "contingência") > 0 Or InStr(cabecalho, "contingencia") > 0 Then
            larguraCm = 12.0 ' 12.0 cm
        ElseIf InStr(cabecalho, "horizonte") > 0 Then
            larguraCm = 3.0 ' 3.0 cm
        Else
            larguraCm = 4.0 ' Largura padrão
        End If
        
        ' Aplicar largura
        On Error Resume Next
        tabela.Columns(j).Width = larguraCm * 28.35
        On Error GoTo 0
    Next j
    
    ' ========== CONFIGURAR FORMATAÇÃO DA TABELA ==========
    Application.StatusBar = "Configurando formatação da tabela..."
    
    ' 1. BORDAS LEVES (1px)
    ' Configurar bordas finas
    On Error Resume Next
    With tabela.Borders
        .InsideLineStyle = 1  ' wdLineStyleSingle (borda contínua)
        .OutsideLineStyle = 1
        .InsideLineWidth = 1  ' wdLineWidth025pt (muito fino)
        .OutsideLineWidth = 1
    End With
    
    ' 2. AJUSTAR ALTURA DAS LINHAS
    ' Configurar altura automática para todas as linhas
    For i = 1 To ultimaLinha
        tabela.Rows(i).HeightRule = 0  ' wdRowHeightAuto
        ' Altura mínima de 15 pontos (aproximadamente 0.5 cm)
        tabela.Rows(i).Height = 15
    Next i
    
    ' 3. PRIMEIRA LINHA COMO CABEÇALHO REPETIDO
    ' Configurar para repetir cabeçalho em cada página
    tabela.Rows(1).HeadingFormat = True
    
    ' ========== PREENCHER CABEÇALHO ==========
    Application.StatusBar = "Preenchendo cabeçalho..."
    
    For j = 1 To ultimaColuna
        Dim cabecalhoTexto As String
        cabecalhoTexto = Trim(ws.Cells(1, j).Value)
        
        tabela.Cell(1, j).Range.Text = cabecalhoTexto
        
        ' Formatar cabeçalho
        On Error Resume Next
        With tabela.Cell(1, j).Range
            .Bold = True
            .Font.Color = RGB(255, 255, 255)  ' Texto branco
            .Shading.BackgroundPatternColor = RGB(68, 114, 196)  ' Fundo azul ONS
            .ParagraphFormat.Alignment = 1  ' Centralizado
            .Font.Size = 10
            .Font.Name = "Calibri"
        End With
        On Error GoTo 0
    Next j
    
    ' ========== PREENCHER DADOS ==========
    Application.StatusBar = "Preenchendo dados..."
    
    For i = 2 To ultimaLinha
        For j = 1 To ultimaColuna
            Dim valorCelula As String
            valorCelula = Trim(ws.Cells(i, j).Text)
            
            If valorCelula = "" Then
                valorCelula = "-"
            End If
            
            tabela.Cell(i, j).Range.Text = valorCelula
            
            ' Configurar formatação básica para células de dados
            With tabela.Cell(i, j).Range
                .Font.Name = "Calibri"
                .Font.Size = 9
                .ParagraphFormat.Alignment = 0  ' Alinhar à esquerda
            End With
            
            ' Aplicar formatação condicional para a coluna Horizonte
            Dim cabecalhoColuna As String
            cabecalhoColuna = LCase(Trim(ws.Cells(1, j).Value))
            
            If InStr(cabecalhoColuna, "horizonte") > 0 Then
                Call FormatarHorizonte(tabela.Cell(i, j), valorCelula)
            End If
        Next j
        
        ' Atualizar progresso a cada 10 linhas
        If i Mod 10 = 0 Then
            Application.StatusBar = "Processando linha " & i & " de " & ultimaLinha
            DoEvents
        End If
    Next i
    
    ' ========== APLICAR FORMATAÇÃO GERAL ==========
    Application.StatusBar = "Aplicando formatação final..."
    
    ' Configurar fonte geral
    With tabela.Range
        .Font.Name = "Calibri"
        .Font.Size = 9
    End With
    
    ' Centralizar verticalmente
    tabela.Rows.VerticalAlignment = 1  ' wdCellAlignVerticalCenter
    
    ' ========== SALVAR ==========
    Application.StatusBar = "Salvando documento..."
    
    On Error Resume Next
    wordDoc.SaveAs2 caminhoSalvar
    If Err.Number <> 0 Then
        MsgBox "Erro ao salvar: " & Err.Description, vbCritical
        GoTo Limpeza
    End If
    On Error GoTo 0
    
    ' ========== CONVERTER PARA PDF ==========
    If converterPDF Then
        Application.StatusBar = "Convertendo para PDF..."
        
        Dim pdfPath As String
        pdfPath = Left(caminhoSalvar, InStrRev(caminhoSalvar, ".")) & "pdf"
        
        On Error Resume Next
        wordDoc.SaveAs2 pdfPath, 17  ' wdFormatPDF
        If Err.Number = 0 Then
            MsgBox "✅ PDF gerado com sucesso!" & vbCrLf & _
                   "Local: " & pdfPath, vbInformation
        Else
            MsgBox "⚠️ Não foi possível converter para PDF automaticamente." & vbCrLf & _
                   "Arquivo Word salvo em: " & caminhoSalvar, vbExclamation
        End If
        On Error GoTo 0
    End If
    
    ' ========== FINALIZAÇÃO ==========
    sucesso = True
    
    Application.StatusBar = False
    
    MsgBox "✅ Relatório gerado com sucesso!" & vbCrLf & _
           "Arquivo: " & caminhoSalvar, vbInformation, "Concluído"
    
Limpeza:
    ' ========== LIMPEZA DE OBJETOS ==========
    On Error Resume Next
    
    If Not tabela Is Nothing Then Set tabela = Nothing
    If Not wordDoc Is Nothing Then
        If Not sucesso Then wordDoc.Close SaveChanges:=False
        Set wordDoc = Nothing
    End If
    If Not wordApp Is Nothing Then
        If Not sucesso Then wordApp.Quit
        Set wordApp = Nothing
    End If
    
    Exit Sub
    
ErroHandler:
    Application.StatusBar = False
    
    Dim erroMsg As String
    erroMsg = "❌ ERRO AO GERAR RELATÓRIO:" & vbCrLf & vbCrLf
    erroMsg = erroMsg & "Descrição: " & Err.Description & vbCrLf
    erroMsg = erroMsg & "Número: " & Err.Number
    
    MsgBox erroMsg, vbCritical, "Erro"
    
    Resume Limpeza
End Sub

' ======================
' FUNÇÃO PARA FORMATAR HORIZONTE
' ======================
Private Sub FormatarHorizonte(celula As Object, valor As String)
    On Error Resume Next
    
    Dim horizonte As String
    horizonte = LCase(Trim(valor))
    
    ' Centralizar texto na célula
    celula.Range.ParagraphFormat.Alignment = 1  ' Centralizado
    
    ' Aplicar cores condicionais
    Select Case horizonte
        Case "curto prazo"
            celula.Range.Font.Color = RGB(0, 100, 0)  ' Verde escuro
            celula.Range.Bold = True
            
        Case "médio prazo", "medio prazo"
            celula.Range.Font.Color = RGB(255, 140, 0)  ' Laranja
            celula.Range.Bold = True
            
        Case "longo prazo"
            celula.Range.Font.Color = RGB(178, 34, 34)  ' Vermelho tijolo
            celula.Range.Bold = True
            
        Case Else
            ' Sem formatação especial
    End Select
End Sub

' ======================
' FUNÇÃO PARA VERIFICAR DADOS
' ======================
Sub VerificarDadosAntes()
    ' Verifica os dados antes de gerar o relatório
    
    Dim ws As Worksheet
    On Error Resume Next
    Set ws = ThisWorkbook.Worksheets("Contingências Duplas")
    If ws Is Nothing Then
        Set ws = ThisWorkbook.Worksheets(1)
    End If
    On Error GoTo 0
    
    Dim ultimaLinha As Long, ultimaColuna As Long
    ultimaLinha = ws.Cells(ws.Rows.Count, 1).End(xlUp).Row
    ultimaColuna = ws.Cells(1, ws.Columns.Count).End(xlToLeft).Column
    
    Dim msg As String
    msg = "DADOS PARA EXPORTAÇÃO:" & vbCrLf & vbCrLf
    msg = msg & "Planilha: " & ws.Name & vbCrLf
    msg = msg & "Linhas totais: " & ultimaLinha & vbCrLf
    msg = msg & "Colunas: " & ultimaColuna & vbCrLf & vbCrLf
    
    msg = msg & "CABEÇALHOS:" & vbCrLf
    Dim j As Long
    For j = 1 To ultimaColuna
        msg = msg & j & ". " & ws.Cells(1, j).Value & vbCrLf
    Next j
    
    msg = msg & vbCrLf & "PRIMEIRAS 3 LINHAS:" & vbCrLf
    Dim i As Long
    For i = 2 To Application.Min(4, ultimaLinha)
        For j = 1 To ultimaColuna
            msg = msg & ws.Cells(i, j).Text & " | "
        Next j
        msg = msg & vbCrLf
    Next i
    
    MsgBox msg, vbInformation, "Verificação de Dados"
End Sub

' ======================
' FUNÇÃO PARA AJUSTAR LARGURAS MANUALMENTE
' ======================
Sub AjustarLargurasManualmente()
    ' Permite ajustar as larguras das colunas manualmente
    
    Dim ws As Worksheet
    On Error Resume Next
    Set ws = ThisWorkbook.Worksheets("Contingências Duplas")
    If ws Is Nothing Then
        Set ws = ThisWorkbook.Worksheets(1)
    End If
    On Error GoTo 0
    
    Dim ultimaColuna As Long
    ultimaColuna = ws.Cells(1, ws.Columns.Count).End(xlToLeft).Column
    
    Dim msg As String
    msg = "AJUSTE DE LARGURAS DAS COLUNAS (em cm):" & vbCrLf & vbCrLf
    
    For j = 1 To ultimaColuna
        Dim cabecalho As String
        cabecalho = Trim(ws.Cells(1, j).Value)
        Dim larguraAtual As Double
        
        ' Determinar largura atual baseada no cabeçalho
        Select Case LCase(cabecalho)
            Case "volume"
                larguraAtual = 2.0
            Case "área geoelétrica", "area geoeletrica"
                larguraAtual = 8.0
            Case "contingência dupla", "contingencia dupla"
                larguraAtual = 12.0
            Case "horizonte"
                larguraAtual = 3.0
            Case Else
                larguraAtual = 4.0
        End Select
        
        msg = msg & "Coluna " & j & " (" & cabecalho & "): " & larguraAtual & " cm" & vbCrLf
        msg = msg & "   (Aprox. " & larguraAtual * 28.35 & " pontos)" & vbCrLf
    Next j
    
    msg = msg & vbCrLf & "Total aproximado: " & (2.0 + 8.0 + 12.0 + 3.0) & " cm de largura"
    
    MsgBox msg, vbInformation, "Configuração de Larguras"
End Sub
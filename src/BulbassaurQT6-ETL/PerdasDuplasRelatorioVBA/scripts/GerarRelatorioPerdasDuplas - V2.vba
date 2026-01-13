'============================================
' GERADOR DE RELATÓRIOS PERDAS DUPLAS - VERSÃO 2 - 16/12/2025
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
    incluirTeste = (MsgBox("Deseja incluir tabela de teste de formatação?", _
                           vbYesNo + vbQuestion, "Tabela de Teste") = vbYes)
    
    ' 4. PERGUNTAR SE CONVERTE PARA PDF
    converterPDF = (MsgBox("Deseja converter para PDF após gerar?", _
                          vbYesNo + vbQuestion, "Converter para PDF") = vbYes)
    
    ' 5. EXECUTAR FUNÇÃO PRINCIPAL
    Call CriarRelatorioCorrigido(templateWord, pagina, incluirTeste, converterPDF)
    
    Exit Sub
    
ErroHandler:
    MsgBox "? ERRO: " & Err.Description, vbCritical, "Erro no Processamento"
End Sub

' ======================
' FUNÇÃO PRINCIPAL CORRIGIDA
' ======================
Sub CriarRelatorioCorrigido(caminhoWord As String, pagina As Long, _
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
    
    ' ========== OBTER DADOS DO EXCEL ==========
    On Error Resume Next
    Set ws = ThisWorkbook.Worksheets("Contingências Duplas")
    If ws Is Nothing Then
        Set ws = ThisWorkbook.Worksheets(1)
        MsgBox "Aba 'Contingências Duplas' não encontrada. Usando primeira aba: " & ws.Name, vbExclamation
    End If
    On Error GoTo ErroHandler
    
    ' VERIFICAÇÃO CRÍTICA: Mostrar informações da planilha
    ultimaLinha = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
    ultimaColuna = ws.Cells(1, ws.Columns.Count).End(xlToLeft).Column
    
    MsgBox "DEBUG INFO:" & vbCrLf & _
           "Planilha: " & ws.Name & vbCrLf & _
           "Última linha: " & ultimaLinha & vbCrLf & _
           "Última coluna: " & ultimaColuna, vbInformation, "Verificação"
    
    If ultimaLinha < 2 Then
        MsgBox "Não há dados na planilha! Apenas cabeçalho encontrado.", vbExclamation
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
    wordApp.Visible = True ' IMPORTANTE: Deixar visível para debug
    
    ' Abrir template
    Set wordDoc = wordApp.Documents.Open(caminhoWord)
    
    ' ========== INSERIR DADOS PRINCIPAIS ==========
    Application.StatusBar = "Criando tabela principal..."
    
    ' Ir para o final do documento para inserir a tabela
    wordApp.Selection.EndKey Unit:=6 ' wdStory
    
    ' Adicionar título
    wordApp.Selection.TypeText "RELATÓRIO DE PERDAS DUPLAS" & vbCrLf
    wordApp.Selection.TypeText "Gerado em: " & Format(Now, "dd/mm/yyyy HH:MM") & vbCrLf & vbCrLf
    
    ' Criar tabela principal (DEBUG: Mostrar dimensões)
    MsgBox "Criando tabela com:" & vbCrLf & _
           "Linhas: " & ultimaLinha & vbCrLf & _
           "Colunas: " & ultimaColuna, vbInformation, "Criando Tabela"
    
    ' ? CHECKPOINT 1: Criar tabela
    Set tabela = wordDoc.Tables.Add(wordApp.Selection.Range, ultimaLinha, ultimaColuna)
    
    ' ========== CONFIGURAR LARGURAS DAS COLUNAS ==========
    Application.StatusBar = "Configurando larguras das colunas..."
    
    ' ? CHECKPOINT 2: Configurar larguras
    For j = 1 To ultimaColuna
        Dim cabecalho As String
        cabecalho = LCase(Trim(ws.Cells(1, j).Value))
        Dim larguraCm As Double
        
        ' Definir larguras específicas
        If InStr(cabecalho, "volume") > 0 Then
            larguraCm = 2.5 ' cm
        ElseIf InStr(cabecalho, "área") > 0 Or InStr(cabecalho, "area") > 0 Then
            larguraCm = 8#  ' cm
        ElseIf InStr(cabecalho, "contingência") > 0 Or InStr(cabecalho, "contingencia") > 0 Then
            larguraCm = 12#  ' cm
        ElseIf InStr(cabecalho, "horizonte") > 0 Then
            larguraCm = 4#  ' cm
        Else
            larguraCm = 5#  ' Largura padrão
        End If
        
        ' Aplicar largura (1 cm = 28.35 pontos)
        tabela.Columns(j).Width = larguraCm * 28.35
    Next j
    
    ' ========== CONFIGURAR FORMATAÇÃO DA TABELA ==========
    Application.StatusBar = "Configurando formatação da tabela..."
    
    ' ? CHECKPOINT 3: Bordas leves (1px)
    On Error Resume Next
    With tabela.Borders
        .InsideLineStyle = 1  ' wdLineStyleSingle
        .OutsideLineStyle = 1
        .InsideLineWidth = 1  ' wdLineWidth025pt
        .OutsideLineWidth = 1
    End With
    
    ' ? CHECKPOINT 4: Altura das linhas ajustada
    For i = 1 To ultimaLinha
        tabela.Rows(i).HeightRule = 0  ' wdRowHeightAuto
        tabela.Rows(i).Height = 20 ' 20 pontos de altura mínima
    Next i
    
    ' ? CHECKPOINT 5: Cabeçalho que se repete
    tabela.Rows(1).HeadingFormat = True
    
    ' ========== PREENCHER CABEÇALHO ==========
    Application.StatusBar = "Preenchendo cabeçalho..."
    
    ' ? CHECKPOINT 6: Preencher e formatar cabeçalho
    For j = 1 To ultimaColuna
        Dim cabecalhoTexto As String
        cabecalhoTexto = Trim(ws.Cells(1, j).Value)
        
        ' DEBUG: Mostrar cabeçalho sendo preenchido
        Debug.Print "Preenchendo cabeçalho coluna " & j & ": " & cabecalhoTexto
        
        tabela.Cell(1, j).Range.Text = cabecalhoTexto
        
        ' ? CHECKPOINT 7: Formatação ONS (azul no cabeçalho)
        With tabela.Cell(1, j).Range
            .Bold = True
            .Font.Color = RGB(255, 255, 255)  ' Texto branco
            .Shading.BackgroundPatternColor = RGB(68, 114, 196)  ' Azul ONS
            .ParagraphFormat.Alignment = 1  ' Centralizado
            .Font.Size = 10
            .Font.Name = "Calibri"
        End With
    Next j
    
    ' ========== PREENCHER DADOS ==========
    Application.StatusBar = "Preenchendo dados..."
    
    ' ? CHECKPOINT 8: Preencher dados das células
    For i = 2 To ultimaLinha
        For j = 1 To ultimaColuna
            Dim valorCelula As String
            valorCelula = Trim(ws.Cells(i, j).Text)
            
            If valorCelula = "" Then
                valorCelula = "-"
            End If
            
            ' DEBUG: Mostrar dados sendo preenchidos
            If i <= 3 Then ' Apenas mostrar as primeiras linhas
                Debug.Print "Linha " & i & ", Coluna " & j & ": " & valorCelula
            End If
            
            tabela.Cell(i, j).Range.Text = valorCelula
            
            ' Formatação básica das células
            With tabela.Cell(i, j).Range
                .Font.Name = "Calibri"
                .Font.Size = 9
                .ParagraphFormat.Alignment = 0  ' Alinhar à esquerda
            End With
            
            ' ? CHECKPOINT 9: Cores condicionais para Horizonte
            Dim cabecalhoColuna As String
            cabecalhoColuna = LCase(Trim(ws.Cells(1, j).Value))
            
            If InStr(cabecalhoColuna, "horizonte") > 0 Then
                Call FormatarCelulaHorizonte(tabela.Cell(i, j), valorCelula)
            End If
        Next j
        
        ' Atualizar barra de progresso
        If i Mod 10 = 0 Then
            Application.StatusBar = "Processando linha " & i & " de " & ultimaLinha
            DoEvents
        End If
    Next i
    
    ' ========== SALVAR DOCUMENTO ==========
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
            MsgBox "? PDF gerado com sucesso!" & vbCrLf & _
                   "Local: " & pdfPath, vbInformation
        Else
            MsgBox "?? Não foi possível converter para PDF." & vbCrLf & _
                   "Arquivo Word salvo em: " & caminhoSalvar, vbExclamation
        End If
        On Error GoTo 0
    End If
    
    ' ========== FINALIZAÇÃO ==========
    sucesso = True
    Application.StatusBar = False
    
    MsgBox "? Relatório gerado com sucesso!" & vbCrLf & _
           "Arquivo salvo em: " & caminhoSalvar, vbInformation, "Concluído"
    
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
    
    ' ? CHECKPOINT 10: Tratamento de erros completo
    Dim erroMsg As String
    erroMsg = "? ERRO DETALHADO:" & vbCrLf & vbCrLf
    erroMsg = erroMsg & "Descrição: " & Err.Description & vbCrLf
    erroMsg = erroMsg & "Número: " & Err.Number & vbCrLf
    erroMsg = erroMsg & "Linha aproximada: " & Erl
    
    MsgBox erroMsg, vbCritical, "Erro"
    
    Resume Limpeza
End Sub

' ======================
' FUNÇÃO PARA FORMATAR CÉLULA HORIZONTE
' ======================
Private Sub FormatarCelulaHorizonte(celula As Object, valor As String)
    On Error Resume Next
    
    Dim horizonte As String
    horizonte = LCase(Trim(valor))
    
    ' Centralizar texto
    celula.Range.ParagraphFormat.Alignment = 1  ' Centralizado
    
    ' Aplicar cores condicionais
    Select Case horizonte
        Case "curto prazo"
            celula.Range.Font.Color = RGB(0, 100, 0)   ' Verde escuro
            celula.Range.Bold = True
            
        Case "médio prazo", "medio prazo"
            celula.Range.Font.Color = RGB(255, 140, 0)  ' Laranja
            celula.Range.Bold = True
            
        Case "longo prazo"
            celula.Range.Font.Color = RGB(178, 34, 34)  ' Vermelho tijolo
            celula.Range.Bold = True
    End Select
End Sub

' ======================
' FUNÇÃO PARA TESTE SIMPLES
' ======================
Sub TestarPreenchimentoSimples()
    ' Teste simples para verificar se os dados estão sendo lidos corretamente
    
    Dim ws As Worksheet
    On Error Resume Next
    Set ws = ThisWorkbook.Worksheets("Contingências Duplas")
    If ws Is Nothing Then
        Set ws = ThisWorkbook.Worksheets(1)
    End If
    On Error GoTo 0
    
    Dim ultimaLinha As Long, ultimaColuna As Long
    ultimaLinha = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
    ultimaColuna = ws.Cells(1, ws.Columns.Count).End(xlToLeft).Column
    
    Dim msg As String
    msg = "TESTE DE PREENCHIMENTO:" & vbCrLf & vbCrLf
    msg = msg & "Planilha: " & ws.Name & vbCrLf
    msg = msg & "Linhas: " & ultimaLinha & vbCrLf
    msg = msg & "Colunas: " & ultimaColuna & vbCrLf & vbCrLf
    
    ' Mostrar primeiras 3 linhas
    Dim i As Long, j As Long
    For i = 1 To Application.Min(3, ultimaLinha)
        msg = msg & "Linha " & i & ": "
        For j = 1 To Application.Min(5, ultimaColuna)
            msg = msg & ws.Cells(i, j).Text & " | "
        Next j
        msg = msg & vbCrLf
    Next i
    
    MsgBox msg, vbInformation, "Teste de Preenchimento"
End Sub

' ======================
' FUNÇÃO PARA DEBUG DETALHADO
' ======================
Sub DebugDetalhado()
    ' Mostra informações detalhadas para debug
    
    Dim ws As Worksheet
    On Error Resume Next
    Set ws = ThisWorkbook.Worksheets("Contingências Duplas")
    If ws Is Nothing Then
        Set ws = ThisWorkbook.Worksheets(1)
        MsgBox "Usando planilha: " & ws.Name, vbInformation
    End If
    On Error GoTo 0
    
    ' Verificar dados
    Dim ultimaLinha As Long, ultimaColuna As Long
    ultimaLinha = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
    ultimaColuna = ws.Cells(1, ws.Columns.Count).End(xlToLeft).Column
    
    ' Criar relatório de debug
    Dim debugInfo As String
    debugInfo = "DEBUG DETALHADO:" & vbCrLf & vbCrLf
    debugInfo = debugInfo & "=== INFORMAÇÕES DA PLANILHA ===" & vbCrLf
    debugInfo = debugInfo & "Nome: " & ws.Name & vbCrLf
    debugInfo = debugInfo & "Linhas totais: " & ultimaLinha & vbCrLf
    debugInfo = debugInfo & "Colunas totais: " & ultimaColuna & vbCrLf & vbCrLf
    
    debugInfo = debugInfo & "=== CABEÇALHOS ===" & vbCrLf
    For j = 1 To ultimaColuna
        debugInfo = debugInfo & "Coluna " & j & ": " & ws.Cells(1, j).Value & vbCrLf
    Next j
    
    debugInfo = debugInfo & vbCrLf & "=== AMOSTRA DE DADOS (3 primeiras linhas) ===" & vbCrLf
    For i = 1 To Application.Min(3, ultimaLinha)
        debugInfo = debugInfo & "Linha " & i & ": "
        For j = 1 To ultimaColuna
            debugInfo = debugInfo & "'" & ws.Cells(i, j).Text & "' "
        Next j
        debugInfo = debugInfo & vbCrLf
    Next i
    
    ' Mostrar em caixa de mensagem
    MsgBox debugInfo, vbInformation, "Debug Detalhado"
    
    ' Também imprimir na Janela Imediata
    Debug.Print debugInfo
End Sub


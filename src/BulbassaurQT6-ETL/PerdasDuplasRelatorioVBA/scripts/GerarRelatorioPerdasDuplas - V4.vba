'============================================
' GERADOR DE RELATÓRIOS PERDAS DUPLAS ETL V4 - VERSÃO 13/01/2026
'============================================

' Controle de versão:
' V3: 16/12/2025
' - [x] Configuração de formatação do relatório por variáveis globais
' - [x] Implementação da função de log
' - [x] Implementação da função de erro
' - [x] Implementação da função de teste rápido
' - [x] Implementação da função de formatação de células horizonte, volume, área, contingência
' V4: 13/01/2026
' - [x] Implementação da função de download do template Word direto do sharepoint
' - [x] Mesma versão do V3, mas com o template Word já baixado na pasta de downloads e usando as funcoes corretas
' V5: 13/01/2026
' - [x] Implementação da função que pega as informações da aba Modificações do excel
' - [x] Implementação da funcao que coloca a revisão e data correta no relatório




Option Explicit

' ======================
' CONFIGURAÇÕES GLOBAIS
' ======================

' Configurações de Formatação
Public Const CABECALHO_AZUL As Boolean = False  ' True: Azul Claro Template | False: Cabeçalho padrão (negrito e fonte 14)
Public Const DEBUG_MODE As Boolean = False     ' True: Mostra MsgBox de debug | False: Silencioso
Public Const CONVERTER_PDF As Boolean = False  ' True: Converte automaticamente para PDF

' Configurações de Fonte
Public Const FONTE_CABECALHO As String = "Calibri"
Public Const TAMANHO_CABECALHO As Integer = 14
Public Const FONTE_DADOS As String = "Calibri"
Public Const TAMANHO_DADOS As Integer = 10

' Configurações de Tabela
Public Const ALTURA_LINHA As Integer = 20      ' Altura mínima das linhas (pontos)
Public Const ESPESSURA_BORDA As Integer = 1    ' Espessura das bordas (1=fininha)
Public Const REPETIR_CABECALHO As Boolean = True  ' Repete cabeçalho em todas páginas

' Cores (formato RGB)
Public Const COR_AZUL_ONS As Long = 10092543   ' RGB(68, 114, 196)
Public Const COR_TEXTO_BRANCO As Long = 16777215 ' RGB(255, 255, 255)
Public Const COR_TEXTO_PRETO As Long = 0       ' RGB(0, 0, 0)

' Larguras das colunas (em centímetros)
Public Const LARGURA_VOLUME As Double = 2.5
Public Const LARGURA_AREA As Double = 8.0
Public Const LARGURA_CONTINGENCIA As Double = 12.0
Public Const LARGURA_HORIZONTE As Double = 4.0
Public Const LARGURA_PADRAO As Double = 5.0

' Cores condicionais para Horizonte
Public Const COR_CURTO_PRAZO As Long = 25600    ' Verde escuro: RGB(0, 100, 0)
Public Const COR_MEDIO_PRAZO As Long = 42495    ' Laranja: RGB(255, 140, 0)
Public Const COR_LONGO_PRAZO As Long = 11674146 ' Vermelho tijolo: RGB(178, 34, 34)

' ======================
' MÓDULO 1 PRINCIPAL (MÉTODOS)
' ======================

' ======================
' Rotina Principal - Colocando o Word template já baixado na pasta de downloads
' ======================
Sub GerarRelatorioPerdasDuplasETL()
    On Error GoTo ErroHandler
    
    Dim templateWord As String
    Dim pagina As Long
    
    ' Declarar logger (se estiver usando a classe)
    ' Dim logger As New clsLogger
    ' logger.DebugMode = DEBUG_MODE
    
    ' Log simples (sem classe)
    Call Log("Iniciando geração de relatório")
    
    ' 1. ESCOLHER ARQUIVO WORD
    templateWord = Application.GetOpenFilename( _
        FileFilter:="Arquivos Word (*.docx; *.doc), *.docx; *.doc", _
        Title:="Selecione o Template Word")
    
    If templateWord = "False" Then
        Call Log("Usuário cancelou seleção do template")
        Exit Sub
    End If
    
    ' 2. PERGUNTAR NÚMERO DA PÁGINA
    Dim respostaPagina As String
    respostaPagina = InputBox("Em qual página deseja inserir a tabela?" & vbCrLf & _
                            "Digite um número (ex: 1, 2, 3...):", _
                            "Número da Página", "1")
    
    If respostaPagina = "" Then
        Call Log("Usuário cancelou operação")
        Exit Sub
    End If
    
    If Not IsNumeric(respostaPagina) Then
        MsgBox "Por favor, digite um número válido!", vbExclamation
        Exit Sub
    End If
    
    pagina = CLng(respostaPagina)
    Call Log("Página selecionada: " & pagina)
    
    ' 3. EXECUTAR FUNÇÃO PRINCIPAL
    Call CriarRelatorioCorrigido(templateWord, pagina, CONVERTER_PDF)
    
    Exit Sub
    
ErroHandler:
    Call LogErro(Err.Description, Err.Number)
    MsgBox "❌ ERRO: " & Err.Description, vbCritical, "Erro no Processamento"
End Sub

' ======================
' FUNÇÃO Para criar o relatório
' ======================
Sub CriarRelatorioCorrigido(caminhoWord As String, pagina As Long, converterPDF As Boolean)
    
    ' Declaração de variáveis
    Dim wordApp As Object, wordDoc As Object
    Dim tabela As Object
    Dim ws As Worksheet
    Dim ultimaLinha As Long, ultimaColuna As Long
    Dim i As Long, j As Long
    Dim caminhoSalvar As String
    Dim sucesso As Boolean
    
    On Error GoTo ErroHandler
    
    Call Log("Iniciando função principal")
    
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
        Call Log("Aba 'Contingências Duplas' não encontrada. Usando: " & ws.Name)
    End If
    On Error GoTo ErroHandler
    
    ' Obter dimensões dos dados
    ultimaLinha = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
    ultimaColuna = ws.Cells(1, ws.Columns.Count).End(xlToLeft).Column
    
    Call Log("Dimensões - Linhas: " & ultimaLinha & ", Colunas: " & ultimaColuna)
    
    ' Exibir debug se ativado
    If DEBUG_MODE Then
        MsgBox "DEBUG INFO:" & vbCrLf & _
               "Planilha: " & ws.Name & vbCrLf & _
               "Última linha: " & ultimaLinha & vbCrLf & _
               "Última coluna: " & ultimaColuna, vbInformation, "Verificação"
    End If
    
    If ultimaLinha < 2 Then
        MsgBox "Não há dados na planilha! Apenas cabeçalho encontrado.", vbExclamation
        Exit Sub
    End If
    
    ' ========== PERGUNTAR ONDE SALVAR ==========
    caminhoSalvar = Application.GetSaveAsFilename( _
        InitialFileName:="Relatorio_Perdas_Duplas_" & Format(Now, "ddmmyyyy_hhmm") & ".docx", _
        FileFilter:="Documentos Word (*.docx), *.docx")
    
    If caminhoSalvar = "False" Then
        Call Log("Usuário cancelou salvamento")
        Exit Sub
    End If
    
    ' Garantir extensão .docx
    If LCase(Right(caminhoSalvar, 5)) <> ".docx" Then
        caminhoSalvar = caminhoSalvar & ".docx"
    End If
    
    Call Log("Caminho para salvar: " & caminhoSalvar)
    
    ' ========== INICIAR WORD ==========
    Application.StatusBar = "Abrindo Microsoft Word..."
    Call Log("Criando aplicação Word")
    
    Set wordApp = CreateObject("Word.Application")
    wordApp.Visible = True
    
    ' CORREÇÃO DO BUG: Criar novo documento se não existir
    If caminhoWord = "" Or Dir(caminhoWord) = "" Then
        Call Log("Criando novo documento Word")
        Set wordDoc = wordApp.Documents.Add
    Else
        Call Log("Abrindo template existente: " & caminhoWord)
        Set wordDoc = wordApp.Documents.Open(caminhoWord)
    End If
    
    ' ========== INSERIR DADOS PRINCIPAIS ==========
    Application.StatusBar = "Criando tabela principal..."
    Call Log("Criando tabela com " & ultimaLinha & " linhas e " & ultimaColuna & " colunas")
    
    ' Ir para o final do documento para inserir a tabela
    wordApp.Selection.EndKey Unit:=6 ' wdStory
    
    ' Adicionar título
    wordApp.Selection.TypeText "RELATÓRIO DE PERDAS DUPLAS" & vbCrLf
    wordApp.Selection.TypeText "Gerado em: " & Format(Now, "dd/mm/yyyy HH:MM") & vbCrLf & vbCrLf
    
    ' Criar tabela principal
    Set tabela = wordDoc.Tables.Add(wordApp.Selection.Range, ultimaLinha, ultimaColuna)
    
    ' ========== CONFIGURAR LARGURAS DAS COLUNAS ==========
    Application.StatusBar = "Configurando larguras das colunas..."
    
    For j = 1 To ultimaColuna
        Dim cabecalho As String
        cabecalho = LCase(Trim(ws.Cells(1, j).Value))
        Dim larguraCm As Double
        
        ' Definir larguras específicas usando constantes
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
        
        ' Aplicar largura (1 cm = 28.35 pontos)
        tabela.Columns(j).Width = larguraCm * 28.35
        Call Log("Coluna " & j & " - Largura: " & larguraCm & " cm")
    Next j
    
    ' ========== CONFIGURAR FORMATAÇÃO DA TABELA ==========
    Application.StatusBar = "Configurando formatação da tabela..."
    
    ' Bordas leves (1px)
    On Error Resume Next
    With tabela.Borders
        .InsideLineStyle = 1  ' wdLineStyleSingle
        .OutsideLineStyle = 1
        .InsideLineWidth = ESPESSURA_BORDA
        .OutsideLineWidth = ESPESSURA_BORDA
    End With
    
    ' Altura das linhas ajustada
    For i = 1 To ultimaLinha
        tabela.Rows(i).HeightRule = 0  ' wdRowHeightAuto
        tabela.Rows(i).Height = ALTURA_LINHA
    Next i
    
    ' Cabeçalho que se repete
    If REPETIR_CABECALHO Then
        tabela.Rows(1).HeadingFormat = True
    End If
    
    ' ========== PREENCHER CABEÇALHO ==========
    Application.StatusBar = "Preenchendo cabeçalho..."
    
    For j = 1 To ultimaColuna
        Dim cabecalhoTexto As String
        cabecalhoTexto = Trim(ws.Cells(1, j).Value)
        
        Call Log("Preenchendo cabeçalho coluna " & j & ": " & cabecalhoTexto)
        tabela.Cell(1, j).Range.Text = cabecalhoTexto
        
        ' Formatação do cabeçalho (usando constantes globais)
        With tabela.Cell(1, j).Range
            .Bold = True
            .Font.Name = FONTE_CABECALHO
            .Font.Size = TAMANHO_CABECALHO
            .ParagraphFormat.Alignment = 1  ' Centralizado
            
            If CABECALHO_AZUL Then
                .Font.Color = COR_TEXTO_BRANCO
                .Shading.BackgroundPatternColor = COR_AZUL_ONS
            Else
                .Font.Color = COR_TEXTO_PRETO
                .Font.Bold = True
                ' Sem cor de fundo
            End If
        End With
    Next j
    
    ' ========== PREENCHER DADOS ==========
    Application.StatusBar = "Preenchendo dados..."
    
    For i = 2 To ultimaLinha
        For j = 1 To ultimaColuna
            Dim valorCelula As String
            valorCelula = Trim(ws.Cells(i, j).Text)
            
            If valorCelula = "" Then valorCelula = "-"
            
            ' DEBUG: Mostrar primeiras linhas
            If DEBUG_MODE And i <= 3 Then
                Call Log("Linha " & i & ", Coluna " & j & ": " & valorCelula)
            End If
            
            tabela.Cell(i, j).Range.Text = valorCelula
            
            ' Formatação básica das células
            With tabela.Cell(i, j).Range
                .Font.Name = FONTE_DADOS
                .Font.Size = TAMANHO_DADOS
                .ParagraphFormat.Alignment = 0  ' Alinhar à esquerda
            End With
            
            ' Cores condicionais para Horizonte
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
    Call Log("Salvando documento em: " & caminhoSalvar)
    
    On Error Resume Next
    wordDoc.SaveAs2 caminhoSalvar
    If Err.Number <> 0 Then
        Call LogErro("Erro ao salvar: " & Err.Description)
        MsgBox "Erro ao salvar: " & Err.Description, vbCritical
        GoTo Limpeza
    End If
    On Error GoTo 0
    
    Call Log("Documento salvo com sucesso")
    
    ' ========== CONVERTER PARA PDF ==========
    If converterPDF Then
        Application.StatusBar = "Convertendo para PDF..."
        Call Log("Convertendo para PDF")
        
        Dim pdfPath As String
        pdfPath = Left(caminhoSalvar, InStrRev(caminhoSalvar, ".")) & "pdf"
        
        On Error Resume Next
        wordDoc.SaveAs2 pdfPath, 17  ' wdFormatPDF
        If Err.Number = 0 Then
            Call Log("PDF gerado com sucesso: " & pdfPath)
            MsgBox "✅ PDF gerado com sucesso!" & vbCrLf & _
                   "Local: " & pdfPath, vbInformation
        Else
            Call LogErro("Falha ao converter PDF: " & Err.Description)
            MsgBox "⚠️ Não foi possível converter para PDF." & vbCrLf & _
                   "Arquivo Word salvo em: " & caminhoSalvar, vbExclamation
        End If
        On Error GoTo 0
    End If
    
    ' ========== FINALIZAÇÃO ==========
    sucesso = True
    Application.StatusBar = False
    
    MsgBox "✅ Relatório gerado com sucesso!" & vbCrLf & _
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
    
    Call Log("Processo concluído - Limpeza realizada")
    Exit Sub
    
ErroHandler:
    Application.StatusBar = False
    Call LogErro(Err.Description & " (Linha: " & Erl & ")", Err.Number)
    
    Dim erroMsg As String
    erroMsg = "❌ ERRO DETALHADO:" & vbCrLf & vbCrLf
    erroMsg = erroMsg & "Descrição: " & Err.Description & vbCrLf
    erroMsg = erroMsg & "Número: " & Err.Number & vbCrLf
    erroMsg = erroMsg & "Linha aproximada: " & Erl
    
    MsgBox erroMsg, vbCritical, "Erro"
    Resume Limpeza
End Sub


' ============================================
' FUNÇÃO DE DOWNLOAD DO TEMPLATE WORD DIRETO DO SHAREPOINT
' ============================================
Sub ExecutarDownloadAutenticado()
    Dim urlDestino As String
    Dim caminhoLocal As String
    Dim nomeArquivo As String
    Dim dataFormatada As String
    
    ' 1. Configurar Data e Nome do Arquivo
    ' Format(Date, "yy_mm_dd") pega a data do sistema -> 26_01_13 (exemplo)
    dataFormatada = Format(Date, "yy_mm_dd")
    nomeArquivo = "word_template_" & dataFormatada & ".docx"
    
    ' 2. Definir Caminhos
    caminhoLocal = Environ("USERPROFILE") & "\Downloads\" & nomeArquivo
    urlDestino = URL_ARQUIVO_SHAREPOINT
    
    ' Limpeza preventiva do link
    If InStr(urlDestino, "?web=1") > 0 Then
        urlDestino = Replace(urlDestino, "?web=1", "")
    End If

    Debug.Print "========================================="
    Debug.Print "INICIANDO DOWNLOAD DE TEMPLATE"
    Debug.Print "Arquivo alvo: " & nomeArquivo
    Debug.Print "URL: " & urlDestino
    
    ' 3. Executar Download
    ' Se a função retornar True, o processo foi bem sucedido
    If BaixarViaWordApp(urlDestino, caminhoLocal) Then
        Debug.Print "Processo finalizado com sucesso."
    Else
        Debug.Print "Processo finalizado com ERRO."
    End If
    
End Sub

' ============================================
' FUNÇÃO VBA (Retorna True se sucesso)
' ============================================
Function BaixarViaWordApp(url As String, caminhoSalvar As String) As Boolean
    Dim wordApp As Object
    Dim wordDoc As Object
    Dim docFoiAberto As Boolean
    
    On Error GoTo ErroWord
    
    Debug.Print "Abrindo Word em background..."
    Set wordApp = CreateObject("Word.Application")
    wordApp.Visible = False
    
    Debug.Print "Acessando SharePoint..."
    ' Abre como ReadOnly para não bloquear o arquivo para outros usuários
    Set wordDoc = wordApp.Documents.Open(Filename:=url, ReadOnly:=True, Visible:=False)
    docFoiAberto = True
    
    Debug.Print "Salvando localmente..."
    ' Verifica se arquivo já existe e deleta para evitar erro de sobrescrita
    If Dir(caminhoSalvar) <> "" Then
        Kill caminhoSalvar
    End If
    
    ' 16 = wdFormatXMLDocument (docx)
    wordDoc.SaveAs2 Filename:=caminhoSalvar, FileFormat:=16
    
    ' Limpeza
    wordDoc.Close SaveChanges:=False
    docFoiAberto = False
    wordApp.Quit
    Set wordApp = Nothing
    
    MsgBox "Template baixado com sucesso!" & vbCrLf & vbCrLf & _
           "Salvo em: " & caminhoSalvar, vbInformation, "Sucesso"
           
    BaixarViaWordApp = True
    Exit Function

ErroWord:
    Debug.Print "ERRO: " & Err.Description
    
    If Not wordApp Is Nothing Then
        If docFoiAberto Then wordDoc.Close False
        wordApp.Quit
    End If
    
    MsgBox "Erro ao baixar template: " & Err.Description, vbCritical
    BaixarViaWordApp = False
End Function

'======================================================================================================================
' --- NOVA FUNÇÕES ---
'======================================================================================================================
' FUNÇÃO PARA GERAR A STRING DA REVISÃO DO EXCEL
' ============================================
Function GerarStringRevisaoDoExcel() As String
    ' Objetivo: Ler "MeuArquivo_Rev9.xlsm" e retornar "REVISÃO 9"
    Dim nomeArquivo As String
    Dim posRev As Integer
    Dim tempStr As String
    Dim i As Integer
    Dim numeroRev As String
    
    nomeArquivo = ThisWorkbook.Name ' Ex: Relatorio_Rev12.xlsm
    
    ' 1. Procura por "_Rev" ou "_rev" ou "Rev" (Case insensitive)
    posRev = InStr(1, nomeArquivo, "Rev", vbTextCompare)
    
    If posRev = 0 Then
        GerarStringRevisaoDoExcel = "ERRO"
        Exit Function
    End If
    
    ' 2. Pega tudo depois do "Rev"
    tempStr = Mid(nomeArquivo, posRev + 3) ' +3 para pular o "Rev"
    
    ' 3. Extrai apenas os números logo após o Rev
    numeroRev = ""
    For i = 1 To Len(tempStr)
        Dim charAtual As String
        charAtual = Mid(tempStr, i, 1)
        
        If IsNumeric(charAtual) Then
            numeroRev = numeroRev & charAtual
        Else
            ' Se achou um ponto (.) ou traço, paramos (ex: Rev9.xlsm)
            Exit For
        End If
    Next i
    
    If numeroRev <> "" Then
        GerarStringRevisaoDoExcel = "REVISÃO " & numeroRev
    Else
        GerarStringRevisaoDoExcel = "ERRO"
    End If
End Function

Sub SubstituirTextoNoWord(doc As Object, textoAntigo As String, textoNovo As String)
    Dim myRange As Object
    Set myRange = doc.Content
    With myRange.Find
        .ClearFormatting
        .Text = textoAntigo
        .Replacement.Text = textoNovo
        .Forward = True
        .Wrap = 1
        .Execute Replace:=2
    End With
End Sub

Sub InserirTabelaModificacoes(doc As Object, app As Object)
    Dim wsMod As Worksheet
    Dim ultLin As Long, ultCol As Long
    Dim tblMod As Object
    Dim i As Long, j As Long
    
    On Error Resume Next
    Set wsMod = ThisWorkbook.Worksheets("Modificações")
    On Error GoTo 0
    
    If wsMod Is Nothing Then Call Log("Aba Modificações não encontrada"): Exit Sub
    
    ultLin = wsMod.Cells(wsMod.Rows.Count, "A").End(xlUp).Row
    ultCol = wsMod.Cells(1, wsMod.Columns.Count).End(xlToLeft).Column
    
    app.Selection.HomeKey Unit:=6
    With app.Selection.Find
        .Text = "Revisões do relatório"
        .Execute
    End With
    
    If app.Selection.Find.Found Then
        app.Selection.MoveDown Unit:=5, Count:=1
        app.Selection.TypeParagraph
    Else
        app.Selection.EndKey Unit:=6
        app.Selection.TypeText vbCrLf & "HISTÓRICO DE MODIFICAÇÕES" & vbCrLf
    End If
    
    Set tblMod = doc.Tables.Add(app.Selection.Range, ultLin, ultCol)
    tblMod.Borders.InsideLineStyle = 1
    tblMod.Borders.OutsideLineStyle = 1
    
    For i = 1 To ultLin
        For j = 1 To ultCol
            tblMod.Cell(i, j).Range.Text = wsMod.Cells(i, j).Text
        Next j
    Next i
    app.Selection.EndKey Unit:=6
End Sub

'======================================================================================================================

' ======================
' FUNÇÃO PARA FORMATAR CÉLULA HORIZONTE
' ======================
Private Sub FormatarCelulaHorizonte(celula As Object, valor As String)
    On Error Resume Next
    
    Dim horizonte As String
    horizonte = LCase(Trim(valor))
    
    ' Centralizar texto
    celula.Range.ParagraphFormat.Alignment = 1  ' Centralizado
    
    ' Aplicar cores condicionais usando constantes
    Select Case horizonte
        Case "curto prazo"
            celula.Range.Font.Color = COR_CURTO_PRAZO
            celula.Range.Bold = True
            
        Case "médio prazo", "medio prazo"
            celula.Range.Font.Color = COR_MEDIO_PRAZO
            celula.Range.Bold = True
            
        'Case "longo prazo"
        '    celula.Range.Font.Color = COR_LONGO_PRAZO
        '    celula.Range.Bold = True
    End Select
End Sub

' ======================
' MÉTODOS DE LOG 
' ======================
Private Sub Log(msg As String)
    ' Imprime no Immediate Window (Ctrl+G para ver)
    Debug.Print Format(Now, "dd/mm/yyyy hh:mm:ss") & " - " & msg
    
    ' Mostra MsgBox se DEBUG_MODE estiver ativado
    If DEBUG_MODE Then
        MsgBox msg, vbInformation, "DEBUG"
    End If
End Sub

Private Sub LogErro(erroDesc As String, Optional erroNum As Long = 0)
    Dim msg As String
    msg = "ERRO " & erroNum & ": " & erroDesc
    Log msg
End Sub

' ======================
' FUNÇÃO PARA TESTE VBA
' ======================
Sub TesteRapido()
    ' Testa as configurações atuais
    Dim msg As String
    msg = "CONFIGURAÇÕES ATUAIS:" & vbCrLf & vbCrLf
    msg = msg & "Cabeçalho Azul: " & CABECALHO_AZUL & vbCrLf
    msg = msg & "Modo Debug: " & DEBUG_MODE & vbCrLf
    msg = msg & "Converter PDF: " & CONVERTER_PDF & vbCrLf
    msg = msg & "Fonte Cabeçalho: " & FONTE_CABECALHO & " " & TAMANHO_CABECALHO & "pt" & vbCrLf
    msg = msg & "Fonte Dados: " & FONTE_DADOS & " " & TAMANHO_DADOS & "pt"
    
    MsgBox msg, vbInformation, "Configurações do Sistema"
End Sub
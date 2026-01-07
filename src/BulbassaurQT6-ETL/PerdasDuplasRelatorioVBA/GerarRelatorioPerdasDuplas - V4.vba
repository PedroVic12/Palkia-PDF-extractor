'============================================
' GERADOR DE RELATÓRIOS PERDAS DUPLAS ETL V4.2 - ACESSO DIRETO AO SHAREPOINT
'============================================
Option Explicit

' ======================
' CONFIGURAÇÕES GLOBAIS
' ======================
Public Const DEBUG_MODE As Boolean = True

' ======================
' CONFIGURAÇÕES SHAREPOINT - LINK DIRETO
' ======================
' IMPORTANTE: Precisamos converter seu link para um link de download direto
' Link original: https://onsbr.sharepoint.com/:w:/s/soumaisons/IQCV7m4JrpKPR5ahRXRZF5cCAXDBNfb_yKAGujqO0ibWwOo?e=mMqkza

' https://onsbr.sharepoint.com/:w:/s/soumaisons/IQCV7m4JrpKPR5ahRXRZF5cCAXDBNfb_yKAGujqO0ibWwOo?e=fVFScq
' Para obter o link direto:
' 1. Vá até o arquivo no SharePoint
' 2. Clique nos "..." (elipses)
' 3. Selecione "Copiar link"
' 4. Escolha a opção "Link de exibição"
' 5. OU use o método abaixo para gerar automaticamente

' Constante para URL base do SharePoint
Private Const SHAREPOINT_BASE_URL As String = "https://onsbr.sharepoint.com"

' Função para converter link de edição para link de download
Public Function GerarLinkDownload(linkEdicao As String) As String
    ' Extrair o ID único do documento do link
    ' Padrão: .../IQCV7m4JrpKPR5ahRXRZF5cCAXDBNfb_yKAGujqO0ibWwOo?e=...
    Dim inicioId As Long, fimId As Long
    Dim docId As String
    
    inicioId = InStrRev(linkEdicao, "/") + 1
    fimId = InStr(linkEdicao, "?") - 1
    
    If inicioId > 0 And fimId > inicioId Then
        docId = Mid(linkEdicao, inicioId, fimId - inicioId + 1)
        
        ' Construir link de download
        GerarLinkDownload = SHAREPOINT_BASE_URL & "/sites/soumaisons/_layouts/15/download.aspx?SourceUrl=" & _
                           "/sites/soumaisons/Documentos%20Compartilhados/" & docId & ".docx"
    Else
        GerarLinkDownload = ""
    End If
End Function

' ======================
' FUNÇÃO PRINCIPAL ATUALIZADA
' ======================
Sub GerarRelatorioPerdasDuplasETL()
    On Error GoTo ErroHandler
    
    Dim templateWord As String
    Dim pagina As Long
    Dim numRevisao As String
    Dim mesEmissao As String
    
    Call Log("Iniciando geração de relatório")
    
    ' 1. TENTAR BAIXAR DIRETAMENTE DO SHAREPOINT
    templateWord = BaixarTemplateDiretoSharepoint()
    
    If templateWord = "" Then
        ' Fallback: pedir para usuário selecionar
        templateWord = Application.GetOpenFilename( _
            FileFilter:="Arquivos Word (*.docx; *.doc), *.docx; *.doc", _
            Title:="Selecione o Template Word")
    End If
    
    If templateWord = "False" Or templateWord = "" Then
        Call Log("Usuário cancelou operação")
        Exit Sub
    End If
    
    ' 2. EXTRAIR REVISÃO
    numRevisao = ExtrairNumeroRevisao(ThisWorkbook.Name)
    mesEmissao = Format(Now, "mmmm", vbLocalDateTime)
    Call Log("Revisão: " & numRevisao & ", Mês: " & mesEmissao)
    
    ' 3. OBTER PÁGINA
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
    
    ' 4. EXECUTAR FUNÇÃO PRINCIPAL
    Call CriarRelatorioComRevisao(templateWord, pagina, False, numRevisao, mesEmissao)
    
    Exit Sub
    
ErroHandler:
    Call LogErro(Err.Description, Err.Number)
    MsgBox "❌ ERRO: " & Err.Description, vbCritical, "Erro no Processamento"
End Sub

' ======================
' FUNÇÃO PARA BAIXAR DIRETAMENTE DO SHAREPOINT
' ======================
Function BaixarTemplateDiretoSharepoint() As String
    On Error GoTo ErroHandler
    
    Dim xmlHttp As Object
    Dim stream As Object
    Dim linkDownload As String
    Dim localPath As String
    Dim sharepointLink As String
    
    ' Link do SharePoint (cole seu link aqui)
    sharepointLink = "https://onsbr.sharepoint.com/:w:/s/soumaisons/IQCV7m4JrpKPR5ahRXRZF5cCAXDBNfb_yKAGujqO0ibWwOo?e=fVFScq"
    
    ' Tentar converter para link de download
    linkDownload = ConverterParaLinkDownload(sharepointLink)
    
    If linkDownload = "" Then
        Call Log("Não foi possível converter o link do SharePoint")
        BaixarTemplateDiretoSharepoint = ""
        Exit Function
    End If
    
    Call Log("Tentando baixar de: " & linkDownload)
    
    ' Criar diretório temporário
    If Dir("C:\Temp", vbDirectory) = "" Then
        MkDir "C:\Temp"
    End If
    
    localPath = "C:\Temp\Template_Perdas_Duplas_" & Format(Now, "ddmmyyyy") & ".docx"
    
    ' Usar XMLHTTP com credenciais
    Set xmlHttp = CreateObject("MSXML2.ServerXMLHTTP.6.0")
    
    ' Configurar timeout
    xmlHttp.setTimeouts 30000, 30000, 30000, 30000
    
    ' Tentar baixar
    xmlHttp.Open "GET", linkDownload, False
    
    ' IMPORTANTE: Usar credenciais automáticas do Windows
    xmlHttp.setOption 2, 13056 ' SXH_OPTION_IGNORE_SERVER_SSL_CERT_ERROR_FLAGS
    xmlHttp.setRequestHeader "User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    ' Usar autenticação automática do Windows
    xmlHttp.SetAutoLogonPolicy 0 ' AutoLogonPolicy_Always
    
    xmlHttp.send
    
    ' Verificar resposta
    If xmlHttp.Status = 200 Then
        ' Salvar arquivo
        Set stream = CreateObject("ADODB.Stream")
        stream.Type = 1 ' Binary
        stream.Open
        stream.Write xmlHttp.responseBody
        stream.SaveToFile localPath, 2 ' Sobrescrever
        stream.Close
        
        Call Log("✅ Template baixado com sucesso: " & localPath)
        BaixarTemplateDiretoSharepoint = localPath
    Else
        Call Log("❌ Falha ao baixar. Status: " & xmlHttp.Status & " - " & xmlHttp.statusText)
        BaixarTemplateDiretoSharepoint = ""
    End If
    
    Exit Function
    
ErroHandler:
    Call LogErro("Erro ao baixar template: " & Err.Description)
    BaixarTemplateDiretoSharepoint = ""
End Function

' ======================
' FUNÇÃO PARA CONVERTER LINK DO SHAREPOINT
' ======================
Function ConverterParaLinkDownload(linkEdicao As String) As String
    On Error Resume Next
    
    ' Método 1: Se já for um link de download direto
    If InStr(1, linkEdicao, "download.aspx", vbTextCompare) > 0 Then
        ConverterParaLinkDownload = linkEdicao
        Exit Function
    End If
    
    ' Método 2: Converter link de edição para download
    ' Padrão: https://onsbr.sharepoint.com/:w:/s/soumaisons/ID_DOCUMENTO?e=CODIGO
    
    ' Extrair partes do link
    Dim partes() As String
    Dim docId As String
    Dim i As Long
    
    ' Remover parâmetros
    partes = Split(linkEdicao, "?")
    If UBound(partes) >= 0 Then
        ' Encontrar o ID do documento (última parte antes de ?)
        Dim urlPartes() As String
        urlPartes = Split(partes(0), "/")
        
        ' Pegar a última parte
        docId = urlPartes(UBound(urlPartes))
        
        ' Construir link de download
        ' Formato padrão do SharePoint Online
        ConverterParaLinkDownload = "https://onsbr.sharepoint.com/sites/soumaisons/_layouts/15/download.aspx" & _
                                   "?UniqueId=" & docId & "&e=" & Mid(partes(1), 3)
    Else
        ConverterParaLinkDownload = ""
    End If
    
    ' Método alternativo se o primeiro falhar
    If ConverterParaLinkDownload = "" Then
        ConverterParaLinkDownload = GerarLinkDownloadManual(linkEdicao)
    End If
End Function

Function GerarLinkDownloadManual(linkEdicao As String) As String
    ' Método manual: Pedir ao usuário para obter o link correto
    Dim resposta As VbMsgBoxResult
    
    resposta = MsgBox("Para configurar o acesso automático ao SharePoint:" & vbCrLf & vbCrLf & _
                     "1. Vá até o arquivo no SharePoint" & vbCrLf & _
                     "2. Clique em '...' (Mais opções)" & vbCrLf & _
                     "3. Selecione 'Baixar'" & vbCrLf & _
                     "4. Durante o download, copie o link do navegador" & vbCrLf & _
                     "5. Cole o link abaixo" & vbCrLf & vbCrLf & _
                     "Deseja abrir o SharePoint agora?", _
                     vbQuestion + vbYesNo, "Configurar SharePoint")
    
    If resposta = vbYes Then
        ' Abrir SharePoint
        Shell "cmd /c start " & linkEdicao, vbNormalFocus
        
        ' Pedir link de download
        Dim linkDownload As String
        linkDownload = InputBox("Após abrir o SharePoint e iniciar o download:" & vbCrLf & _
                               "1. Copie o link da barra de endereços durante o download" & vbCrLf & _
                               "2. Cole aqui:" & vbCrLf & _
                               "(Exemplo: https://.../download.aspx?...)", _
                               "Cole o Link de Download", "")
        
        If linkDownload <> "" Then
            ' Salvar o link para uso futuro
            SalvarLinkConfigurado linkDownload
            GerarLinkDownloadManual = linkDownload
        Else
            GerarLinkDownloadManual = ""
        End If
    Else
        GerarLinkDownloadManual = ""
    End If
End Function

Sub SalvarLinkConfigurado(linkDownload As String)
    ' Salvar em uma planilha de configuração
    On Error Resume Next
    
    Dim wsConfig As Worksheet
    Set wsConfig = ThisWorkbook.Sheets("Config")
    
    If wsConfig Is Nothing Then
        Set wsConfig = ThisWorkbook.Sheets.Add
        wsConfig.Name = "Config"
    End If
    
    wsConfig.Range("A1").Value = "SHAREPOINT_TEMPLATE_URL"
    wsConfig.Range("B1").Value = linkDownload
    
    Call Log("Link configurado salvo: " & linkDownload)
End Function

Function ObterLinkConfigurado() As String
    On Error Resume Next
    
    Dim wsConfig As Worksheet
    Set wsConfig = ThisWorkbook.Sheets("Config")
    
    If Not wsConfig Is Nothing Then
        ObterLinkConfigurado = wsConfig.Range("B1").Value
    Else
        ObterLinkConfigurado = ""
    End If
End Function

' ======================
' MÉTODO ALTERNATIVO: USAR WORD PARA ABRIR DIRETAMENTE
' ======================
Function BaixarViaWordDireto() As String
    On Error GoTo ErroHandler
    
    Dim wordApp As Object
    Dim wordDoc As Object
    Dim localPath As String
    Dim sharepointLink As String
    
    Call Log("Tentando abrir template via Word...")
    
    ' Criar caminho local
    localPath = "C:\Temp\Template_Word_" & Format(Now, "ddmmyyyy_hhnnss") & ".docx"
    
    ' Iniciar Word
    Set wordApp = CreateObject("Word.Application")
    wordApp.Visible = False
    wordApp.DisplayAlerts = False
    
    ' URL do SharePoint (use o link original)
    sharepointLink = "https://onsbr.sharepoint.com/:w:/s/soumaisons/IQCV7m4JrpKPR5ahRXRZF5cCAXDBNfb_yKAGujqO0ibWwOo?e=mMqkza"
    
    ' Tentar abrir diretamente
    On Error Resume Next
    Set wordDoc = wordApp.Documents.Open(sharepointLink, ReadOnly:=True)
    
    If Err.Number = 0 And Not wordDoc Is Nothing Then
        ' Salvar localmente
        wordDoc.SaveAs2 localPath
        wordDoc.Close False
        
        Call Log("✅ Template aberto via Word e salvo em: " & localPath)
        BaixarViaWordDireto = localPath
    Else
        Call Log("❌ Word não conseguiu abrir o link diretamente")
        BaixarViaWordDireto = ""
    End If
    
    ' Limpar
    wordApp.Quit
    Set wordDoc = Nothing
    Set wordApp = Nothing
    
    Exit Function
    
ErroHandler:
    On Error Resume Next
    If Not wordDoc Is Nothing Then wordDoc.Close False
    If Not wordApp Is Nothing Then wordApp.Quit
    Call LogErro("Erro ao abrir via Word: " & Err.Description)
    BaixarViaWordDireto = ""
End Function

' ======================
' BOTÃO ÚNICO SIMPLIFICADO
' ======================
Sub GerarRelatorioAuto()
    ' Esta é a função que você vai chamar do botão
    
    Dim resultado As VbMsgBoxResult
    
    ' Explicar ao usuário
    resultado = MsgBox("Este script vai:" & vbCrLf & vbCrLf & _
                      "1. Baixar o template do SharePoint automaticamente" & vbCrLf & _
                      "2. Extrair a revisão do nome do arquivo" & vbCrLf & _
                      "3. Preencher a tabela de modificações" & vbCrLf & _
                      "4. Gerar o relatório completo" & vbCrLf & vbCrLf & _
                      "Você precisa estar conectado à rede ONS." & vbCrLf & _
                      "Deseja continuar?", _
                      vbQuestion + vbYesNo, "Gerar Relatório Automático")
    
    If resultado = vbYes Then
        ' Verificar se está no domínio ONS
        If VerificarConexaoSharepoint() Then
            ' Executar a geração
            Call GerarRelatorioPerdasDuplasETL
        Else
            MsgBox "❌ Não foi possível conectar ao SharePoint ONS." & vbCrLf & _
                   "Verifique sua conexão de rede e tente novamente.", _
                   vbExclamation, "Erro de Conexão"
        End If
    End If
End Sub

Function VerificarConexaoSharepoint() As Boolean
    ' Verificar se consegue acessar o SharePoint
    On Error Resume Next
    
    Dim xmlHttp As Object
    Set xmlHttp = CreateObject("MSXML2.XMLHTTP")
    
    xmlHttp.Open "HEAD", "https://onsbr.sharepoint.com", False
    xmlHttp.setRequestHeader "User-Agent", "Mozilla/5.0"
    xmlHttp.send
    
    If Err.Number = 0 And xmlHttp.Status = 200 Then
        VerificarConexaoSharepoint = True
        Call Log("✅ Conexão com SharePoint OK")
    Else
        VerificarConexaoSharepoint = False
        Call Log("❌ Falha na conexão com SharePoint")
    End If
End Function

' ======================
' FUNÇÕES DE LOG (SIMPLIFICADAS)
' ======================
Private Sub Log(msg As String)
    Debug.Print Format(Now, "dd/mm/yyyy hh:mm:ss") & " - " & msg
End Sub

Private Sub LogErro(erroDesc As String, Optional erroNum As Long = 0)
    Log "ERRO " & erroNum & ": " & erroDesc
End Sub

' ======================
' FUNÇÕES EXISTENTES (MANTENHA AS QUE JÁ TEM)
' ======================
Function ExtrairNumeroRevisao(nomeArquivo As String) As String
    ' Sua função existente
    ' ...
End Function

Sub CriarRelatorioComRevisao(caminhoWord As String, pagina As Long, converterPDF As Boolean, _
                            numRevisao As String, mesEmissao As String)
    ' Sua função existente
    ' ...
End Sub

' ======================
' TESTE RÁPIDO
' ======================
Sub TestarSharepoint()
    Dim linkTeste As String
    Dim linkConvertido As String
    
    linkTeste = "https://onsbr.sharepoint.com/:w:/s/soumaisons/IQCV7m4JrpKPR5ahRXRZF5cCAXDBNfb_yKAGujqO0ibWwOo?e=mMqkza"
    
    linkConvertido = ConverterParaLinkDownload(linkTeste)
    
    If linkConvertido <> "" Then
        MsgBox "Link convertido:" & vbCrLf & linkConvertido, vbInformation
    Else
        MsgBox "Não foi possível converter o link.", vbExclamation
    End If
End Sub
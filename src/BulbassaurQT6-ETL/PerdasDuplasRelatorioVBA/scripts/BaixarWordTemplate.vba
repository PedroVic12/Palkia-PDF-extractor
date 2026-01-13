Option Explicit

' ============================================
' VARIÁVEIS PÚBLICAS - Configurações
' ============================================
Public Const URL_PASTA_SHAREPOINT As String = "https://onsbr-my.sharepoint.com/shared?id=%2Fsites%2Fsoumaisons%2FOnsIntranetCentralArquivos%2FPL%2F19%20Diretrizes%20para%20Opera%C3%A7%C3%A3o%2F00%20Padroniza%C3%A7%C3%A3o&listurl=https%3A%2F%2Fonsbr%2Esharepoint%2Ecom%2Fsites%2Fsoumaisons%2FOnsIntranetCentralArquivos"
Public Const URL_WORD_TEMPLATE As String = "https://onsbr.sharepoint.com/:w:/s/soumaisons/IQCV7m4JrpKPR5ahRXRZF5cCAXDBNfb_yKAGujqO0ibWwOo?e=LCFzM5"


' ============================================
' FUNÇÃO 1 - Converter URL do SharePoint
' ============================================
Function ConverterURLSharePointParaDownload(urlOriginal As String) As String
    Debug.Print "=== PASSO 1: Convertendo URL ==="
    
    Dim urlConvertida As String
    urlConvertida = urlOriginal
    
    ' Remover parâmetros ?e=
    If InStr(urlConvertida, "?e=") > 0 Then
        urlConvertida = Left(urlConvertida, InStr(urlConvertida, "?e=") - 1)
    End If
    
    ' Adicionar parâmetro de download
    urlConvertida = urlConvertida & "?download=1"
    
    Debug.Print "URL original: " & urlOriginal
    Debug.Print "URL convertida: " & urlConvertida
    Debug.Print ""
    
    ConverterURLSharePointParaDownload = urlConvertida
End Function


' ============================================
' FUNÇÃO 2 - Obter Pasta Downloads
' ============================================
Function ObterPastaDownloads() As String
    Debug.Print "=== PASSO 2: Obtendo pasta Downloads ==="
    
    Dim caminhoDownloads As String
    
    On Error Resume Next
    caminhoDownloads = CreateObject("WScript.Shell").SpecialFolders("Downloads")
    
    If caminhoDownloads = "" Then
        caminhoDownloads = Environ("USERPROFILE") & "\Downloads"
    End If
    
    Debug.Print "Pasta Downloads: " & caminhoDownloads
    Debug.Print ""
    
    ObterPastaDownloads = caminhoDownloads
End Function


' ============================================
' FUNÇÃO 3 - Obter Credenciais
' ============================================
Function ObterCredenciais(ByRef usuario As String, ByRef senha As String) As Boolean
    Debug.Print "=== Obtendo Credenciais ==="
    
    ' Solicitar usuário
    usuario = InputBox("Digite seu e-mail corporativo:" & vbCrLf & _
                       "(ex: seu.nome@empresa.com.br)", _
                       "Autenticação SharePoint")
    
    If usuario = "" Then
        Debug.Print "Cancelado pelo usuário"
        ObterCredenciais = False
        Exit Function
    End If
    
    ' Solicitar senha
    senha = InputBox("Digite sua senha:", "Autenticação SharePoint")
    
    If senha = "" Then
        Debug.Print "Cancelado pelo usuário"
        ObterCredenciais = False
        Exit Function
    End If
    
    Debug.Print "Usuário: " & usuario
    Debug.Print "Senha: [OCULTA]"
    Debug.Print ""
    
    ObterCredenciais = True
End Function


' ============================================
' FUNÇÃO 4 - Fazer Download com Autenticação
' ============================================
Function DownloadArquivoComAuth(url As String, caminhoDestino As String, usuario As String, senha As String) As Boolean
    On Error GoTo ErrorHandler
    
    Debug.Print "=== PASSO 3: Iniciando Download ==="
    Debug.Print "URL: " & url
    Debug.Print "Destino: " & caminhoDestino
    Debug.Print "Usuário: " & usuario
    Debug.Print ""
    
    Dim http As Object
    Dim stream As Object
    
    ' Criar objeto HTTP
    Set http = CreateObject("WinHttp.WinHttpRequest.5.1")
    
    ' Abrir conexão
    http.Open "GET", url, False
    
    ' Configurar autenticação
    http.SetCredentials usuario, senha, 0  ' 0 = HTTPREQUEST_SETCREDENTIALS_FOR_SERVER
    
    ' Configurar headers
    http.SetRequestHeader "User-Agent", "Microsoft Office/16.0"
    http.SetRequestHeader "Accept", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    
    ' Tentar autenticação automática também
    http.SetAutoLogonPolicy 0
    
    Debug.Print "Enviando requisição..."
    http.Send
    
    Debug.Print "Status HTTP: " & http.Status
    Debug.Print "Status Text: " & http.StatusText
    
    On Error Resume Next
    Debug.Print "Content-Type: " & http.GetResponseHeader("Content-Type")
    Debug.Print "Content-Length: " & http.GetResponseHeader("Content-Length")
    On Error GoTo ErrorHandler
    Debug.Print ""
    
    ' Verificar resposta
    If http.Status = 200 Then
        Debug.Print "Download bem-sucedido! Salvando arquivo..."
        
        ' Salvar arquivo
        Set stream = CreateObject("ADODB.Stream")
        stream.Type = 1 ' adTypeBinary
        stream.Open
        stream.Write http.ResponseBody
        stream.SaveToFile caminhoDestino, 2 ' adSaveCreateOverWrite
        stream.Close
        
        Debug.Print "Arquivo salvo com sucesso!"
        Debug.Print "Tamanho: " & FileLen(caminhoDestino) & " bytes"
        Debug.Print ""
        
        DownloadArquivoComAuth = True
    ElseIf http.Status = 302 Or http.Status = 301 Then
        Debug.Print "AVISO: Redirecionamento detectado (Status " & http.Status & ")"
        Debug.Print "Location: " & http.GetResponseHeader("Location")
        Debug.Print ""
        DownloadArquivoComAuth = False
    ElseIf http.Status = 401 Then
        Debug.Print "ERRO: Não autorizado (401) - Credenciais inválidas"
        Debug.Print ""
        DownloadArquivoComAuth = False
    ElseIf http.Status = 403 Then
        Debug.Print "ERRO: Acesso negado (403) - Verifique permissões"
        Debug.Print "Possíveis causas:"
        Debug.Print "  1. URL de compartilhamento não permite download direto"
        Debug.Print "  2. Arquivo requer autenticação moderna (OAuth)"
        Debug.Print "  3. Necessita abrir no navegador primeiro"
        Debug.Print ""
        DownloadArquivoComAuth = False
    Else
        Debug.Print "ERRO: Status HTTP " & http.Status
        Debug.Print ""
        DownloadArquivoComAuth = False
    End If
    
    Set stream = Nothing
    Set http = Nothing
    Exit Function
    
ErrorHandler:
    Debug.Print "ERRO na função de download:"
    Debug.Print "  " & Err.Description & " (Erro #" & Err.Number & ")"
    Debug.Print ""
    DownloadArquivoComAuth = False
End Function


' ============================================
' FUNÇÃO 5 - Abrir Word
' ============================================
Sub AbrirWordTemplate(caminhoArquivo As String)
    Debug.Print "=== PASSO 4: Abrindo Word ==="
    
    On Error GoTo ErrorHandler
    
    If Dir(caminhoArquivo) = "" Then
        Debug.Print "ERRO: Arquivo não encontrado: " & caminhoArquivo
        Debug.Print ""
        Exit Sub
    End If
    
    Debug.Print "Arquivo encontrado, abrindo..."
    
    Dim wordApp As Object
    Set wordApp = CreateObject("Word.Application")
    wordApp.Visible = True
    wordApp.Documents.Open caminhoArquivo
    
    Debug.Print "Word aberto com sucesso!"
    Debug.Print ""
    
    Set wordApp = Nothing
    Exit Sub
    
ErrorHandler:
    Debug.Print "ERRO ao abrir Word: " & Err.Description
    Debug.Print ""
End Sub


' ============================================
' FUNÇÃO 6 - Obter Caminho Final
' ============================================
Function ObterCaminhoArquivoFinal() As String
    Dim pastaDownloads As String
    Dim nomeArquivo As String
    
    pastaDownloads = CreateObject("WScript.Shell").SpecialFolders("Downloads")
    If pastaDownloads = "" Then
        pastaDownloads = Environ("USERPROFILE") & "\Downloads"
    End If
    
    nomeArquivo = "Template_Relatorio.docx"
    
    ObterCaminhoArquivoFinal = pastaDownloads & "\" & nomeArquivo
End Function


' ============================================
' PROCEDIMENTO PRINCIPAL - Baixar Template
' ============================================
Sub BaixarWordTemplate()
    On Error GoTo ErrorHandler
    
    Debug.Print "========================================="
    Debug.Print "INÍCIO DO PROCESSO DE DOWNLOAD"
    Debug.Print "========================================="
    Debug.Print ""
    
    Dim urlDownload As String
    Dim caminhoLocal As String
    Dim nomeArquivo As String
    Dim pastaDownloads As String
    Dim usuario As String
    Dim senha As String
    Dim sucesso As Boolean
    
    nomeArquivo = "Template_Relatorio.docx"
    
    ' 1. Obter credenciais
    If Not ObterCredenciais(usuario, senha) Then
        Debug.Print "Download cancelado pelo usuário"
        Exit Sub
    End If
    
    ' 2. Converter URL
    urlDownload = ConverterURLSharePointParaDownload(URL_WORD_TEMPLATE)
    
    ' 3. Obter pasta Downloads
    pastaDownloads = ObterPastaDownloads()
    caminhoLocal = pastaDownloads & "\" & nomeArquivo
    
    ' 4. Fazer download
    sucesso = DownloadArquivoComAuth(urlDownload, caminhoLocal, usuario, senha)
    
    If Not sucesso Then
        Debug.Print "========================================="
        Debug.Print "DOWNLOAD FALHOU!"
        Debug.Print "========================================="
        Debug.Print ""
    Else
        Debug.Print "========================================="
        Debug.Print "DOWNLOAD CONCLUÍDO COM SUCESSO!"
        Debug.Print "========================================="
        Debug.Print ""
    End If
    
    Exit Sub
    
ErrorHandler:
    Debug.Print "ERRO GERAL: " & Err.Description & " (Erro #" & Err.Number & ")"
    Debug.Print ""
End Sub


' ============================================
' SUB TESTAR - Executar todas as funções
' ============================================
Sub Testar()
    Dim caminhoArquivo As String
    
    ' Passo 1: Baixar template
    Call BaixarWordTemplate
    
    ' Passo 2: Obter caminho
    caminhoArquivo = ObterCaminhoArquivoFinal()
    
    ' Passo 3: Abrir Word
    Call AbrirWordTemplate(caminhoArquivo)
    
    Debug.Print "========================================="
    Debug.Print "PROCESSO FINALIZADO"
    Debug.Print "========================================="
End Sub

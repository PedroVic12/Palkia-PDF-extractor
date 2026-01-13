Option Explicit

' ==============================================================================
' MÓDULO: Download SharePoint Online (Método Nativo Office)
' AUTOR: Gemini
' DESCRIÇÃO: Usa o Word para abrir o link e salvar uma cópia local.
'            Resolve problemas de autenticação moderna/MFA.
' ==============================================================================

' ## Sprint Atual 13/01/26 (Requisitos atuais)
' - [x] VBA Perdas duplas
' - [x] Auth do sharepoint correto e baixar para pasta /downloads
' - [x] Data Atual correta no nome do arquivo (word_template_yy_mm_dd.docx)

' ============================================
' CONFIGURAÇÕES GLOBAIS
' ============================================
Public Const URL_ARQUIVO_SHAREPOINT As String = "https://onsbr.sharepoint.com/sites/soumaisons/OnsIntranetCentralArquivos/PL/19%20Diretrizes%20para%20Opera%C3%A7%C3%A3o/00%20Padroniza%C3%A7%C3%A3o/Lista%20de%20Conting%C3%AAncias%20Duplas%20Analisadas_Modelo.docx"

' ============================================
' ROTINA PRINCIPAL 
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

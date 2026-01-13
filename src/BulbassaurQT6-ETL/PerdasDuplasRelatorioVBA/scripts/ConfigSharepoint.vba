Option Explicit

' ============================================
' VARIÁVEIS PÚBLICAS - Configurações
' ============================================
Public Const URL_PASTA_SHAREPOINT As String = "https://onsbr-my.sharepoint.com/shared?id=%2Fsites%2Fsoumaisons%2FOnsIntranetCentralArquivos%2FPL%2F19%20Diretrizes%20para%20Opera%C3%A7%C3%A3o%2F00%20Padroniza%C3%A7%C3%A3o"
Public Const URL_WORD_TEMPLATE As String = "https://onsbr.sharepoint.com/:w:/s/soumaisons/IQCV7m4JrpKPR5ahRXRZF5cCAXDBNfb_yKAGujqO0ibWwOo"


' ============================================
' FUNÇÃO 1 - Encontrar Pasta OneDrive
' ============================================
Function EncontrarPastaOneDrive() As String
    Debug.Print "=== PASSO 1: Procurando pasta OneDrive ==="
    
    Dim caminhoOneDrive As String
    Dim shell As Object
    Set shell = CreateObject("WScript.Shell")
    
    ' Tentar diferentes variáveis de ambiente
    On Error Resume Next
    
    ' Opção 1: OneDrive Comercial
    caminhoOneDrive = Environ("OneDriveCommercial")
    If caminhoOneDrive <> "" Then
        Debug.Print "OneDrive encontrado (Comercial): " & caminhoOneDrive
        EncontrarPastaOneDrive = caminhoOneDrive
        Exit Function
    End If
    
    ' Opção 2: OneDrive padrão
    caminhoOneDrive = Environ("OneDrive")
    If caminhoOneDrive <> "" Then
        Debug.Print "OneDrive encontrado: " & caminhoOneDrive
        EncontrarPastaOneDrive = caminhoOneDrive
        Exit Function
    End If
    
    ' Opção 3: Ler do registro
    caminhoOneDrive = shell.RegRead("HKEY_CURRENT_USER\Software\Microsoft\OneDrive\Accounts\Business1\UserFolder")
    If caminhoOneDrive <> "" Then
        Debug.Print "OneDrive encontrado (Registro): " & caminhoOneDrive
        EncontrarPastaOneDrive = caminhoOneDrive
        Exit Function
    End If
    
    ' Opção 4: Caminho padrão
    caminhoOneDrive = Environ("USERPROFILE") & "\OneDrive - ONS"
    If Dir(caminhoOneDrive, vbDirectory) <> "" Then
        Debug.Print "OneDrive encontrado (Padrão): " & caminhoOneDrive
        EncontrarPastaOneDrive = caminhoOneDrive
        Exit Function
    End If
    
    Debug.Print "AVISO: OneDrive não encontrado!"
    Debug.Print ""
    EncontrarPastaOneDrive = ""
End Function


' ============================================
' FUNÇÃO 2 - Listar Pastas OneDrive
' ============================================
Sub ListarPastasOneDrive()
    Debug.Print "=== Listando pastas OneDrive disponíveis ==="
    
    Dim basePath As String
    Dim fso As Object
    Dim folder As Object
    Dim subfolder As Object
    
    basePath = Environ("USERPROFILE")
    Set fso = CreateObject("Scripting.FileSystemObject")
    
    If Not fso.FolderExists(basePath) Then
        Debug.Print "Pasta não encontrada: " & basePath
        Exit Sub
    End If
    
    Set folder = fso.GetFolder(basePath)
    
    Debug.Print "Procurando em: " & basePath
    Debug.Print ""
    
    For Each subfolder In folder.SubFolders
        If InStr(LCase(subfolder.Name), "onedrive") > 0 Then
            Debug.Print "  ✓ " & subfolder.Name
            Debug.Print "    Caminho: " & subfolder.Path
            Debug.Print ""
        End If
    Next subfolder
    
    Set fso = Nothing
End Sub


' ============================================
' FUNÇÃO 3 - Buscar Arquivo no OneDrive
' ============================================
Function BuscarArquivoOneDrive(nomeArquivo As String) As String
    Debug.Print "=== PASSO 2: Buscando arquivo no OneDrive ==="
    Debug.Print "Arquivo procurado: " & nomeArquivo
    Debug.Print ""
    
    Dim caminhoOneDrive As String
    Dim caminhoCompleto As String
    Dim fso As Object
    
    Set fso = CreateObject("Scripting.FileSystemObject")
    
    ' Tentar encontrar OneDrive
    caminhoOneDrive = EncontrarPastaOneDrive()
    
    If caminhoOneDrive = "" Then
        Debug.Print "ERRO: Não foi possível encontrar o OneDrive"
        Debug.Print "Execute: ListarPastasOneDrive para ver as pastas disponíveis"
        BuscarArquivoOneDrive = ""
        Exit Function
    End If
    
    ' Tentar diferentes caminhos possíveis
    Dim caminhosPossiveis As Variant
    Dim i As Integer
    
    caminhosPossiveis = Array( _
        caminhoOneDrive & "\" & nomeArquivo, _
        caminhoOneDrive & "\Documents\" & nomeArquivo, _
        caminhoOneDrive & "\Documentos Compartilhados\" & nomeArquivo, _
        caminhoOneDrive & "\OnsIntranetCentralArquivos\" & nomeArquivo, _
        caminhoOneDrive & "\OnsIntranetCentralArquivos\PL\19 Diretrizes para Operação\00 Padronização\" & nomeArquivo _
    )
    
    For i = LBound(caminhosPossiveis) To UBound(caminhosPossiveis)
        caminhoCompleto = caminhosPossiveis(i)
        
        Debug.Print "Tentando: " & caminhoCompleto
        
        If fso.FileExists(caminhoCompleto) Then
            Debug.Print "✓ ARQUIVO ENCONTRADO!"
            Debug.Print ""
            BuscarArquivoOneDrive = caminhoCompleto
            Exit Function
        End If
    Next i
    
    Debug.Print "✗ Arquivo não encontrado em nenhum caminho"
    Debug.Print ""
    BuscarArquivoOneDrive = ""
    
    Set fso = Nothing
End Function


' ============================================
' FUNÇÃO 4 - Copiar Arquivo para Downloads
' ============================================
Function CopiarArquivoParaDownloads(caminhoOrigem As String) As String
    Debug.Print "=== PASSO 3: Copiando arquivo ==="
    
    Dim fso As Object
    Dim pastaDownloads As String
    Dim nomeArquivo As String
    Dim caminhoDestino As String
    
    Set fso = CreateObject("Scripting.FileSystemObject")
    
    ' Obter pasta Downloads
    pastaDownloads = CreateObject("WScript.Shell").SpecialFolders("Downloads")
    If pastaDownloads = "" Then
        pastaDownloads = Environ("USERPROFILE") & "\Downloads"
    End If
    
    ' Obter nome do arquivo
    nomeArquivo = fso.GetFileName(caminhoOrigem)
    caminhoDestino = pastaDownloads & "\" & nomeArquivo
    
    Debug.Print "Origem: " & caminhoOrigem
    Debug.Print "Destino: " & caminhoDestino
    
    ' Copiar arquivo
    On Error GoTo ErrorHandler
    fso.CopyFile caminhoOrigem, caminhoDestino, True ' True = sobrescrever
    
    Debug.Print "✓ Arquivo copiado com sucesso!"
    Debug.Print "Tamanho: " & FileLen(caminhoDestino) & " bytes"
    Debug.Print ""
    
    CopiarArquivoParaDownloads = caminhoDestino
    Set fso = Nothing
    Exit Function
    
ErrorHandler:
    Debug.Print "✗ ERRO ao copiar: " & Err.Description
    Debug.Print ""
    CopiarArquivoParaDownloads = ""
End Function


' ============================================
' FUNÇÃO 5 - Abrir Word
' ============================================
Sub AbrirWordTemplate(caminhoArquivo As String)
    Debug.Print "=== PASSO 4: Abrindo Word ==="
    
    On Error GoTo ErrorHandler
    
    If Dir(caminhoArquivo) = "" Then
        Debug.Print "✗ ERRO: Arquivo não encontrado: " & caminhoArquivo
        Debug.Print ""
        Exit Sub
    End If
    
    Debug.Print "Abrindo: " & caminhoArquivo
    
    Dim wordApp As Object
    Set wordApp = CreateObject("Word.Application")
    wordApp.Visible = True
    wordApp.Documents.Open caminhoArquivo
    
    Debug.Print "✓ Word aberto com sucesso!"
    Debug.Print ""
    
    Set wordApp = Nothing
    Exit Sub
    
ErrorHandler:
    Debug.Print "✗ ERRO ao abrir Word: " & Err.Description
    Debug.Print ""
End Sub


' ============================================
' FUNÇÃO 6 - Buscar Arquivo Manualmente
' ============================================
Function SelecionarArquivoManualmente() As String
    Debug.Print "=== Seleção Manual de Arquivo ==="
    
    Dim fd As FileDialog
    Set fd = Application.FileDialog(msoFileDialogFilePicker)
    
    With fd
        .Title = "Selecione o Template do Word"
        .Filters.Clear
        .Filters.Add "Documentos Word", "*.docx;*.doc"
        .AllowMultiSelect = False
        .InitialFileName = Environ("USERPROFILE") & "\OneDrive*\"
        
        If .Show = -1 Then
            SelecionarArquivoManualmente = .SelectedItems(1)
            Debug.Print "Arquivo selecionado: " & .SelectedItems(1)
        Else
            SelecionarArquivoManualmente = ""
            Debug.Print "Seleção cancelada"
        End If
    End With
    
    Debug.Print ""
End Function


' ============================================
' PROCEDIMENTO PRINCIPAL
' ============================================
Sub BaixarWordTemplate()
    Debug.Print "========================================="
    Debug.Print "INÍCIO DO PROCESSO"
    Debug.Print "========================================="
    Debug.Print ""
    
    Dim caminhoArquivo As String
    Dim caminhoDownloads As String
    Dim nomeArquivo As String
    
    nomeArquivo = "Template_Relatorio.docx"
    
    ' Tentar buscar automaticamente
    caminhoArquivo = BuscarArquivoOneDrive(nomeArquivo)
    
    ' Se não encontrou, permitir seleção manual
    If caminhoArquivo = "" Then
        Debug.Print "========================================="
        Debug.Print "ARQUIVO NÃO ENCONTRADO AUTOMATICAMENTE"
        Debug.Print "========================================="
        Debug.Print ""
        Debug.Print "Opções:"
        Debug.Print "1. Execute 'ListarPastasOneDrive' para ver suas pastas"
        Debug.Print "2. Execute 'SelecionarArquivoManualmente' para escolher o arquivo"
        Debug.Print "3. Sincronize a pasta do SharePoint com OneDrive primeiro"
        Debug.Print ""
        
        ' Tentar seleção manual
        caminhoArquivo = SelecionarArquivoManualmente()
        
        If caminhoArquivo = "" Then
            Debug.Print "Processo cancelado."
            Exit Sub
        End If
    End If
    
    ' Copiar para Downloads
    caminhoDownloads = CopiarArquivoParaDownloads(caminhoArquivo)
    
    If caminhoDownloads = "" Then
        Debug.Print "========================================="
        Debug.Print "PROCESSO FALHOU"
        Debug.Print "========================================="
        Exit Sub
    End If
    
    Debug.Print "========================================="
    Debug.Print "PROCESSO CONCLUÍDO COM SUCESSO!"
    Debug.Print "========================================="
    Debug.Print ""
End Sub


' ============================================
' SUB TESTAR
' ============================================
Sub Testar()
    Dim caminhoArquivo As String
    
    ' Passo 1: Listar pastas OneDrive disponíveis
    Call ListarPastasOneDrive
    
    ' Passo 2: Buscar e copiar template
    Call BaixarWordTemplate
    
    ' Passo 3: Obter caminho final
    Dim pastaDownloads As String
    pastaDownloads = CreateObject("WScript.Shell").SpecialFolders("Downloads")
    If pastaDownloads = "" Then pastaDownloads = Environ("USERPROFILE") & "\Downloads"
    
    caminhoArquivo = pastaDownloads & "\Template_Relatorio.docx"
    
    ' Passo 4: Abrir Word
    Call AbrirWordTemplate(caminhoArquivo)
    
    Debug.Print "========================================="
    Debug.Print "PROCESSO FINALIZADO"
    Debug.Print "========================================="
End Sub
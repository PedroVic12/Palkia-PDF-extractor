Sub ConfigurarAcessoSharepoint()
    ' 1. Abra o link no navegador e faça login
    ' 2. Baixe o template manualmente
    ' 3. Execute esta macro para configurar o caminho
    
    Dim caminho As String
    caminho = Application.GetOpenFilename( _
        FileFilter:="Word Files (*.docx), *.docx", _
        Title:="Selecione o template baixado do Sharepoint")
    
    If caminho <> "False" Then
        ' Salvar no caminho padrão
        FileCopy caminho, LOCAL_TEMPLATE_PATH
        MsgBox "Template configurado com sucesso!", vbInformation
    End If
End Sub
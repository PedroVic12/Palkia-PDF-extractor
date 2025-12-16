Sub RodarScriptAguardarConclusao()
    Dim wsh As Object
    Dim scriptPath As String
    Dim pythonExe As String
    Dim command As String
    Dim exitCode As Integer
    
    ' 1. Configurações
    ' Pega o caminho do script na célula A1 da Sheet1
    scriptPath = Sheets("Sheet1").Range("A1").Value
    
    ' (Opcional) Pega o caminho do Python na célula A2, ou usa padrão
    On Error Resume Next
    pythonExe = Sheets("Sheet1").Range("A2").Value
    On Error GoTo 0
    
    If pythonExe = "" Then pythonExe = "python" ' Usa o python do PATH se A2 estiver vazio
    
    ' 2. Validações
    If scriptPath = "" Then
        MsgBox "A célula A1 está vazia! Coloque o caminho do script .py", vbExclamation
        Exit Sub
    End If
    
    If Dir(scriptPath) = "" Then
        MsgBox "Arquivo não encontrado:" & vbCrLf & scriptPath, vbCritical
        Exit Sub
    End If
    
    ' 3. Monta o comando
    ' Aspas triplas para lidar com espaços nos nomes de pastas
    command = """" & pythonExe & """ """ & scriptPath & """"
    
    ' 4. Executa e ESPERA (WaitOnReturn = True)
    Set wsh = CreateObject("WScript.Shell")
    
    ' O parametro '1' mostra a janela preta. Use '0' para esconder.
    ' O 'True' no final é o segredo: trava o Excel até o Python acabar.
    exitCode = wsh.Run(command, 1, True)
    
    ' 5. Feedback
    If exitCode = 0 Then
        MsgBox "✅ Processo finalizado com sucesso!", vbInformation, "Python Concluído"
    Else
        MsgBox "❌ O script retornou um erro ou foi interrompido.", vbCritical, "Erro"
    End If
    
    Set wsh = Nothing
End Sub
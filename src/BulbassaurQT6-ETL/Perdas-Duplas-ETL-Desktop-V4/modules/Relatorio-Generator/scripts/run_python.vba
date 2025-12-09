Sub run_python_script()
    ' Objeto para executar comandos do sistema
    Dim vbaPython As Object
    Set vbaPython = VBA.CreateObject("Wscript.Shell")
    
    ' TODO: Usar "where python" no cmd para encontrar o caminho do Python instalado
    ' Exemplo: C:\Users\[usuario]\AppData\Local\Programs\Python\Python313\python.exe
    Dim pythonPath As String
    pythonPath = "C:\Users\pedrovictor.veras\AppData\Local\Programs\Python\Python313\python.exe"
    
    ' TODO: Apontar o caminho completo do script Python que deseja executar
    ' Verificar no aqruivo de CLI.py os scripts disponiveis para executar
    Dim scriptPath As String
    scriptPath = "C:\Users\pedrovictor.veras\OneDrive - Operador Nacional do Sistema Eletrico\Documentos\ESTAGIO_ONS_PVRV_2025\GitHub\Palkia-PDF-extractor\src\BulbassaurQT6-ETL\Relatorio_PLC_Automate\scripts\gerar_relatorio_perdas_duplas.py"
    
    ' Executa o script Python
    vbaPython.Run """" & pythonPath & """ """ & scriptPath & """"

End Sub
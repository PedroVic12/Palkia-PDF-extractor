Sub run_python_script()
    Dim vbaPython As Object
    set vbaPython = VBA.CreateObject("Wscript.Shell")
    vbaPython.run """C:\Users\pedrovictor.veras\AppData\Local\Programs\Python\Python313\python.exe""" & _
    """C:\Users\pedrovictor.veras\OneDrive - Operador Nacional do Sistema Eletrico\Documentos\ESTAGIO_ONS_PVRV_2025\GitHub\Palkia-PDF-extractor\src\BulbassaurQT6-ETL\Perdas-Duplas-ETL-Desktop-V4\modules\Relatorio_ONS_Automate\controllers\graficos_LTs_perdas_duplas.py"""

End Sub
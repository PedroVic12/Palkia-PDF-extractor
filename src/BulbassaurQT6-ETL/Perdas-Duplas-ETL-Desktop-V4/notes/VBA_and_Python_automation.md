# **VBA vs Python - Análise Comparativa**

## **PARALELO ENTRE PYTHON E VBA**

### **1. ABRIR/CARREGAR ARQUIVOS**

**Python (openpyxl/docx):**
```python
# Excel
from openpyxl import load_workbook
wb = load_workbook('arquivo.xlsx')
ws = wb['Contingências Duplas']

# Word
from docx import Document
doc = Document('template.docx')
```

**VBA (equivalente):**
```vba
' Excel (trabalha no Excel aberto)
Set ws = ThisWorkbook.Worksheets("Contingências Duplas")

' Word (abre Word)
Set wordApp = CreateObject("Word.Application")
Set wordDoc = wordApp.Documents.Open(caminhoWord)
```

**Tradução:**  
`CreateObject("Word.Application")` ≈ `import win32com.client` em Python

---

### **2. LER DADOS DA PLANILHA**

**Python (pandas/openpyxl):**
```python
# Com pandas
import pandas as pd
df = pd.read_excel('arquivo.xlsx', sheet_name='Contingências Duplas')
ultima_linha = df.shape[0]
ultima_coluna = df.shape[1]

# Com openpyxl
ws = wb.active
ultima_linha = ws.max_row
ultima_coluna = ws.max_column
```

**VBA (equivalente):**
```vba
' Encontrar última linha e coluna
ultimaLinha = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
ultimaColuna = ws.Cells(1, ws.Columns.Count).End(xlToLeft).Column

' Acessar célula específica
valor = ws.Cells(i, j).Value  # Similar a df.iloc[i-1, j-1]
```

**Tradução:**  
- `ws.Cells(i, j)` ≈ `ws.cell(row=i, column=j)` em openpyxl
- `.End(xlUp)` ≈ `.max_row` mas com lógica de Excel (Ctrl+↑)

---

### **3. TRABALHAR COM WORD**

**Python (python-docx):**
```python
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Criar tabela
tabela = doc.add_table(rows=ultima_linha, cols=ultima_coluna)

# Acessar célula
celula = tabela.cell(i-1, j-1)  # Índice 0-based
celula.text = valor

# Formatar
run = celula.paragraphs[0].runs[0]
run.font.bold = True
run.font.color.rgb = RGBColor(0, 0, 255)
```

**VBA (equivalente):**
```vba
' Criar tabela
Set tabela = wordDoc.Tables.Add(wordApp.Selection.Range, ultimaLinha, ultimaColuna)

' Acessar célula (1-based)
tabela.Cell(i, j).Range.Text = valor

' Formatar
With tabela.Cell(i, j).Range
    .Bold = True
    .Font.Color = RGB(0, 0, 255)
End With
```

**Tradução:**  
- `tabela.Cell(i, j)` ≈ `tabela.cell(i-1, j-1)` (VBA é 1-based)
- `.Range.Text` ≈ `.text` em python-docx

---

### **4. CONSTANTES E CONFIGURAÇÕES**

**Python:**
```python
# No topo do arquivo
CABECALHO_AZUL = True
DEBUG_MODE = False
FONTE_CABECALHO = "Calibri"
TAMANHO_CABECALHO = 14

# Em classe/config
class Config:
    CABECALHO_AZUL = True
    FONTE = "Calibri"
```

**VBA:**
```vba
' No topo do módulo
Public Const CABECALHO_AZUL As Boolean = True
Public Const DEBUG_MODE As Boolean = False
Public Const FONTE_CABECALHO As String = "Calibri"
Public Const TAMANHO_CABECALHO As Integer = 14
```

**Tradução:**  
- `Public Const` ≈ `CONSTANTE` global em Python
- Tipos explícitos (`As Boolean`, `As String`)

---

### **5. CLASSES E MÉTODOS**

**Python:**
```python
class Logger:
    def __init__(self, debug_mode=False):
        self.debug_mode = debug_mode
    
    def log(self, msg):
        print(f"{datetime.now()} - {msg}")
        if self.debug_mode:
            print(f"[DEBUG] {msg}")

# Usar
logger = Logger(debug_mode=True)
logger.log("Mensagem")
```

**VBA:**
```vba
' Classe clsLogger
Private pDebugMode As Boolean

Public Property Get DebugMode() As Boolean
    DebugMode = pDebugMode
End Property

Public Property Let DebugMode(ByVal valor As Boolean)
    pDebugMode = valor
End Property

Public Sub Log(msg As String)
    Debug.Print Format(Now, "dd/mm/yyyy hh:mm:ss") & " - " & msg
    If pDebugMode Then MsgBox msg
End Sub

' Usar
Dim logger As New clsLogger
logger.DebugMode = True
logger.Log "Mensagem"
```

**Tradução:**  
- `Property Get/Let` ≈ `@property` em Python
- `New clsLogger` ≈ `Logger()` instanciação

---

### **6. LAÇOS E ITERAÇÕES**

**Python:**
```python
for i in range(1, ultima_linha + 1):
    for j in range(1, ultima_coluna + 1):
        valor = ws.cell(i, j).value
        # processar
```

**VBA:**
```vba
For i = 1 To ultimaLinha
    For j = 1 To ultimaColuna
        valor = ws.Cells(i, j).Value
        ' processar
    Next j
Next i
```

**Tradução:**  
- `For i = 1 To N` ≈ `for i in range(1, N+1)`
- `Next i` ≈ `}` do for

---

### **7. TRATAMENTO DE ERROS**

**Python:**
```python
try:
    # código que pode falhar
    doc.save('arquivo.docx')
except Exception as e:
    print(f"Erro: {e}")
    # limpeza
finally:
    # código de limpeza
```

**VBA:**
```vba
On Error GoTo ErroHandler
    ' código que pode falhar
    wordDoc.SaveAs2 caminhoSalvar
    Exit Sub
    
ErroHandler:
    MsgBox "Erro: " & Err.Description
    ' limpeza
    Resume Limpeza
```

**Tradução:**  
- `On Error GoTo` ≈ `try/except`
- `Err.Description` ≈ `str(e)`

---

## **MAPA DETALHADO DO CÓDIGO VBA**

### **PARTE 1: ESTRUTURA DO PROGRAMA**

```vba
' ===== Python equivalente =====
' if __name__ == "__main__":
'     main()

Sub GerarRelatorioPerdasDuplasETL()  ' <-- Função principal
    ' ... código ...
End Sub
```

### **PARTE 2: VARIÁVEIS E CONSTANTES**

```vba
' Python: CONSTANTES_GLOBAIS = {...}
Public Const CABECALHO_AZUL As Boolean = True
Public Const FONTE_CABECALHO As String = "Calibri"
' ... outras constantes ...
```

### **PARTE 3: MÉTODOS PRINCIPAIS**

```vba
' ===== Método 1: Função principal =====
' Python: def criar_relatorio(template_word, pagina, converter_pdf):
Sub CriarRelatorioCorrigido(caminhoWord As String, pagina As Long, converterPDF As Boolean)
    ' ... implementação ...
End Sub

' ===== Método 2: Função auxiliar =====
' Python: def formatar_celula_horizonte(celula, valor):
Private Sub FormatarCelulaHorizonte(celula As Object, valor As String)
    ' ... implementação ...
End Sub
```

### **PARTE 4: SISTEMA DE LOG**

```vba
' Python: def log(msg, debug=False):
Private Sub Log(msg As String)
    Debug.Print Format(Now, "dd/mm/yyyy hh:mm:ss") & " - " & msg
    If DEBUG_MODE Then MsgBox msg
End Sub
```

---

## **ANÁLISE DAS SEÇÕES DO CÓDIGO**

### **SEÇÃO 1: Inicialização**
```vba
' Abrir Word (equivalente a Document() em Python)
Set wordApp = CreateObject("Word.Application")
Set wordDoc = wordApp.Documents.Open(caminhoWord)
' wordApp.Visible = True  <-- Como doc.show() em algumas libs
```

### **SEÇÃO 2: Construir Tabela**
```vba
' Criar tabela vazia
Set tabela = wordDoc.Tables.Add(wordApp.Selection.Range, linhas, colunas)

' Similar a Python:
' tabela = doc.add_table(rows=linhas, cols=colunas)
```

### **SEÇÃO 3: Formatação**
```vba
' Formatar bordas (equivalente a python-docx TableStyle)
With tabela.Borders
    .InsideLineStyle = 1  ' wdLineStyleSingle
    .InsideLineWidth = ESPESSURA_BORDA
End With

' Configurar colunas
tabela.Columns(j).Width = larguraCm * 28.35
' 28.35 pontos = 1 cm (unidade do Word)
```

### **SEÇÃO 4: Preenchimento**
```vba
' Preencher células
For i = 1 To ultimaLinha
    For j = 1 To ultimaColuna
        tabela.Cell(i, j).Range.Text = ws.Cells(i, j).Text
    Next j
Next i
```

### **SEÇÃO 5: Salvar/Exportar**
```vba
' Salvar como DOCX
wordDoc.SaveAs2 caminhoSalvar

' Converter para PDF (código 17 = PDF)
wordDoc.SaveAs2 pdfPath, 17
```

---

## **EXEMPLO COMPARATIVO COMPLETO**

### **Em Python (como você faria):**
```python
from docx import Document
from docx.shared import Inches, Pt, RGBColor
import pandas as pd

class RelatorioPerdas:
    def __init__(self, debug=False):
        self.debug = debug
        self.cabecalho_azul = True
        self.fonte_cabecalho = "Calibri"
    
    def log(self, msg):
        print(f"[LOG] {msg}")
        if self.debug:
            print(f"[DEBUG] {msg}")
    
    def criar_tabela(self, df, doc):
        # Criar tabela
        tabela = doc.add_table(rows=df.shape[0]+1, cols=df.shape[1])
        
        # Preencher cabeçalho
        for j, coluna in enumerate(df.columns):
            celula = tabela.cell(0, j)
            celula.text = coluna
            
            # Formatar (equivalente ao VBA)
            if self.cabecalho_azul:
                for paragraph in celula.paragraphs:
                    for run in paragraph.runs:
                        run.font.color.rgb = RGBColor(255, 255, 255)
        
        # Preencher dados
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                tabela.cell(i+1, j).text = str(df.iloc[i, j])
        
        return tabela

# Uso
relatorio = RelatorioPerdas(debug=True)
df = pd.read_excel("dados.xlsx")
doc = Document("template.docx")
tabela = relatorio.criar_tabela(df, doc)
doc.save("relatorio.docx")
```

### **Em VBA (o que temos):**
```vba
' Instanciar e configurar
' (Não precisa de "new RelatorioPerdas" porque é procedural)

' Ler dados (já no Excel)
ultimaLinha = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row

' Criar documento
Set wordDoc = wordApp.Documents.Open(caminhoWord)

' Criar tabela
Set tabela = wordDoc.Tables.Add(wordApp.Selection.Range, ultimaLinha, ultimaColuna)

' Formatar e preencher (diretamente no objeto)
tabela.Cell(1, 1).Range.Text = "Cabeçalho"
If CABECALHO_AZUL Then
    tabela.Cell(1, 1).Range.Font.Color = RGB(255, 255, 255)
End If

' Salvar
wordDoc.SaveAs2 caminhoSalvar
```

---

## **CONCEITOS-CHAVE PARA ENTENDER:**

1. **Objetos COM vs Bibliotecas Python**
   - VBA usa objetos COM do Office (`Word.Application`, `Excel.Worksheet`)
   - Python usa bibliotecas externas (`openpyxl`, `python-docx`)

2. **1-based vs 0-based Indexing**
   - VBA: Tudo começa em 1 (`Cells(1, 1)`)
   - Python: Tudo começa em 0 (`cell(0, 0)`)

3. **Propriedades vs Métodos**
   - VBA: `.Range.Text` (propriedade para definir texto)
   - Python: `.text = valor` (atribuição direta)

4. **Eventos e Handlers**
   - VBA: `On Error GoTo ErroHandler` (manipulação estruturada)
   - Python: `try/except/finally` (exceções)

5. **Tipagem**
   - VBA: Tipagem explícita (`As String`, `As Long`)
   - Python: Tipagem dinâmica

## **DICAS PARA APRENDER VBA VINDO DO PYTHON:**

1. **Pense em objetos do Office como classes Python**
   - `Worksheet` ≈ `Workbook.active` no openpyxl
   - `Table` ≈ `doc.add_table()` no python-docx

2. **Use o gravador de macros**
   - Grava ações em VBA → Ótimo para aprender sintaxe

3. **Debug similar**
   - `Debug.Print` ≈ `print()` em Python
   - `MsgBox` ≈ `print()` + pausa

4. **Referências de objeto**
   - `Set obj = NovoObjeto` ≈ `obj = Class()` em Python
   - `Set obj = Nothing` ≈ `del obj` ou `obj = None`

5. **Arrays/coleções**
   - VBA: `Dim arr(1 To 10) As String`
   - Python: `arr = [""] * 10`

O código VBA que você tem agora é funcionalmente equivalente ao que você faria em Python, apenas com a sintaxe e padrões do Office/VBA.
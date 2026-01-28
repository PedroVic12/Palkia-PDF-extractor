# 🚀 Guia Rápido - script_inicial_anaRede.py

## 📌 O que foi feito

Unifiquei **TODO** o seu código original com o sistema CLI Rich, mantendo:
- ✅ **TODOS os nomes originais** das classes e funções
- ✅ `Configuracoes` (com showToast)
- ✅ `C3POGeminiAssistant` (com falar, abrir_programa)
- ✅ `AnaRedeDeckBuilder` (com carregar_save_case, carregar_diagrama, diagnosticar_posicao_mouse)
- ✅ `anaRedeScript()` - função original
- ✅ `OrganonScript()` - função original
- ✅ `run_automation()` - função original

**NOVO:**
- ✅ Nova variável `caminho_decks_anaRede` na classe Configuracoes
- ✅ CLI interativa com Rich
- ✅ Explorador de arquivos com árvore visual
- ✅ Rastreamento avançado de mouse
- ✅ Sistema de seleção de casos/diagramas
- ✅ Atalhos EditCepel documentados

## 🎯 Estrutura do Menu

```
╔═══════════════════════════════════════════════╗
║   ⚡ AUTOMAÇÃO SEP - AnaREDE & Organon      ║
╚═══════════════════════════════════════════════╝

┌───────┬─────────────────────────────────────────────┐
│ Opção │ Descrição                                   │
├───────┼─────────────────────────────────────────────┤
│   1   │ 📂 Explorar arquivos (Tree)                │
│   2   │ 📋 Selecionar casos/diagramas              │
│   3   │ ▶️  Executar anaRedeScript                 │
│   4   │ ▶️  Executar OrganonScript                 │
│   5   │ 🔄 Executar run_automation (completo)      │
│   6   │ ⌨️  Atalhos EditCepel                      │
│   7   │ 🖱️  Rastrear posição do mouse              │
│   8   │ 📍 Diagnosticar posição (original)         │
│   9   │ 🔊 Toggle voz                              │
│   0   │ 🚪 Sair                                     │
└───────┴─────────────────────────────────────────────┘
```

## 🛠️ Instalação

```bash
# 1. Instalar dependências
pip install -r requirements_script_inicial.txt

# 2. Ajustar o caminho (IMPORTANTE!)
# Edite o script_inicial_anaRede.py linha ~75
caminho_decks_anaRede = r"C:\Users\...\SIN"
```

## 🚦 Como Usar

### 1️⃣ Primeiro Uso - Calibrar Coordenadas

```bash
python script_inicial_anaRede.py
```

No menu, escolha:
- **Opção 7**: Rastrear posição do mouse (10 segundos)
- Mova o mouse sobre os botões do AnaREDE
- Anote as coordenadas X, Y
- Atualize a classe `AnaRedeDeckBuilder` no código:

```python
self.coordenadas = {
    'menu_caso': (50, 35),      # ← Suas coordenadas aqui
    'abrir_caso': (100, 70),    # ← Suas coordenadas aqui
    'salvar_caso': (100, 95),
    ...
}
```

### 2️⃣ Workflow Normal

```bash
python script_inicial_anaRede.py

# Menu → Opção 2: Selecionar casos
# Escolher arquivo .SAV
# Escolher diagrama .LST

# Menu → Opção 3: Executar anaRedeScript
# OU
# Menu → Opção 5: Executar run_automation (completo)
```

## 📂 Estrutura de Diretórios Esperada

```
C:\Users\...\SIN\
├── Casos de Uso - SEP ONS/
├── decks/
│   ├── caso1.pwf
│   └── caso2.dat
├── diagramas/
│   ├── SIN.lst
│   └── NE.lst
├── planilhas/
└── Sav/
    └── 3Q2025_estudo_v1.SAV
```

## 🎯 Funções Originais Mantidas

### anaRedeScript()
```python
# O que faz:
# 1. Abre AnaREDE 12
# 2. Carrega arquivo .SAV selecionado
```

### OrganonScript()
```python
# O que faz:
# 1. Abre Organon
# 2. Carrega diagrama .LST selecionado
```

### run_automation()
```python
# O que faz:
# 1. Executa anaRedeScript()
# 2. (Opcional) Executa OrganonScript()
# 3. Workflow completo
```

## 🖱️ Rastreamento de Mouse

### Opção 7: Rastreamento Contínuo
- Duração configurável (padrão: 10s)
- Mostra X, Y em tempo real
- Pressione ESC para parar
- Gera tabela com últimas 10 posições

### Opção 8: Diagnóstico Original
- Modo original do seu código
- Aguarda 3 segundos
- Mostra alerta com posição

## ⌨️ Atalhos EditCepel (Opção 6)

| Atalho   | Função                |
|----------|-----------------------|
| Ctrl+N   | Novo arquivo          |
| Ctrl+O   | Abrir .PWF/.DAT       |
| Ctrl+*   | Inserir régua         |
| Ctrl+V   | Colar deck            |
| Ctrl+S   | Salvar                |
| Ctrl+W   | Fechar                |

## 🔊 Sistema de Voz

O assistente C3PO fala em português:
- Usa gTTS + pygame
- Toggle on/off: Menu → Opção 9
- Desativa automaticamente se gTTS não instalado

## 🎨 Explorador de Arquivos (Opção 1)

Mostra estrutura visual:
```
📁 SIN
├── 📁 Casos de Uso - SEP ONS
├── 📁 decks
│   ├── ⚡ caso1.pwf
│   └── 📊 caso2.dat
├── 📁 diagramas
│   └── 📋 SIN.lst
└── 📁 Sav
    └── 💾 3Q2025_estudo_v1.SAV
```

## 📝 Próximos Passos

1. **Calibrar coordenadas** dos menus AnaREDE
2. **Testar** cada opção do menu
3. **Adicionar novas coordenadas** conforme você descobre:

```python
# Em AnaRedeDeckBuilder.__init__()
self.coordenadas = {
    'menu_caso': (X1, Y1),
    'abrir_caso': (X2, Y2),
    'novo_botao': (X3, Y3),  # ← Adicionar aqui
}
```

4. **Criar novos métodos** no AnaRedeDeckBuilder:

```python
def executar_contingencia(self):
    """Executa análise de contingência"""
    pyautogui.click(*self.coordenadas['menu_analise'])
    time.sleep(1)
    pyautogui.click(*self.coordenadas['contingencia'])
    ...
```

## 💡 Dicas

- ✅ Use **Opção 7** para mapear todos os menus
- ✅ Sempre teste com **delay maior** em computadores lentos
- ✅ Salve coordenadas em um arquivo JSON para backup
- ✅ Use **Opção 2** antes de executar scripts
- ✅ Toggle voz OFF se estiver em ambiente silencioso

## 🐛 Troubleshooting

**Erro: Caminho não encontrado**
```python
# Ajuste a linha 75 em Configuracoes.__init__()
self.caminho_decks_anaRede = r"SEU_CAMINHO_AQUI"
```

**Erro: keyboard não instalado**
```bash
pip install keyboard
# OU use modo sem keyboard (funciona automaticamente)
```

**Voz não funciona**
```bash
pip install gtts pygame
# OU desative: Menu → Opção 9
```

---

## 🎯 Resumo Final

Você agora tem:
1. ✅ Todo código original preservado
2. ✅ CLI Rich integrada
3. ✅ Explorador de arquivos visual
4. ✅ Rastreamento de mouse profissional
5. ✅ Sistema de seleção interativa
6. ✅ Todas as funções originais funcionando

**Próximo passo:** Calibrar coordenadas e começar a usar! 🚀

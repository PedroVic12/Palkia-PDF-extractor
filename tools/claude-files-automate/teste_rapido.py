#!/usr/bin/env python3
"""
teste_rapido.py - Script de teste rápido
Verifica se todas as funcionalidades estão operacionais
"""

import sys
from pathlib import Path

def testar_imports():
    """Testa se todas as bibliotecas estão instaladas"""
    print("=" * 60)
    print("TESTE 1: Verificando imports")
    print("=" * 60)
    
    bibliotecas = {
        'rich': 'Interface CLI',
        'pyautogui': 'Automação GUI',
        'pygame': 'Sistema de áudio',
        'gtts': 'Text-to-Speech',
    }
    
    resultados = {}
    
    for lib, descricao in bibliotecas.items():
        try:
            __import__(lib)
            print(f"✅ {lib:15s} - {descricao}")
            resultados[lib] = True
        except ImportError:
            print(f"❌ {lib:15s} - {descricao} [NÃO INSTALADO]")
            resultados[lib] = False
    
    # Teste opcional Windows
    try:
        __import__('win10toast')
        print(f"✅ {'win10toast':15s} - Notificações Windows")
        resultados['win10toast'] = True
    except ImportError:
        print(f"⚠️  {'win10toast':15s} - Notificações Windows [Opcional - Windows only]")
        resultados['win10toast'] = False
    
    print()
    return resultados


def testar_classes():
    """Testa se as classes podem ser importadas"""
    print("=" * 60)
    print("TESTE 2: Verificando classes do script")
    print("=" * 60)
    
    try:
        # Simular import do script
        import script_inicial_anaRede as script
        
        classes = [
            'Configuracoes',
            'C3POGeminiAssistant',
            'AnaRedeDeckBuilder',
            'MouseTracker',
            'FileExplorer',
            'EditCepelAutomation',
            'CLIMenu'
        ]
        
        for classe in classes:
            if hasattr(script, classe):
                print(f"✅ Classe {classe}")
            else:
                print(f"❌ Classe {classe} não encontrada")
        
        print()
        return True
    
    except ImportError as e:
        print(f"❌ Erro ao importar script: {e}")
        print()
        return False


def testar_funcoes():
    """Testa se as funções originais existem"""
    print("=" * 60)
    print("TESTE 3: Verificando funções originais")
    print("=" * 60)
    
    try:
        import script_inicial_anaRede as script
        
        funcoes = [
            'anaRedeScript',
            'OrganonScript',
            'run_automation',
            'main'
        ]
        
        for funcao in funcoes:
            if hasattr(script, funcao):
                print(f"✅ Função {funcao}()")
            else:
                print(f"❌ Função {funcao}() não encontrada")
        
        print()
        return True
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        print()
        return False


def testar_configuracoes():
    """Testa a classe Configuracoes"""
    print("=" * 60)
    print("TESTE 4: Testando Configuracoes")
    print("=" * 60)
    
    try:
        import script_inicial_anaRede as script
        
        config = script.Configuracoes()
        
        print(f"✅ Configurações criadas")
        print(f"   Programas: {len(config.PROGRAMAS)}")
        print(f"   Arquivos AnaREDE: {len(config.arquivos_anaRede)}")
        print(f"   Caminho Decks: {config.caminho_decks_anaRede[:50]}...")
        
        # Verificar se caminho existe
        decks_path = Path(config.caminho_decks_anaRede)
        if decks_path.exists():
            print(f"✅ Caminho decks existe")
        else:
            print(f"⚠️  Caminho decks NÃO existe - ajuste na classe Configuracoes")
        
        print()
        return True
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        print()
        return False


def testar_pyautogui():
    """Testa funcionalidades básicas do PyAutoGUI"""
    print("=" * 60)
    print("TESTE 5: Testando PyAutoGUI")
    print("=" * 60)
    
    try:
        import pyautogui
        
        # Obter tamanho da tela
        largura, altura = pyautogui.size()
        print(f"✅ Resolução da tela: {largura}x{altura}")
        
        # Obter posição do mouse
        x, y = pyautogui.position()
        print(f"✅ Posição do mouse: ({x}, {y})")
        
        # Verificar fail-safe
        print(f"✅ Fail-safe ativo: {pyautogui.FAILSAFE}")
        print(f"   (Mova mouse para canto superior esquerdo para parar)")
        
        print()
        return True
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        print()
        return False


def gerar_relatorio(resultados_imports):
    """Gera relatório final"""
    print("\n" + "=" * 60)
    print("RELATÓRIO FINAL")
    print("=" * 60)
    
    essenciais = ['rich', 'pyautogui', 'pygame']
    opcionais = ['gtts', 'win10toast']
    
    print("\n📦 Bibliotecas Essenciais:")
    tudo_ok = True
    for lib in essenciais:
        status = "✅" if resultados_imports.get(lib, False) else "❌"
        print(f"   {status} {lib}")
        if not resultados_imports.get(lib, False):
            tudo_ok = False
    
    print("\n📦 Bibliotecas Opcionais:")
    for lib in opcionais:
        status = "✅" if resultados_imports.get(lib, False) else "⚠️"
        print(f"   {status} {lib}")
    
    print("\n" + "=" * 60)
    
    if tudo_ok:
        print("✅ SISTEMA PRONTO PARA USO!")
        print("\nExecute:")
        print("   python script_inicial_anaRede.py")
    else:
        print("❌ FALTAM DEPENDÊNCIAS")
        print("\nInstale com:")
        print("   pip install -r requirements_script_inicial.txt")
    
    print("=" * 60 + "\n")


def main():
    """Função principal de teste"""
    print("\n")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║          TESTE RÁPIDO - script_inicial_anaRede.py       ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    
    # Executar testes
    resultados_imports = testar_imports()
    testar_classes()
    testar_funcoes()
    testar_configuracoes()
    testar_pyautogui()
    
    # Relatório final
    gerar_relatorio(resultados_imports)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário\n")
    except Exception as e:
        print(f"\n\n❌ Erro durante teste: {e}\n")
        import traceback
        traceback.print_exc()

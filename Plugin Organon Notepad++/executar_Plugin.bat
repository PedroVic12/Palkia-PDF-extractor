@echo off
rem Define a pagina de codigo para UTF-8.
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ============================================================================
:: INSTALADOR ORGANON - VERSAO FINAL E DEFINITIVA
:: ============================================================================
:: - Automatiza 100% da instalacao, incluindo os snippets.
:: ============================================================================

title Instalador Organon para Notepad++ (Versao Final e Definitiva)

call :run_installer
if errorlevel 1 (goto fail) else (goto success)

:: ROTINA PRINCIPAL
:run_installer
    cls
    echo =====================================================
    echo  INSTALADOR DO PLUGIN ORGANON PARA NOTEPAD++
    echo =====================================================
    echo.

    set "SCRIPT_DIR=%~dp0"
    set "NOTEPAD_ROOT="

    :: Tenta encontrar a versao portatil primeiro
    if exist "%SCRIPT_DIR%npp_portable_V8\notepad++.exe" (
        set "NOTEPAD_ROOT=%SCRIPT_DIR%npp_portable_V8"
        echo   [INFO] Notepad++ portatil encontrado em: %NOTEPAD_ROOT%
    ) else (
        :: Se nao encontrou portatil, tenta encontrar a instalacao padrao
        for %%P in ("%ProgramFiles%" "%ProgramFiles(x86)%") do (
            if exist "%%P\Notepad++\notepad++.exe" (
                set "NOTEPAD_ROOT=%%P\Notepad++"
                echo   [INFO] Notepad++ instalado encontrado em: !NOTEPAD_ROOT!
                goto :found_notepad
            )
        )
    )

    :found_notepad
    if not defined NOTEPAD_ROOT (
        echo [ERRO] Notepad++ nao encontrado em nenhuma das localizacoes esperadas.
        exit /b 1
    )

    :: --- Etapa 1: Pergunta sobre o Reset ---
    echo [ETAPA 1 de 4] Verificacao de Reset
    set /p USER_CHOICE="Deseja resetar os snippets (apagar a pasta Config do FingerText)? [S/N]: "
    if /I "%USER_CHOICE%"=="S" (
        if exist "%NOTEPAD_ROOT%\plugins\Config\FingerText" (
            echo   [INFO] Removendo configuracoes antigas do FingerText...
            rd /s /q "%NOTEPAD_ROOT%\plugins\Config\FingerText" || exit /b 1
        )
    )

    :: --- Etapa 2: Finalizar Notepad++ ---
    echo.
    echo [ETAPA 2 de 4] Verificando e finalizando o Notepad++...
    tasklist /FI "IMAGENAME eq notepad++.exe" | find /I "notepad++.exe" >nul && (
        taskkill /f /im notepad++.exe >nul 2>&1
        echo   [OK] Processo do Notepad++ finalizado.
    ) || (
        echo   [INFO] Notepad++ nao esta em execucao.
    )

    :: --- Etapa 3: Instalacao dos Arquivos ---
    echo.
    echo [ETAPA 3 de 4] Instalando e configurando arquivos...
    call :install_for_target "%NOTEPAD_ROOT%" || exit /b 1
    exit /b 0

:: SUB-ROTINA DE INSTALACAO
:install_for_target
    set "TARGET_DIR=%~1"
    echo. & echo   >> Processando destino: "%TARGET_DIR%"
    
    rem --- Criacao de Pastas ---
    if not exist "%TARGET_DIR%\userDefineLangs" mkdir "%TARGET_DIR%\userDefineLangs" || exit /b 1
    if not exist "%TARGET_DIR%\autoCompletion" mkdir "%TARGET_DIR%\autoCompletion" || exit /b 1
    if not exist "%TARGET_DIR%\plugins\FingerText" mkdir "%TARGET_DIR%\plugins\FingerText" || exit /b 1
    if not exist "%TARGET_DIR%\plugins\Config\FingerText" mkdir "%TARGET_DIR%\plugins\Config\FingerText" || exit /b 1

    rem --- Copia dos Arquivos de Configuracao ---
    copy /Y "%SCRIPT_DIR%Organon_Script_Plugin.udl.xml" "%TARGET_DIR%\userDefineLangs\" >nul || exit /b 1
    echo      [OK] Arquivo 'Organon_Script_Plugin.udl.xml' copiado.

    copy /Y "%SCRIPT_DIR%Organon_AutoComplete.xml" "%TARGET_DIR%\autoCompletion\" >nul || exit /b 1
    echo      [OK] Arquivo 'Organon_AutoComplete.xml' copiado.
    
    rem --- Instala o plugin FingerText SOMENTE SE NAO ESTIVER INSTALADO ---
    if not exist "%TARGET_DIR%\plugins\FingerText\FingerText.dll" (
        if exist "%SCRIPT_DIR%FingerText - 0.5.60\FingerText.dll" (
            copy /Y "%SCRIPT_DIR%FingerText - 0.5.60\FingerText.dll" "%TARGET_DIR%\plugins\FingerText\" >nul || exit /b 1
            echo      [OK] Plugin 'FingerText.dll' instalado.
        ) else (
            echo      [AVISO] 'FingerText.dll' nao encontrado na pasta 'FingerText - 0.5.60'.
        )
    ) else (
        echo      [INFO] Plugin 'FingerText.dll' ja instalado. Pulando.
    )

    rem --- Instala o arquivo mestre de snippets ---
    if exist "%SCRIPT_DIR%organon_GLOBAL_MESTRE.sqlite" (
        copy /Y "%SCRIPT_DIR%organon_GLOBAL_MESTRE.sqlite" "%TARGET_DIR%\plugins\Config\FingerText\GLOBAL.sqlite" >nul || exit /b 1
        echo      [OK] Snippets instalados automaticamente.
    ) else (
        echo      [AVISO] Arquivo 'organon_GLOBAL_MESTRE.sqlite' nao encontrado. Snippets nao instalados.
    )
    exit /b 0

:success
    :: --- Etapa 4: Finalizacao ---
    echo.
    echo [ETAPA 4 de 4] Finalizando a instalacao.
    echo.
    echo =====================================================
    echo      INSTALACAO AUTOMATIZADA CONCLUIDA!
    echo =====================================================
    echo.
    echo Lembrete: Para o TAB funcionar, desative-o no NppSnippets.
    echo.
    if defined NOTEPAD_ROOT (
        start "" "%NOTEPAD_ROOT%\notepad++.exe"
    )
    goto end

:fail
    echo. & echo =====================================================
    echo           FALHA DURANTE A INSTALACAO
    echo =====================================================
    echo Ocorreu um erro. A janela permanecera aberta.
    goto end

:end
    pause
    endlocal
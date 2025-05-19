@echo off
REM Script para executar o CheckStyle e corrigir problemas comuns

echo ===================================================
echo Executando CheckStyle em Repositorios Java
echo ===================================================

REM Configurar diretórios
set PROJECT_DIR=%~dp0
set REPO_DIR=%PROJECT_DIR%..\repo_miner\data\raw_repos
set OUTPUT_DIR=%PROJECT_DIR%..\data\checkstyle
set CONFIG_PATH=%PROJECT_DIR%config\checkstyle-config.xml
set JAR_PATH=%PROJECT_DIR%config\checkstyle.jar

REM Verificar se o Python está instalado
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Python não encontrado! Por favor, instale o Python 3.
    pause
    exit /b 1
) else (
    echo [OK] Python encontrado.
)

REM Verificar se o Java está instalado
java -version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Java não encontrado! Por favor, instale o Java.
    pause
    exit /b 1
) else (
    echo [OK] Java encontrado.
)

REM Verificar se as dependências estão instaladas
python -c "import dotenv" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Instalando dependências...
    pip install python-dotenv tqdm requests
)

REM Verificar se o arquivo JAR do CheckStyle existe
if not exist "%JAR_PATH%" (
    echo [INFO] Baixando CheckStyle Java 8 compatível...
    python %PROJECT_DIR%download_checkstyle_java8.py
)

REM Verificar se o arquivo de configuração existe
if not exist "%CONFIG_PATH%" (
    echo [INFO] Criando arquivo de configuração mínimo...
    echo ^<?xml version="1.0"?^> > "%CONFIG_PATH%"
    echo ^<!DOCTYPE module PUBLIC "-//Checkstyle//DTD Checkstyle Configuration 1.3//EN" "https://checkstyle.org/dtds/configuration_1_3.dtd"^> >> "%CONFIG_PATH%"
    echo ^<module name="Checker"^> >> "%CONFIG_PATH%"
    echo     ^<property name="severity" value="warning"/^> >> "%CONFIG_PATH%"
    echo     ^<property name="fileExtensions" value="java"/^> >> "%CONFIG_PATH%"
    echo     ^<module name="TreeWalker"^> >> "%CONFIG_PATH%"
    echo         ^<module name="MethodLength"^> >> "%CONFIG_PATH%"
    echo             ^<property name="tokens" value="METHOD_DEF"/^> >> "%CONFIG_PATH%"
    echo             ^<property name="max" value="60"/^> >> "%CONFIG_PATH%"
    echo         ^</module^> >> "%CONFIG_PATH%"
    echo     ^</module^> >> "%CONFIG_PATH%"
    echo ^</module^> >> "%CONFIG_PATH%"
)

REM Criar diretório de saída
if not exist "%OUTPUT_DIR%" (
    echo [INFO] Criando diretório de saída...
    mkdir "%OUTPUT_DIR%"
)

echo [INFO] Executando análise...
python "%PROJECT_DIR%run_checkstyle.py" --repo-dir="%REPO_DIR%" --config="%CONFIG_PATH%" --jar="%JAR_PATH%" --output-dir="%OUTPUT_DIR%" --verbose

if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Ocorreu um erro durante a execução da análise.
    echo Verifique o arquivo run_checkstyle.log para mais detalhes.
) else (
    echo [SUCESSO] Análise concluída!
    echo Os resultados foram salvos em: %OUTPUT_DIR%
)

echo.
echo Pressione qualquer tecla para sair...
pause
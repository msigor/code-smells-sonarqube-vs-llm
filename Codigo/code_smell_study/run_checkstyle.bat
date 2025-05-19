@echo off
REM Script para executar a análise de CheckStyle nos repositórios clonados

echo Iniciando análise com CheckStyle...

REM Verificar se o Python está instalado
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python não encontrado! Por favor, instale o Python 3.
    exit /b 1
)

REM Instalar dependências se necessário
pip show python-dotenv >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Instalando dependências...
    pip install python-dotenv tqdm requests
)

REM Criar diretório de resultados se não existir
if not exist "data\checkstyle" mkdir "data\checkstyle"

REM Executar análise com CheckStyle
python run_checkstyle.py --repo-dir="../repo_miner/data/raw_repos" --output-dir="../data/checkstyle"

echo Análise concluída! Os resultados estão em data/checkstyle/
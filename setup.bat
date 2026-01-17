@echo off
echo ========================================
echo   SISTEMA DE AGENDAMENTO - BARBEARIA
echo ========================================
echo.

REM Verificar se o ambiente virtual existe
if not exist "venv\" (
    echo [1/4] Criando ambiente virtual...
    python -m venv venv
    if errorlevel 1 (
        echo ERRO: Falha ao criar ambiente virtual
        echo Certifique-se que o Python esta instalado
        pause
        exit /b 1
    )
    echo Ambiente virtual criado!
    echo.
)

REM Ativar ambiente virtual
echo [2/4] Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Instalar dependências
echo [3/4] Instalando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERRO: Falha ao instalar dependencias
    pause
    exit /b 1
)
echo Dependencias instaladas!
echo.

REM Verificar se .env existe
if not exist ".env" (
    echo [4/4] Criando arquivo de configuracao...
    copy .env.example .env
    echo.
    echo IMPORTANTE: Edite o arquivo .env com suas configuracoes!
    echo.
)

REM Inicializar banco de dados
echo Deseja inicializar o banco de dados agora? (S/N)
set /p init_db=
if /i "%init_db%"=="S" (
    python init_db.py
)

echo.
echo ========================================
echo   INSTALACAO CONCLUIDA!
echo ========================================
echo.
echo Para iniciar o sistema, execute:
echo   run.bat
echo.
pause

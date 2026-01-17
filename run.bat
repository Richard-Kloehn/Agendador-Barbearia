@echo off
echo ========================================
echo   INICIANDO SISTEMA DE BARBEARIA
echo ========================================
echo.

REM Ativar ambiente virtual
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo ERRO: Ambiente virtual nao encontrado!
    echo Execute primeiro: setup.bat
    pause
    exit /b 1
)

REM Verificar se .env existe
if not exist ".env" (
    echo AVISO: Arquivo .env nao encontrado!
    echo Criando a partir do exemplo...
    copy .env.example .env
    echo.
    echo IMPORTANTE: Edite o arquivo .env antes de continuar!
    pause
)

echo Iniciando servidor...
echo.
echo Acesse:
echo   - Site: http://localhost:5000
echo   - Admin: http://localhost:5000/admin-dashboard
echo.
echo Pressione Ctrl+C para parar o servidor
echo.

python app.py

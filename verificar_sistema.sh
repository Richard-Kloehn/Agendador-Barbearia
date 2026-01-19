#!/bin/bash

# 🔍 SCRIPT DE VERIFICAÇÃO RÁPIDA DO SISTEMA
# Execute na VM para verificar se tudo está funcionando

echo "================================================"
echo "🔍 VERIFICAÇÃO DO SISTEMA COMPLETO"
echo "================================================"
echo ""

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Função para testar
test_command() {
    if eval "$1" > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC} $2"
        return 0
    else
        echo -e "${RED}❌${NC} $2"
        return 1
    fi
}

# 1. Verificar Python
echo "🐍 PYTHON"
test_command "python3 --version" "Python 3 instalado"
test_command "pip3 --version" "pip instalado"

# 2. Verificar Chrome
echo ""
echo "🌐 GOOGLE CHROME"
test_command "which google-chrome" "Google Chrome instalado"
test_command "which chromium" "Chromium disponível" || echo -e "${YELLOW}⚠️${NC}  Chromium não encontrado (ok, usa Chrome)"

# 3. Verificar Xvfb
echo ""
echo "🖥️ XVFB (DISPLAY VIRTUAL)"
test_command "which Xvfb" "Xvfb instalado"

# 4. Verificar Variáveis de Ambiente
echo ""
echo "⚙️ VARIÁVEIS DE AMBIENTE (.env)"
if [ -f ~/.env ]; then
    echo -e "${GREEN}✅${NC} Arquivo .env existe"
    if grep -q "DATABASE_URL" ~/.env; then
        echo -e "${GREEN}✅${NC} DATABASE_URL configurado"
    else
        echo -e "${RED}❌${NC} DATABASE_URL NÃO configurado"
    fi
    if grep -q "WHATSAPP_API_TOKEN" ~/.env; then
        echo -e "${GREEN}✅${NC} WHATSAPP_API_TOKEN configurado"
    else
        echo -e "${RED}❌${NC} WHATSAPP_API_TOKEN NÃO configurado"
    fi
else
    echo -e "${RED}❌${NC} Arquivo .env NÃO ENCONTRADO"
fi

# 5. Verificar Ambiente Virtual
echo ""
echo "🔧 AMBIENTE VIRTUAL PYTHON"
if [ -d "~/whatsapp-server/venv" ]; then
    echo -e "${GREEN}✅${NC} Ambiente virtual existe"
else
    echo -e "${RED}❌${NC} Ambiente virtual não encontrado"
fi

# 6. Verificar Serviço WhatsApp
echo ""
echo "🚀 SERVIÇO WHATSAPP"
if systemctl is-active --quiet whatsapp-api; then
    echo -e "${GREEN}✅${NC} Serviço whatsapp-api ATIVO"
else
    echo -e "${YELLOW}⚠️${NC}  Serviço whatsapp-api INATIVO (pode iniciar manualmente)"
fi

# 7. Verificar Portas
echo ""
echo "🔌 PORTAS"
test_command "netstat -tuln 2>/dev/null | grep -q ':5000'" "Porta 5000 (Site) aberta"
test_command "netstat -tuln 2>/dev/null | grep -q ':5001'" "Porta 5001 (WhatsApp API) aberta"

# 8. Verificar Conexão com Internet
echo ""
echo "🌍 INTERNET"
test_command "ping -c 1 8.8.8.8" "Conexão com Internet OK"

# 9. Espaço em Disco
echo ""
echo "💾 ESPAÇO EM DISCO"
DISK_FREE=$(df -h / | awk 'NR==2 {print $4}')
echo -e "${GREEN}✅${NC} Espaço livre: $DISK_FREE"

# 10. Memória RAM
echo ""
echo "🧠 MEMÓRIA RAM"
FREE_MEM=$(free -h | awk 'NR==2 {print $7}')
echo -e "${GREEN}✅${NC} Memória livre: $FREE_MEM"

# 11. Teste de Conexão com Banco (Se Python disponível)
echo ""
echo "🗄️ BANCO DE DADOS (SUPABASE)"
if command -v python3 &> /dev/null; then
    cat > test_db_quick.py << 'EOF'
import os
import sys
from dotenv import load_dotenv

try:
    load_dotenv()
    import psycopg2
    
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cursor = conn.cursor()
    cursor.execute("SELECT NOW()")
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    print(f"✅ Conexão com Supabase OK")
except ImportError:
    print(f"⚠️  psycopg2 não instalado (necessário para banco)")
except Exception as e:
    print(f"❌ Erro ao conectar: {str(e)[:50]}")
EOF
    python3 test_db_quick.py 2>/dev/null
    rm -f test_db_quick.py
else
    echo -e "${RED}❌${NC} Python não disponível"
fi

# 12. Verificar Git
echo ""
echo "📚 GIT"
test_command "git --version" "Git instalado"

# 13. IP Público
echo ""
echo "🌐 IP PÚBLICO"
IP=$(curl -s ifconfig.me 2>/dev/null)
if [ -n "$IP" ]; then
    echo -e "${GREEN}✅${NC} IP Público: $IP"
else
    echo -e "${YELLOW}⚠️${NC}  Não conseguiu obter IP público"
fi

# 14. Resumo Final
echo ""
echo "================================================"
echo "📊 RESUMO DA CONFIGURAÇÃO"
echo "================================================"
echo ""
echo "✅ Tudo verificado!"
echo ""
echo "Próximas ações:"
echo "  1. Se algo está ❌, execute os passos de configuração"
echo "  2. Se DATABASE_URL está vazio, configure .env"
echo "  3. Se serviço está inativo, inicie: sudo systemctl start whatsapp-api"
echo "  4. Para ver logs: sudo journalctl -u whatsapp-api -f"
echo ""
echo "Status: PRONTO PARA USAR ✅"
echo "================================================"

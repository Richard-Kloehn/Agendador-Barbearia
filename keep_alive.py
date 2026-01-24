"""
🔄 KEEP-ALIVE PARA RENDER GRATUITO
Faz ping no servidor a cada 10 minutos para evitar hibernação
"""

import requests
import time
from datetime import datetime

# Substitua pela URL do seu site no Render
URL_SITE = "https://seu-site.onrender.com"  # ← TROCAR AQUI

def fazer_ping():
    """Faz uma requisição ao site para mantê-lo ativo"""
    try:
        response = requests.get(URL_SITE, timeout=30)
        status = "✅" if response.status_code == 200 else "⚠️"
        print(f"{datetime.now().strftime('%H:%M:%S')} - {status} Ping realizado - Status: {response.status_code}")
        return True
    except Exception as e:
        print(f"{datetime.now().strftime('%H:%M:%S')} - ❌ Erro no ping: {e}")
        return False

def main():
    print("🔄 KEEP-ALIVE INICIADO")
    print(f"🌐 URL: {URL_SITE}")
    print(f"⏱️  Ping a cada 10 minutos")
    print("=" * 60)
    print()
    
    while True:
        fazer_ping()
        # Aguarda 10 minutos (600 segundos)
        # Render hiberna após 15min, então 10min é seguro
        time.sleep(600)

if __name__ == '__main__':
    main()

"""
Script para verificar status da conexão WHAPI
Execute: python verificar_status_whapi.py
"""

import requests
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def verificar_status_whapi():
    """Verifica status da conexão e canal WHAPI"""
    
    api_url = os.getenv('WHAPI_API_URL', 'https://gate.whapi.cloud').rstrip('/')
    api_token = os.getenv('WHAPI_API_TOKEN', '')
    
    print("=" * 60)
    print("VERIFICAÇÃO DE STATUS DO WHAPI")
    print("=" * 60)
    
    if not api_token:
        print("❌ ERRO: WHAPI_API_TOKEN não configurado!")
        return
    
    print(f"✅ API URL: {api_url}")
    print(f"✅ Token: {api_token[:10]}...{api_token[-4:]}")
    print()
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Accept': 'application/json'
    }
    
    # 1. Verificar status da conta/canal
    print("=" * 60)
    print("1. VERIFICANDO STATUS DO CANAL")
    print("=" * 60)
    
    try:
        response = requests.get(
            f'{api_url}/settings',
            headers=headers,
            timeout=30
        )
        
        print(f"📡 Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            import json
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print()
    
    # 2. Verificar informações do dispositivo/número conectado
    print("=" * 60)
    print("2. VERIFICANDO DISPOSITIVO CONECTADO")
    print("=" * 60)
    
    try:
        response = requests.get(
            f'{api_url}/me',
            headers=headers,
            timeout=30
        )
        
        print(f"📡 Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            import json
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if 'phone' in result:
                print(f"\n📱 NÚMERO CONECTADO: {result['phone']}")
            if 'name' in result:
                print(f"👤 NOME: {result['name']}")
            if 'status' in result:
                print(f"⚡ STATUS: {result['status']}")
        else:
            print(f"❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print()
    
    # 3. Verificar status da conexão/sessão
    print("=" * 60)
    print("3. VERIFICANDO STATUS DA SESSÃO WHATSAPP")
    print("=" * 60)
    
    try:
        response = requests.get(
            f'{api_url}/health',
            headers=headers,
            timeout=30
        )
        
        print(f"📡 Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            import json
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if 'status' in result:
                status = result['status']
                if status in ['online', 'connected', 'ready']:
                    print(f"\n✅ WHATSAPP CONECTADO: {status}")
                else:
                    print(f"\n⚠️ STATUS: {status}")
                    print("⚠️ O WhatsApp pode não estar conectado corretamente!")
        else:
            print(f"❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print()
    print("=" * 60)
    print("DIAGNÓSTICO")
    print("=" * 60)
    print("Se o STATUS não estiver como 'online/connected/ready':")
    print("1. Acesse o painel do WHAPI: https://panel.whapi.cloud")
    print("2. Verifique se o WhatsApp está conectado")
    print("3. Escaneie o QR Code novamente se necessário")
    print("4. Verifique se o número da barbearia tem WhatsApp ativo")

if __name__ == '__main__':
    verificar_status_whapi()

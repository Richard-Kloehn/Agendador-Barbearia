"""
Script para verificar status do canal Whapi
============================================
Verifica se o canal está conectado e pronto para enviar mensagens
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_url = os.getenv('WHAPI_API_URL', 'https://gate.whapi.cloud').rstrip('/')
api_token = os.getenv('WHAPI_API_TOKEN', '')

if not api_token:
    print("❌ WHAPI_API_TOKEN não configurado")
    exit(1)

print(f"✅ API URL: {api_url}")
print(f"✅ Token: {api_token[:10]}...{api_token[-4:]}")

headers = {
    'Authorization': f'Bearer {api_token}',
    'Accept': 'application/json'
}

# Verificar status do canal
print("\n🔍 Verificando status do canal...")
try:
    response = requests.get(f'{api_url}/settings', headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n📋 Informações do canal:")
        print(f"   Nome: {data.get('push_name', 'N/A')}")
        print(f"   Número: {data.get('wid', 'N/A')}")
        print(f"   Status: {data.get('status', 'N/A')}")
        
        # Verificar se está conectado
        if data.get('status') == 'ready':
            print("\n✅ Canal conectado e pronto para enviar mensagens!")
        else:
            print(f"\n⚠️ Canal não está pronto. Status atual: {data.get('status')}")
            print("\n💡 Você precisa conectar seu WhatsApp primeiro.")
            print("   Acesse: https://panel.whapi.cloud/channels")
except Exception as e:
    print(f"❌ Erro: {e}")

# Verificar QR Code se necessário
print("\n🔍 Tentando obter QR Code...")
try:
    response = requests.get(f'{api_url}/screen', headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('qr'):
            print("\n📱 QR CODE disponível:")
            print(data.get('qr'))
            print("\n💡 Escaneie este QR Code com seu WhatsApp para conectar")
        else:
            print("\n✅ Não há QR Code (canal já conectado)")
    else:
        print(f"Resposta: {response.text}")
except Exception as e:
    print(f"❌ Erro: {e}")

"""
Script para conectar canal Whapi e obter QR Code
================================================
"""

import requests
import os
from dotenv import load_dotenv
import time

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

print("\n" + "="*70)
print("📱 CONECTANDO CANAL WHAPI")
print("="*70)

# Método 1: Tentar endpoint /qr
print("\n1️⃣ Tentando endpoint /qr...")
try:
    response = requests.get(f'{api_url}/qr', headers=headers, timeout=10)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Resposta: {data}")
        
        if data.get('qr'):
            print("\n✅ QR CODE OBTIDO:")
            print(data.get('qr'))
            print("\n📱 Escaneie este QR Code com seu WhatsApp:")
            print("   1. Abra o WhatsApp no celular")
            print("   2. Toque em ⋮ (menu) > Aparelhos conectados")
            print("   3. Toque em 'Conectar um aparelho'")
            print("   4. Aponte a câmera para o QR Code acima")
        elif data.get('connected'):
            print("\n✅ Canal já está conectado!")
    else:
        print(f"   Resposta: {response.text}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Método 2: Tentar endpoint /health/me
print("\n2️⃣ Verificando saúde do canal (/health/me)...")
try:
    response = requests.get(f'{api_url}/health/me', headers=headers, timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   Resposta: {response.text}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Método 3: Verificar todos os endpoints disponíveis
print("\n3️⃣ Listando recursos disponíveis...")
endpoints = [
    '/me',
    '/status',
    '/state',
    '/channels',
    '/channel',
    '/connect',
    '/qr-code',
]

for endpoint in endpoints:
    try:
        response = requests.get(f'{api_url}{endpoint}', headers=headers, timeout=5)
        if response.status_code != 404:
            print(f"   ✅ {endpoint}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"      {data}")
    except:
        pass

print("\n" + "="*70)
print("\n💡 PRÓXIMOS PASSOS:")
print("   1. Se você viu um QR Code acima, escaneie-o com seu WhatsApp")
print("   2. Se não viu QR Code, acesse: https://panel.whapi.cloud/channels")
print("   3. Conecte seu número de WhatsApp no painel")
print("   4. Aguarde alguns segundos e execute este script novamente")
print("\n⚠️ IMPORTANTE: A conta Whapi tem 5 dias de trial gratuito!")

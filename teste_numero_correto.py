import requests
import os
from dotenv import load_dotenv

load_dotenv()

WHAPI_URL = os.getenv('WHAPI_API_URL', 'https://gate.whapi.cloud')
WHAPI_TOKEN = os.getenv('WHAPI_API_TOKEN')

headers = {
    'Authorization': f'Bearer {WHAPI_TOKEN}',
    'Content-Type': 'application/json'
}

# Testando com 10 dígitos (número que aparece no WHAPI)
numero_10_digitos = "554791557386"  # SEM o 9 extra

mensagem = """🧪 TESTE - Número com 10 dígitos

Esta mensagem foi enviada para: 554791557386

Se você recebeu, este é o formato correto! ✅

Navalha's Barber Club 💈"""

payload = {
    'typing_time': 0,
    'to': numero_10_digitos,
    'body': mensagem
}

print("=" * 60)
print("TESTE COM NÚMERO DE 10 DÍGITOS")
print("=" * 60)
print(f"📱 Enviando para: {numero_10_digitos}")
print()

try:
    response = requests.post(
        f"{WHAPI_URL}/messages/text",
        headers=headers,
        json=payload,
        timeout=60
    )
    
    print(f"📡 Status HTTP: {response.status_code}")
    print()
    
    if response.status_code in [200, 201]:
        result = response.json()
        print("✅ SUCESSO!")
        print(f"📋 Resposta: {result}")
        
        if result.get('sent'):
            print()
            print("✅ Mensagem ENVIADA!")
            print("📱 Verifique o WhatsApp (47) 9155-7386")
    else:
        print(f"❌ Erro: {response.text}")
        
except Exception as e:
    print(f"❌ Erro: {e}")

print()
print("=" * 60)

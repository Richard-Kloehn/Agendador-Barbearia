import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

WHAPI_URL = os.getenv('WHAPI_API_URL', 'https://gate.whapi.cloud')
WHAPI_TOKEN = os.getenv('WHAPI_API_TOKEN')

headers = {
    'Authorization': f'Bearer {WHAPI_TOKEN}',
    'Content-Type': 'application/json'
}

# 4 números SEM O 55
numeros = [
    {"numero": "47991557386", "descricao": "(47) 99155-7386"},
    {"numero": "48992032706", "descricao": "(48) 99203-2706"},
    {"numero": "47992849526", "descricao": "(47) 99284-9526"}
]

print("=" * 70)
print("TESTE SEM O CÓDIGO +55")
print("=" * 70)
print()

for item in numeros:
    numero = item["numero"]
    desc = item["descricao"]
    
    print(f"📱 Enviando para {desc}")
    print(f"   Formato: {numero} (SEM 55)")
    
    mensagem = f"""🎯 TESTE 3 - SEM CÓDIGO DO PAÍS

Tentativa sem o +55 no início.

Destino: {desc}

Se chegou, RESPONDA "OK"! ✅

💈 Navalha's Barber Club"""
    
    payload = {
        'typing_time': 0,
        'to': numero,
        'body': mensagem
    }
    
    try:
        response = requests.post(
            f"{WHAPI_URL}/messages/text",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            status = result.get('message', {}).get('status', 'unknown')
            chat_id = result.get('message', {}).get('chat_id', 'N/A')
            
            print(f"   ✅ Enviado!")
            print(f"   Status: {status}")
            print(f"   Chat ID: {chat_id}")
        else:
            print(f"   ❌ Erro {response.status_code}")
            print(f"   Resposta: {response.text[:150]}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print()
    time.sleep(2)

print("=" * 70)
print("AGORA VERIFIQUE NO WHATSAPP")
print("=" * 70)
print("Se aparecer 2 ticks (✓✓), esse é o formato correto!")
print("=" * 70)

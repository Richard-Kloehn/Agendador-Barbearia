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

# 4 números brasileiros (sem o +61)
numeros = [
    {"numero": "5547991557386", "descricao": "(47) 99155-7386"},
    {"numero": "5548992032706", "descricao": "(48) 99203-2706"},
    {"numero": "5547992849526", "descricao": "(47) 99284-9526"},
    {"numero": "47991557386", "descricao": "(47) 9915-7386"}
]

print("=" * 70)
print("TESTE COM FORMATO @s.whatsapp.net")
print("=" * 70)
print()

for item in numeros:
    numero = item["numero"]
    desc = item["descricao"]
    
    # Adicionar @s.whatsapp.net
    numero_formatado = f"{numero}@s.whatsapp.net"
    
    print(f"📱 Enviando para {desc}")
    print(f"   Formato: {numero_formatado}")
    
    mensagem = f"""✅ TESTE 2 - FORMATO WHATSAPP ID

Esta é uma nova tentativa de envio.

Destino: {desc}

Se você recebeu, responda "RECEBI"! 🎯

💈 Sistema de Agendamentos"""
    
    payload = {
        'typing_time': 0,
        'to': numero_formatado,  # Usando formato completo
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
print("VERIFICAR NO WHATSAPP DA BARBEARIA")
print("=" * 70)
print("Confira se agora as mensagens têm 2 ticks (✓✓)")
print("=" * 70)

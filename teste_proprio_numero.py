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

# Enviando para o PRÓPRIO número da barbearia (554791557386)
numero = "554791557386"  # Número conectado no WHAPI

mensagem = """🧪 AUTO-TESTE DO SISTEMA

Você está recebendo esta mensagem porque ela foi enviada para o próprio número da barbearia.

Se esta mensagem chegou com 2 ticks (✓✓), o WHAPI está funcionando perfeitamente!

💈 Navalha's Barber Club
Sistema de Agendamentos Online"""

payload = {
    'typing_time': 0,
    'to': numero,
    'body': mensagem
}

print("=" * 70)
print("AUTO-TESTE - ENVIANDO PARA O PRÓPRIO NÚMERO DA BARBEARIA")
print("=" * 70)
print(f"📱 Número da barbearia: {numero}")
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
        print("✅ MENSAGEM ENVIADA!")
        
        import json
        print("\n📋 Resposta:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        print()
        print("=" * 70)
        print("📱 VERIFIQUE O WHATSAPP DA BARBEARIA (47) 9155-7386")
        print()
        print("Se a mensagem chegou com 2 ticks (✓✓):")
        print("  ✅ O sistema está funcionando!")
        print("  ✅ O problema é o formato dos outros números")
        print()
        print("Se ficou com 1 tick (✓) ou não chegou:")
        print("  ⚠️  Pode haver problema com a conexão do WHAPI")
        print("=" * 70)
    else:
        print(f"❌ Erro {response.status_code}")
        print(f"📋 Resposta: {response.text}")
        
except Exception as e:
    print(f"❌ Erro: {e}")

print()

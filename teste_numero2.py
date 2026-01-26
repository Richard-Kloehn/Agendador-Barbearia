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

# Número escolhido: opção 2
numero = "5548992032706"  # (48) 99203-2706

mensagem = """Olá! 👋

✅ Mensagem de TESTE do sistema de agendamentos da barbearia.

Você está recebendo esta mensagem porque o sistema de WhatsApp está sendo testado.

Se você recebeu, tudo está funcionando perfeitamente! 🎉

💈 Navalha's Barber Club
📱 Sistema de Agendamentos Online"""

payload = {
    'typing_time': 0,
    'to': numero,
    'body': mensagem
}

print("=" * 70)
print("TESTE DE ENVIO - NÚMERO 2")
print("=" * 70)
print(f"📱 Enviando para: {numero}")
print(f"📱 Formatado: (48) 99203-2706")
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
        
        import json
        print("\n📋 Resposta:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if result.get('sent'):
            print()
            print("=" * 70)
            print("✅ MENSAGEM ENVIADA!")
            print("=" * 70)
            print(f"📱 Verifique o WhatsApp: (48) 99203-2706")
            print(f"🔔 Status: {result.get('message', {}).get('status', 'unknown')}")
            print("=" * 70)
    else:
        print(f"❌ Erro {response.status_code}")
        print(f"📋 Resposta: {response.text}")
        
except Exception as e:
    print(f"❌ Erro: {e}")

print()

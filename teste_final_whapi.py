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

# Testando com número que JÁ está nos chats permitidos
numero = "47991557386"  # Esse está na lista de 5 chats

mensagem = """✅ TESTE FINAL - WHAPI FUNCIONANDO

Esta mensagem foi enviada para o número que já está cadastrado no trial.

Se você recebeu, o sistema está 100% funcional! 🎉

Navalha's Barber Club 💈
--
Sistema de Agendamentos Online"""

payload = {
    'typing_time': 0,
    'to': numero,
    'body': mensagem
}

print("=" * 70)
print("TESTE COM NÚMERO JÁ CADASTRADO NO TRIAL")
print("=" * 70)
print(f"✅ Número: {numero} (já está nos 5 chats permitidos)")
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
        print("🎉 SUCESSO!")
        print(f"📋 Resposta completa:")
        import json
        print(json.dumps(result, indent=2))
        
        if result.get('sent'):
            print()
            print("=" * 70)
            print("✅ MENSAGEM ENVIADA COM SUCESSO!")
            print("=" * 70)
            print(f"📱 Verifique o WhatsApp: {numero}")
            print()
            print("🎯 SISTEMA FUNCIONANDO PERFEITAMENTE!")
            print()
            print("Agora você pode:")
            print("  1. Fazer deploy no Railway (já está configurado)")
            print("  2. Fazer upgrade do WHAPI ($10/mês) para chats ilimitados")
            print("  3. Começar a usar o sistema para agendamentos reais!")
            print("=" * 70)
    else:
        print(f"❌ Erro {response.status_code}: {response.text}")
        
except Exception as e:
    print(f"❌ Erro na requisição: {e}")

print()

import requests
import os
from dotenv import load_dotenv

load_dotenv()

WHAPI_URL = os.getenv('WHAPI_API_URL', 'https://gate.whapi.cloud')
WHAPI_TOKEN = os.getenv('WHAPI_API_TOKEN')

headers = {
    'Authorization': f'Bearer {WHAPI_TOKEN}'
}

# Números para verificar
numeros = [
    "5548992032706",
    "5547992849526",
    "5547991557386"
]

print("=" * 70)
print("VERIFICAR SE NÚMEROS TÊM WHATSAPP")
print("=" * 70)
print()

for numero in numeros:
    print(f"🔍 Verificando: {numero}")
    try:
        response = requests.get(
            f"{WHAPI_URL}/contacts/{numero}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            
            # Verificar se tem WhatsApp
            is_whatsapp = data.get('is_whatsapp', False)
            if is_whatsapp:
                print(f"   ✅ TEM WhatsApp!")
            else:
                print(f"   ❌ NÃO tem WhatsApp!")
                
            # Outras informações
            if data.get('name'):
                print(f"   📝 Nome: {data.get('name')}")
            if data.get('status'):
                print(f"   💬 Status: {data.get('status')}")
        else:
            print(f"   ⚠️  Status: {response.status_code}")
            print(f"   📋 Resposta: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print()

print("=" * 70)
print()
print("💡 DICA:")
print("   Se aparecer 'NÃO tem WhatsApp', o número não pode receber mensagens")
print("   Você pode usar um número seu para testar!")
print("=" * 70)

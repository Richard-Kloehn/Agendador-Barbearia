import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

EVOLUTION_API_URL = os.getenv('EVOLUTION_API_URL')
EVOLUTION_API_KEY = os.getenv('EVOLUTION_API_KEY')
INSTANCE_NAME = os.getenv('EVOLUTION_INSTANCE_NAME', 'barbearia')

headers = {
    'apikey': EVOLUTION_API_KEY
}

print("=" * 70)
print("DEBUG - LISTAR TODAS AS INSTÂNCIAS")
print("=" * 70)

try:
    response = requests.get(
        f"{EVOLUTION_API_URL}/instance/fetchInstances",
        headers=headers,
        timeout=30
    )
    print(f"📡 Status HTTP: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n📋 Resposta completa:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"❌ Erro: {response.text}")
        
except Exception as e:
    print(f"❌ Erro: {e}")

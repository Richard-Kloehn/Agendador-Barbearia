import requests
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()

EVOLUTION_API_URL = os.getenv('EVOLUTION_API_URL')
EVOLUTION_API_KEY = os.getenv('EVOLUTION_API_KEY')
INSTANCE_NAME = os.getenv('EVOLUTION_INSTANCE_NAME', 'barbearia')

headers = {
    'apikey': EVOLUTION_API_KEY,
    'Content-Type': 'application/json'
}

print("=" * 70)
print("TESTAR MÉTODOS ALTERNATIVOS PARA QR CODE")
print("=" * 70)
print()

# Método 1: Verificar status da instância
print("1️⃣  Verificando status detalhado...")
try:
    response = requests.get(
        f"{EVOLUTION_API_URL}/instance/connectionState/{INSTANCE_NAME}",
        headers=headers,
        timeout=30
    )
    print(f"📡 Status HTTP: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"📋 Estado: {json.dumps(data, indent=2)}")
    else:
        print(f"⚠️  Erro: {response.text}")
except Exception as e:
    print(f"❌ Erro: {e}")

print()
print("-" * 70)
print()

# Método 2: Logout e reconectar forçado
print("2️⃣  Tentando logout da instância...")
try:
    response = requests.delete(
        f"{EVOLUTION_API_URL}/instance/logout/{INSTANCE_NAME}",
        headers=headers,
        timeout=30
    )
    print(f"📡 Status HTTP: {response.status_code}")
    if response.status_code in [200, 201]:
        print("✅ Logout realizado")
    else:
        print(f"⚠️  Resposta: {response.text}")
except Exception as e:
    print(f"⚠️  Erro: {e}")

print()
print("⏳ Aguardando 10 segundos...")
time.sleep(10)

# Método 3: Conectar novamente (deve gerar QR)
print()
print("3️⃣  Tentando gerar QR Code após logout...")
for i in range(1, 4):
    print(f"\n   Tentativa {i}/3...")
    try:
        response = requests.get(
            f"{EVOLUTION_API_URL}/instance/connect/{INSTANCE_NAME}",
            headers=headers,
            timeout=30
        )
        print(f"   📡 Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'base64' in data and data['base64']:
                print("\n🎉 QR CODE GERADO!")
                print(f"\n✅ Use o script conectar_whatsapp_evolution.py para exibir")
                break
            elif 'code' in data and data['code']:
                print("\n🎉 QR CODE GERADO (formato código)!")
                print(f"Código: {data['code'][:50]}...")
                break
            else:
                print(f"   ⚠️  Resposta: {json.dumps(data, indent=2)}")
        else:
            print(f"   ❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    if i < 3:
        print("   ⏳ Aguardando 10 segundos...")
        time.sleep(10)

print()
print("=" * 70)
print()

# Método 4: Verificar se há QR salvo no fetchInstances
print("4️⃣  Verificando se QR está disponível via fetchInstances...")
try:
    response = requests.get(
        f"{EVOLUTION_API_URL}/instance/fetchInstances?instanceName={INSTANCE_NAME}",
        headers=headers,
        timeout=30
    )
    
    if response.status_code == 200:
        instances = response.json()
        print(f"📋 Instâncias retornadas: {len(instances)}")
        
        if instances:
            inst = instances[0]
            print(f"\n✅ Instância encontrada:")
            print(f"   Nome: {inst.get('name')}")
            print(f"   Status: {inst.get('connectionStatus')}")
            print(f"   Número: {inst.get('number', 'N/A')}")
            
            # Verificar se tem QR code nas propriedades
            for key in inst.keys():
                if 'qr' in key.lower():
                    print(f"   {key}: {inst[key]}")
    else:
        print(f"❌ Erro: {response.text}")
        
except Exception as e:
    print(f"❌ Erro: {e}")

print()
print("=" * 70)

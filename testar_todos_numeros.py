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

# TODOS os 5 números cadastrados
numeros = [
    {"numero": "5547991557386", "descricao": "(47) 99155-7386"},
    {"numero": "5548992032706", "descricao": "(48) 99203-2706"},
    {"numero": "5547992849526", "descricao": "(47) 99284-9526"},
    {"numero": "61371989950", "descricao": "+61 37 1989 950"},
    {"numero": "47991557386", "descricao": "(47) 9915-7386"}
]

print("=" * 70)
print("ENVIANDO PARA TODOS OS 5 NÚMEROS CADASTRADOS")
print("=" * 70)
print()

resultados = []

for item in numeros:
    numero = item["numero"]
    desc = item["descricao"]
    
    print(f"📱 Enviando para {desc}...")
    
    mensagem = f"""🧪 TESTE DO SISTEMA

Olá! Esta é uma mensagem de teste do sistema de agendamentos da Navalha's Barber Club.

Número de destino: {desc}

Se você recebeu esta mensagem, por favor responda com "OK" para confirmar! ✅

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
            message_id = result.get('message', {}).get('id', 'N/A')
            status = result.get('message', {}).get('status', 'unknown')
            
            print(f"   ✅ Enviado! Status: {status}")
            print(f"   📋 ID: {message_id}")
            
            resultados.append({
                "numero": numero,
                "descricao": desc,
                "sucesso": True,
                "message_id": message_id,
                "status": status
            })
        else:
            print(f"   ❌ Erro {response.status_code}: {response.text[:100]}")
            resultados.append({
                "numero": numero,
                "descricao": desc,
                "sucesso": False,
                "erro": response.text[:100]
            })
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        resultados.append({
            "numero": numero,
            "descricao": desc,
            "sucesso": False,
            "erro": str(e)
        })
    
    print()
    time.sleep(2)  # Espera 2 segundos entre envios

print("=" * 70)
print("RESUMO DOS ENVIOS")
print("=" * 70)
print()

for r in resultados:
    if r['sucesso']:
        print(f"✅ {r['descricao']}: Enviado (ID: {r.get('message_id')})")
    else:
        print(f"❌ {r['descricao']}: Falhou ({r.get('erro', 'Erro desconhecido')})")

print()
print("=" * 70)
print("AGORA VERIFIQUE:")
print("=" * 70)
print("1. Veja no WhatsApp da barbearia (47) 9155-7386")
print("2. Confira quantos ticks cada mensagem tem:")
print("   • 1 tick (✓) = Não entregue")
print("   • 2 ticks (✓✓) = Entregue mas não lida")
print("   • 2 ticks azuis = Lida")
print()
print("3. Se algum número respondeu ou tem 2 ticks, esse é válido!")
print("=" * 70)

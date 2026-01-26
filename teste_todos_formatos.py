import requests

WHAPI_TOKEN = "OxR8uL8Hjf5Usq7KzCdbE84xgEuT2Ibr"
WHAPI_URL = "https://gate.whapi.cloud"

def testar_formato(numero: str, descricao: str):
    """Testa verificação de contato e envio de mensagem"""
    print(f"\n{'=' * 70}")
    print(f"📱 {descricao}: {numero}")
    print('=' * 70)
    
    headers = {
        "Authorization": f"Bearer {WHAPI_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # 1. Verificar contato
    print(f"\n1️⃣ Verificando contato /contacts/{numero}...")
    url_contact = f"{WHAPI_URL}/contacts/{numero}"
    
    try:
        response = requests.get(url_contact, headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            tem_whats = data.get('is_whatsapp', False)
            print(f"   {'✅' if tem_whats else '❌'} is_whatsapp: {tem_whats}")
            if tem_whats:
                print(f"   Nome: {data.get('name', 'N/A')}")
                print(f"   ID: {data.get('id', 'N/A')}")
        else:
            print(f"   ❌ Erro: {response.text[:200]}")
    except Exception as e:
        print(f"   ⚠️ Exceção: {str(e)}")
    
    # 2. Tentar enviar mensagem teste
    print(f"\n2️⃣ Tentando enviar mensagem para {numero}...")
    url_msg = f"{WHAPI_URL}/messages/text"
    
    payload = {
        "to": numero,
        "body": f"🧪 Teste de formato - {descricao}"
    }
    
    try:
        response = requests.post(url_msg, json=payload, headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Enviado! ID: {data.get('id')}")
            print(f"   Chat ID: {data.get('chat_id')}")
            print(f"   Status: {data.get('status')}")
        elif response.status_code == 402:
            print(f"   ⚠️ Erro 402: Limite de trial excedido")
        else:
            print(f"   ❌ Erro: {response.text[:200]}")
    except Exception as e:
        print(f"   ⚠️ Exceção: {str(e)}")

# O painel WHAPI mostra: 4791557386 (10 dígitos)
# Testar diferentes formatos baseados nisso

print("=" * 70)
print("TESTE: Qual formato o WHAPI realmente aceita?")
print("Baseado no painel que mostra: 4791557386 (10 dígitos)")
print("=" * 70)

formatos = [
    ("4791557386", "10 dígitos (como no painel)"),
    ("554791557386", "12 dígitos (55 + 10)"),
    ("5547991557386", "13 dígitos (55 + 11)"),
    ("+554791557386", "12 dígitos com +"),
    ("+5547991557386", "13 dígitos com +"),
]

for numero, desc in formatos:
    testar_formato(numero, desc)

print("\n" + "=" * 70)
print("CONCLUSÃO")
print("=" * 70)
print("✅ O formato que funcionar no /contacts é o correto para usar")
print("✅ O WHAPI mostra 4791557386 no painel (10 dígitos, sem 55)")

"""
Verificar se as mensagens foram entregues (2 ticks)
"""
import requests
import time

WHAPI_TOKEN = "OxR8uL8Hjf5Usq7KzCdbE84xgEuT2Ibr"
WHAPI_URL = "https://gate.whapi.cloud"

headers = {
    "Authorization": f"Bearer {WHAPI_TOKEN}",
}

# IDs das mensagens enviadas (do teste anterior)
message_ids = [
    ("PsoTvoKwYt7KfEY-wPQFC74Q5Qo", "47991557386 (sem 55)"),
    ("Psq3BDKNb4FGZbM-wFYFC74Q5Qo", "5547991557386 (13 dígitos)"),
    ("PsortnZFQ.UbX2M-wHoFC_my78I", "(48) 99203-2706"),
]

print("=" * 70)
print("🔍 VERIFICANDO STATUS DE ENTREGA DAS MENSAGENS")
print("=" * 70)

time.sleep(2)  # Aguardar processamento

for msg_id, descricao in message_ids:
    print(f"\n{'=' * 70}")
    print(f"📱 {descricao}")
    print(f"   ID: {msg_id}")
    print('=' * 70)
    
    url = f"{WHAPI_URL}/messages/{msg_id}"
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            status = data.get('status', 'N/A')
            ack = data.get('ack', 'N/A')
            chat_id = data.get('chat_id', 'N/A')
            
            print(f"\n✅ Mensagem encontrada:")
            print(f"   Chat ID: {chat_id}")
            print(f"   Status: {status}")
            print(f"   ACK: {ack}")
            
            # Interpretar ACK
            if ack == 1:
                print(f"   ✓ 1 tick - Enviado ao servidor (não entregue)")
            elif ack == 2:
                print(f"   ✓✓ 2 ticks - ENTREGUE ao destinatário! ✅")
            elif ack == 3:
                print(f"   ✓✓ 3 ticks - LIDO pelo destinatário! 🔵")
            elif ack == 0 or ack == 'N/A':
                print(f"   ⏳ Aguardando confirmação...")
            else:
                print(f"   ❓ ACK desconhecido: {ack}")
        else:
            print(f"❌ Erro ao consultar: {response.status_code}")
            print(f"   {response.text[:200]}")
    except Exception as e:
        print(f"⚠️ Erro: {e}")

print("\n" + "=" * 70)
print("💡 INTERPRETAÇÃO DOS ACKS")
print("=" * 70)
print("""
ACK 0 ou N/A: Mensagem pendente (aguardando)
ACK 1: ✓ Enviado ao servidor WhatsApp (não entregue ainda)
ACK 2: ✓✓ Entregue ao dispositivo do destinatário
ACK 3: ✓✓ Lido pelo destinatário (marcado como lido)

Se ACK = 2 ou 3, o número TEM WhatsApp e a mensagem FOI ENTREGUE! ✅
""")
print("=" * 70)

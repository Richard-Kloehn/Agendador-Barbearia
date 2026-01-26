import requests
import time

WHAPI_TOKEN = "OxR8uL8Hjf5Usq7KzCdbE84xgEuT2Ibr"
WHAPI_URL = "https://gate.whapi.cloud"

headers = {
    "Authorization": f"Bearer {WHAPI_TOKEN}",
    "Content-Type": "application/json"
}

print("=" * 70)
print("TESTANDO ENVIO E VERIFICANDO STATUS DA MENSAGEM")
print("=" * 70)

# Enviar mensagem
numero = "5547991557386"
print(f"\n📤 Enviando mensagem para {numero}...")

payload = {
    "to": numero,
    "body": f"🧪 Teste FINAL - Verificando entrega {time.strftime('%H:%M:%S')}"
}

response = requests.post(f"{WHAPI_URL}/messages/text", json=payload, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    try:
        data = response.json()
        message_id = data.get('id')
        
        if message_id:
            print(f"\n✅ Mensagem enviada! ID: {message_id}")
            
            # Aguardar processamento
            print(f"\n⏳ Aguardando 3 segundos para processar...")
            time.sleep(3)
            
            # Consultar status da mensagem
            print(f"\n📋 Consultando status da mensagem...")
            url_status = f"{WHAPI_URL}/messages/{message_id}"
            
            response_status = requests.get(url_status, headers=headers)
            print(f"Status consulta: {response_status.status_code}")
            
            if response_status.status_code == 200:
                msg_data = response_status.json()
                print(f"\n📊 Detalhes da mensagem:")
                print(f"   ID: {msg_data.get('id')}")
                print(f"   Status: {msg_data.get('status')}")
                print(f"   Chat ID: {msg_data.get('chat_id')}")
                print(f"   From Me: {msg_data.get('from_me')}")
                print(f"   Type: {msg_data.get('type')}")
                print(f"   Timestamp: {msg_data.get('timestamp')}")
                
                # Verificar ACKs
                ack = msg_data.get('ack')
                if ack:
                    print(f"\n✅ ACK (confirmação):")
                    print(f"   Ack: {ack}")
                    print(f"   Significado:")
                    print(f"      1 = Enviado ao servidor")
                    print(f"      2 = Entregue ao destinatário (✓✓)")
                    print(f"      3 = Lido pelo destinatário (✓✓ azul)")
                else:
                    print(f"\n⚠️ Sem ACK ainda")
            else:
                print(f"❌ Erro ao consultar status: {response_status.text}")
        else:
            print("⚠️ Resposta sem message ID")
    except Exception as e:
        print(f"⚠️ Erro ao processar resposta: {e}")

print("\n" + "=" * 70)
print("LISTA DE MENSAGENS RECENTES")
print("=" * 70)

# Listar mensagens recentes do chat
print(f"\n📬 Consultando mensagens do chat {numero}...")
url_messages = f"{WHAPI_URL}/messages/list"
params = {
    "chat_id": f"{numero}@s.whatsapp.net",
    "count": 5
}

response_list = requests.get(url_messages, headers=headers, params=params)
print(f"Status: {response_list.status_code}")

if response_list.status_code == 200:
    try:
        data = response_list.json()
        messages = data.get('messages', [])
        
        if messages:
            print(f"\n✅ {len(messages)} mensagens encontradas:")
            for msg in messages:
                status = msg.get('status', 'N/A')
                ack = msg.get('ack', 'N/A')
                body = msg.get('text', {}).get('body', 'N/A')[:50]
                print(f"   • {msg.get('id')} - Status: {status} - ACK: {ack}")
                print(f"     Texto: {body}")
        else:
            print("⚠️ Nenhuma mensagem encontrada")
    except Exception as e:
        print(f"⚠️ Erro: {e}")
else:
    print(f"Response: {response_list.text[:300]}")

print("\n" + "=" * 70)

import requests
import os
import json
import base64
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
import time

load_dotenv()

EVOLUTION_API_URL = os.getenv('EVOLUTION_API_URL')
EVOLUTION_API_KEY = os.getenv('EVOLUTION_API_KEY')
INSTANCE_NAME = os.getenv('EVOLUTION_INSTANCE_NAME', 'barbearia')

headers = {
    'apikey': EVOLUTION_API_KEY
}

print("=" * 70)
print("FORÇAR CONEXÃO E OBTER QR CODE")
print("=" * 70)
print(f"✅ API URL: {EVOLUTION_API_URL}")
print(f"✅ Instância: {INSTANCE_NAME}")
print()

# 1. Restart da instância para gerar novo QR Code
print("🔄 Reiniciando instância...")
try:
    response = requests.put(
        f"{EVOLUTION_API_URL}/instance/restart/{INSTANCE_NAME}",
        headers=headers,
        timeout=30
    )
    print(f"📡 Status HTTP: {response.status_code}")
    if response.status_code in [200, 201]:
        print("✅ Instância reiniciada")
    else:
        print(f"⚠️  Resposta: {response.text}")
except Exception as e:
    print(f"⚠️  Erro: {e}")

print()
print("⏳ Aguardando 10 segundos para gerar QR Code...")
time.sleep(10)

# 2. Buscar QR Code
print()
print("🔍 Buscando QR Code...")
for tentativa in range(1, 6):
    print(f"\n   Tentativa {tentativa}/5...")
    try:
        response = requests.get(
            f"{EVOLUTION_API_URL}/instance/connect/{INSTANCE_NAME}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if 'base64' in data and data['base64']:
                print("\n🎉 QR CODE GERADO COM SUCESSO!")
                
                # Salvar imagem
                qr_data = data['base64']
                if ',' in qr_data:
                    qr_data = qr_data.split(',')[1]
                
                qr_bytes = base64.b64decode(qr_data)
                qr_image = Image.open(BytesIO(qr_bytes))
                
                qr_path = "qrcode_whatsapp.png"
                qr_image.save(qr_path)
                
                print(f"\n💾 QR Code salvo: {qr_path}")
                print(f"🌐 Caminho: {os.path.abspath(qr_path)}")
                print()
                print("=" * 70)
                print("📱 ESCANEAR AGORA COM O WHATSAPP:")
                print("=" * 70)
                print("1. Abra WhatsApp no celular (47 99155-7386)")
                print("2. Menu (⋮) > 'Aparelhos conectados'")
                print("3. 'Conectar um aparelho'")
                print("4. Escaneie o QR Code")
                print()
                print("⏱️  Válido por alguns minutos!")
                print("=" * 70)
                
                # Abrir imagem
                try:
                    import webbrowser
                    webbrowser.open(os.path.abspath(qr_path))
                    print("\n🖼️  Imagem aberta automaticamente!")
                except:
                    pass
                
                break
                
            elif data.get('count') == 0:
                print(f"   ⏳ QR Code ainda não gerado (count: 0)")
                if tentativa < 5:
                    print("   Aguardando 5 segundos...")
                    time.sleep(5)
            else:
                print(f"   📋 Resposta: {json.dumps(data, indent=2)}")
                if tentativa < 5:
                    time.sleep(5)
        else:
            print(f"   ❌ Status {response.status_code}: {response.text}")
            if tentativa < 5:
                time.sleep(5)
                
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        if tentativa < 5:
            time.sleep(5)
else:
    print("\n❌ Não foi possível gerar QR Code após 5 tentativas")
    print("\n💡 Possíveis soluções:")
    print("   1. Verifique se o Redis está configurado no Railway")
    print("   2. Aguarde mais alguns minutos e tente novamente")
    print("   3. Delete e recrie a instância")

print()

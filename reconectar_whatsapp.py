import requests
import os
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
print("RECONECTAR WHATSAPP - EVOLUTION API")
print("=" * 70)
print(f"✅ API URL: {EVOLUTION_API_URL}")
print(f"✅ Instância: {INSTANCE_NAME}")
print()

# 1. Deletar instância antiga
print("🗑️  Deletando instância antiga...")
try:
    response = requests.delete(
        f"{EVOLUTION_API_URL}/instance/delete/{INSTANCE_NAME}",
        headers=headers,
        timeout=30
    )
    print(f"📡 Status HTTP: {response.status_code}")
    if response.status_code in [200, 201, 404]:
        print("✅ Instância deletada/não existia")
    else:
        print(f"⚠️  Resposta: {response.text}")
except Exception as e:
    print(f"⚠️  Erro ao deletar (pode não existir): {e}")

print()
print("⏳ Aguardando 5 segundos...")
time.sleep(5)

# 2. Criar nova instância
print()
print("🔄 Criando nova instância...")
data = {
    "instanceName": INSTANCE_NAME,
    "integration": "WHATSAPP-BAILEYS",
    "qrcode": True
}

try:
    response = requests.post(
        f"{EVOLUTION_API_URL}/instance/create",
        headers=headers,
        json=data,
        timeout=30
    )
    print(f"📡 Status HTTP: {response.status_code}")
    
    if response.status_code in [200, 201]:
        result = response.json()
        print("\n✅ INSTÂNCIA CRIADA COM SUCESSO!")
        print(f"Status: {result.get('instance', {}).get('status', 'desconhecido')}")
    else:
        print(f"❌ Erro: {response.text}")
        exit(1)
except Exception as e:
    print(f"❌ Erro: {e}")
    exit(1)

# 3. Conectar ao WhatsApp (obter QR)
print()
print("=" * 70)
print("OBTENDO QR CODE")
print("=" * 70)
print("⏳ Aguardando 5 segundos para gerar QR...")
time.sleep(5)

try:
    response = requests.get(
        f"{EVOLUTION_API_URL}/instance/connect/{INSTANCE_NAME}",
        headers=headers,
        timeout=30
    )
    print(f"📡 Status HTTP: {response.status_code}")
    
    result = response.json()
    
    if 'base64' in result:
        print("\n✅ QR CODE GERADO!")
        print("\n" + "=" * 70)
        print("📱 ESCANEAR COM WHATSAPP")
        print("=" * 70)
        print("1. Abra o WhatsApp no celular da barbearia")
        print("2. Toque em 'Mais opções' (⋮) > 'Aparelhos conectados'")
        print("3. Toque em 'Conectar um aparelho'")
        print("4. Aponte a câmera para o QR Code abaixo:")
        print()
        
        # Salvar imagem do QR Code
        import base64
        from io import BytesIO
        from PIL import Image
        
        qr_data = result['base64'].split(',')[1] if ',' in result['base64'] else result['base64']
        qr_bytes = base64.b64decode(qr_data)
        qr_image = Image.open(BytesIO(qr_bytes))
        
        # Salvar arquivo
        qr_path = "qrcode_whatsapp.png"
        qr_image.save(qr_path)
        print(f"💾 QR Code salvo em: {qr_path}")
        print()
        
        # Mostrar QR Code no terminal
        try:
            import qrcode
            qr_code = result.get('code', '')
            if qr_code:
                qr = qrcode.QRCode()
                qr.add_data(qr_code)
                qr.make()
                qr.print_ascii(invert=True)
        except:
            pass
            
        print()
        print(f"🌐 Ou abra o arquivo: {os.path.abspath(qr_path)}")
        print()
        print("⏱️  QR Code expira em alguns minutos!")
        print()
        
    else:
        print(f"\n📋 Resposta: {result}")
        if result.get('count', 0) == 0:
            print("\n⚠️  QR Code ainda não disponível")
            print("💡 Aguarde alguns segundos e execute novamente")
        
except Exception as e:
    print(f"❌ Erro: {e}")

print()
print("=" * 70)

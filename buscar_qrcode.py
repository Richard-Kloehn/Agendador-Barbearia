import requests
import os
import base64
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

load_dotenv()

EVOLUTION_API_URL = os.getenv('EVOLUTION_API_URL')
EVOLUTION_API_KEY = os.getenv('EVOLUTION_API_KEY')
INSTANCE_NAME = os.getenv('EVOLUTION_INSTANCE_NAME', 'barbearia')

headers = {
    'apikey': EVOLUTION_API_KEY
}

print("=" * 70)
print("BUSCAR QR CODE - EVOLUTION API")
print("=" * 70)
print(f"✅ API URL: {EVOLUTION_API_URL}")
print(f"✅ Instância: {INSTANCE_NAME}")
print()

# Tentar endpoint fetchInstances
print("🔍 Buscando informações da instância...")
try:
    response = requests.get(
        f"{EVOLUTION_API_URL}/instance/fetchInstances?instanceName={INSTANCE_NAME}",
        headers=headers,
        timeout=30
    )
    print(f"📡 Status HTTP: {response.status_code}")
    
    if response.status_code == 200:
        instances = response.json()
        print(f"\n📋 Instâncias encontradas: {len(instances)}")
        
        for inst in instances:
            if inst.get('instance', {}).get('instanceName') == INSTANCE_NAME:
                print(f"\n✅ Instância: {INSTANCE_NAME}")
                print(f"   Estado: {inst.get('instance', {}).get('state')}")
                
                # Verificar se tem QR Code
                qrcode_info = inst.get('qrcode', {})
                if qrcode_info and qrcode_info.get('base64'):
                    print("\n🎉 QR CODE ENCONTRADO!")
                    
                    # Salvar imagem do QR Code
                    qr_data = qrcode_info['base64']
                    if ',' in qr_data:
                        qr_data = qr_data.split(',')[1]
                    
                    qr_bytes = base64.b64decode(qr_data)
                    qr_image = Image.open(BytesIO(qr_bytes))
                    
                    qr_path = "qrcode_whatsapp.png"
                    qr_image.save(qr_path)
                    
                    print(f"\n💾 QR Code salvo em: {qr_path}")
                    print(f"🌐 Abra: {os.path.abspath(qr_path)}")
                    print()
                    print("=" * 70)
                    print("📱 COMO ESCANEAR:")
                    print("=" * 70)
                    print("1. Abra o WhatsApp no celular (47 99155-7386)")
                    print("2. Toque em ⋮ (3 pontinhos) > 'Aparelhos conectados'")
                    print("3. Toque em 'Conectar um aparelho'")
                    print("4. Escaneie o QR Code do arquivo qrcode_whatsapp.png")
                    print()
                    print("⏱️  QR Code expira em alguns minutos!")
                    print("=" * 70)
                    
                    # Abrir imagem automaticamente
                    try:
                        import webbrowser
                        webbrowser.open(os.path.abspath(qr_path))
                        print("\n🖼️  Arquivo aberto automaticamente!")
                    except:
                        pass
                else:
                    print(f"\n⚠️  QR Code ainda não disponível")
                    print(f"   Count: {qrcode_info.get('count', 0)}")
                    print(f"   Estado: {inst.get('instance', {}).get('state')}")
                break
        else:
            print(f"\n❌ Instância '{INSTANCE_NAME}' não encontrada")
    else:
        print(f"❌ Erro: {response.text}")
        
except Exception as e:
    print(f"❌ Erro: {e}")

print()

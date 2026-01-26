"""
Script para conectar WhatsApp via QR Code
Execute: python conectar_whatsapp_evolution.py
"""

import requests
import os
from dotenv import load_dotenv
import json
import base64
from PIL import Image
from io import BytesIO

load_dotenv()

def conectar_whatsapp():
    """Obtém QR Code para conectar WhatsApp"""
    
    api_url = os.getenv('EVOLUTION_API_URL', '').rstrip('/')
    api_key = os.getenv('EVOLUTION_API_KEY', '')
    instance_name = os.getenv('EVOLUTION_INSTANCE_NAME', 'barbearia')
    
    print("=" * 70)
    print("CONECTAR WHATSAPP - EVOLUTION API")
    print("=" * 70)
    
    if not api_url or not api_key:
        print("❌ Configurações não encontradas!")
        return
    
    print(f"✅ API URL: {api_url}")
    print(f"✅ Instância: {instance_name}")
    print()
    
    headers = {
        'apikey': api_key
    }
    
    print("🔄 Obtendo QR Code...")
    print()
    
    try:
        response = requests.get(
            f'{api_url}/instance/connect/{instance_name}',
            headers=headers,
            timeout=30
        )
        
        print(f"📡 Status HTTP: {response.status_code}\n")
        
        if response.status_code == 200:
            result = response.json()
            
            # Verificar se já está conectado
            if result.get('instance', {}).get('state') == 'open':
                print("✅ WHATSAPP JÁ ESTÁ CONECTADO!")
                print("\nPode testar o envio de mensagens agora!")
                return
            
            # Pegar QR Code
            if 'qrcode' in result:
                qrcode_data = result['qrcode']
                
                # Se for base64
                if 'base64' in qrcode_data:
                    print("📱 QR CODE GERADO!")
                    print("\n" + "=" * 70)
                    print("ESCANEIE COM O WHATSAPP DA BARBEARIA:")
                    print("=" * 70)
                    print("\n1. Abra o WhatsApp no celular da barbearia")
                    print("2. Vá em Configurações → Aparelhos conectados")
                    print("3. Toque em 'Conectar um aparelho'")
                    print("4. Escaneie o QR Code que vai abrir no navegador\n")
                    
                    # Salvar QR Code como imagem
                    try:
                        base64_string = qrcode_data['base64'].split(',')[1] if ',' in qrcode_data['base64'] else qrcode_data['base64']
                        image_data = base64.b64decode(base64_string)
                        image = Image.open(BytesIO(image_data))
                        image.save('qrcode_whatsapp.png')
                        print("✅ QR Code salvo em: qrcode_whatsapp.png")
                        print("   Abra esse arquivo para escanear!")
                    except:
                        pass
                    
                    # Tentar abrir no navegador
                    qr_url = f"{api_url}/instance/qrcode/{instance_name}"
                    print(f"\n🌐 Ou acesse no navegador:")
                    print(f"   {qr_url}")
                    print(f"   (Adicione header: apikey: {api_key})")
                    
                elif 'code' in qrcode_data:
                    print("📱 CÓDIGO PARA PAREAMENTO:")
                    print(qrcode_data['code'])
                    print("\nUse esse código no WhatsApp para conectar")
                    
            else:
                print("📋 Resposta da API:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
        else:
            print(f"❌ Erro: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏱️ Timeout - A API pode estar ocupada")
        print("💡 Tente novamente")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    conectar_whatsapp()

"""
Script para criar instância na Evolution API
Execute: python criar_instancia_evolution.py
"""

import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

def criar_instancia():
    """Cria a instância do WhatsApp na Evolution API"""
    
    api_url = os.getenv('EVOLUTION_API_URL', '').rstrip('/')
    api_key = os.getenv('EVOLUTION_API_KEY', '')
    instance_name = os.getenv('EVOLUTION_INSTANCE_NAME', 'barbearia')
    
    print("=" * 70)
    print("CRIAR INSTÂNCIA - EVOLUTION API")
    print("=" * 70)
    
    if not api_url or not api_key:
        print("❌ Configurações não encontradas!")
        return
    
    print(f"✅ API URL: {api_url}")
    print(f"✅ Instância: {instance_name}")
    print()
    
    headers = {
        'apikey': api_key,
        'Content-Type': 'application/json'
    }
    
    # Criar instância
    payload = {
        "instanceName": instance_name,
        "qrcode": True,
        "integration": "WHATSAPP-BAILEYS"
    }
    
    print("🔄 Criando instância...")
    
    try:
        response = requests.post(
            f'{api_url}/instance/create',
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"📡 Status HTTP: {response.status_code}\n")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print("✅ INSTÂNCIA CRIADA COM SUCESSO!")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print("\n" + "=" * 70)
            print("PRÓXIMO PASSO: Conectar o WhatsApp")
            print("=" * 70)
            print("\nExecute: python conectar_whatsapp_evolution.py")
        else:
            error = response.json()
            if 'Instance already exists' in str(error) or 'já existe' in str(error):
                print("✅ Instância já existe! Pode seguir para conectar.")
                print("\nExecute: python conectar_whatsapp_evolution.py")
            else:
                print(f"❌ Erro: {error}")
                
    except requests.exceptions.Timeout:
        print("⏱️ Timeout - A API pode estar iniciando ainda")
        print("💡 Aguarde 1-2 minutos e tente novamente")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    criar_instancia()

"""
Script de teste para Evolution API
Execute: python teste_evolution_api.py
"""

import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

def testar_evolution_api():
    """Testa configuração e envio via Evolution API"""
    
    api_url = os.getenv('EVOLUTION_API_URL', '').rstrip('/')
    api_key = os.getenv('EVOLUTION_API_KEY', '')
    instance_name = os.getenv('EVOLUTION_INSTANCE_NAME', 'barbearia')
    
    print("=" * 70)
    print("TESTE DE CONFIGURAÇÃO - EVOLUTION API")
    print("=" * 70)
    
    if not api_url:
        print("❌ EVOLUTION_API_URL não configurada!")
        print("   Configure no arquivo .env")
        return
    
    if not api_key:
        print("❌ EVOLUTION_API_KEY não configurada!")
        print("   Configure no arquivo .env")
        return
    
    print(f"✅ API URL: {api_url}")
    print(f"✅ API Key: {api_key[:10]}...{api_key[-4:]}")
    print(f"✅ Instância: {instance_name}")
    print()
    
    headers = {
        'apikey': api_key,
        'Content-Type': 'application/json'
    }
    
    # 1. Verificar status da instância
    print("=" * 70)
    print("1. VERIFICANDO STATUS DA INSTÂNCIA")
    print("=" * 70)
    
    try:
        response = requests.get(
            f'{api_url}/instance/connectionState/{instance_name}',
            headers=headers,
            timeout=10
        )
        
        print(f"📡 Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            state = result.get('instance', {}).get('state')
            if state == 'open':
                print("\n✅ INSTÂNCIA CONECTADA!")
            else:
                print(f"\n⚠️ Estado da instância: {state}")
                print("   Pode precisar escanear QR Code novamente")
        else:
            print(f"❌ Erro: {response.text}")
            print("\n💡 Dica: A instância pode não existir ainda. Crie ela primeiro!")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        print("\n💡 Verifique se a URL está correta e a API está online")
        return
    
    print()
    
    # 2. Perguntar se quer testar envio
    resposta = input("Deseja testar o envio de mensagem? (s/n): ").lower()
    
    if resposta != 's':
        print("\nTeste finalizado!")
        return
    
    numero = input("\nDigite o número para teste (ex: 47992849526): ").strip()
    
    if not numero:
        print("❌ Número não fornecido")
        return
    
    # Formatar número
    numero_limpo = ''.join(filter(str.isdigit, numero))
    if not numero_limpo.startswith('55'):
        numero_limpo = '55' + numero_limpo
    
    print(f"\n📱 Número formatado: {numero_limpo}")
    
    # 3. Enviar mensagem de teste
    print()
    print("=" * 70)
    print("2. ENVIANDO MENSAGEM DE TESTE")
    print("=" * 70)
    
    mensagem = """Olá! 👋

Esta é uma mensagem de TESTE da Evolution API.

Se você recebeu, significa que está tudo funcionando! ✅

Navalha's Barber Club 💈"""
    
    payload = {
        'number': numero_limpo,
        'text': mensagem
    }
    
    print(f"\n📤 Enviando para: {numero_limpo}")
    print(f"📝 Mensagem:\n{mensagem}\n")
    
    try:
        response = requests.post(
            f'{api_url}/message/sendText/{instance_name}',
            json=payload,
            headers=headers,
            timeout=60
        )
        
        print(f"📡 Status HTTP: {response.status_code}")
        print(f"📄 Resposta:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        if response.status_code in [200, 201]:
            print("\n✅ MENSAGEM ENVIADA COM SUCESSO!")
            print("👉 Verifique o WhatsApp do destinatário!")
        else:
            print(f"\n❌ Falha no envio")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    testar_evolution_api()

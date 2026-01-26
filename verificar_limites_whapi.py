"""
Script para verificar limites do plano WHAPI
Execute: python verificar_limites_whapi.py
"""

import requests
import os
from dotenv import load_dotenv
import json

# Carregar variáveis de ambiente
load_dotenv()

def verificar_limites():
    """Verifica os limites do plano WHAPI"""
    
    api_url = os.getenv('WHAPI_API_URL', 'https://gate.whapi.cloud').rstrip('/')
    api_token = os.getenv('WHAPI_API_TOKEN', '')
    
    print("=" * 60)
    print("VERIFICAÇÃO DE LIMITES DO PLANO WHAPI")
    print("=" * 60)
    
    if not api_token:
        print("❌ ERRO: WHAPI_API_TOKEN não configurado!")
        return
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(
            f'{api_url}/limits',
            headers=headers,
            timeout=30
        )
        
        print(f"📡 Status HTTP: {response.status_code}\n")
        
        if response.status_code == 200:
            result = response.json()
            print("📋 LIMITES DO SEU PLANO:")
            print("=" * 60)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print("=" * 60)
        else:
            print(f"❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    verificar_limites()

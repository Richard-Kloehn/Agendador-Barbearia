"""
Script de teste para envio de mensagem via WHAPI
Execute: python teste_whapi.py
"""

import requests
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def testar_envio_whapi():
    """Testa envio de mensagem via WHAPI"""
    
    # Configurações
    api_url = os.getenv('WHAPI_API_URL', 'https://gate.whapi.cloud').rstrip('/')
    api_token = os.getenv('WHAPI_API_TOKEN', '')
    
    print("=" * 60)
    print("TESTE DE ENVIO WHAPI")
    print("=" * 60)
    
    if not api_token:
        print("❌ ERRO: WHAPI_API_TOKEN não configurado!")
        print("Configure no arquivo .env ou nas variáveis de ambiente")
        return
    
    print(f"✅ API URL: {api_url}")
    print(f"✅ Token: {api_token[:10]}...{api_token[-4:]}")
    print()
    
    # Solicitar número do cliente
    numero_input = input("Digite o número do cliente (ex: 47992849526 ou 11987654321): ").strip()
    
    if not numero_input:
        print("❌ Número não fornecido")
        return
    
    # Formatar número
    numero_limpo = ''.join(filter(str.isdigit, numero_input))
    if not numero_limpo.startswith('55'):
        numero_limpo = '55' + numero_limpo
    
    print(f"\n📱 Número original: {numero_input}")
    print(f"📱 Número formatado: {numero_limpo}")
    print()
    
    # Mensagem de teste
    mensagem = """Boa tarde! ✂️

Esta é uma mensagem de TESTE do sistema de agendamentos.

Se você recebeu esta mensagem, o sistema está funcionando corretamente! ✅

Navalha's Barber Club 💈"""
    
    print("📝 Mensagem:")
    print(mensagem)
    print()
    
    # Preparar requisição
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'typing_time': 0,
        'to': numero_limpo,
        'body': mensagem
    }
    
    url = f'{api_url}/messages/text'
    
    print("=" * 60)
    print("ENVIANDO REQUISIÇÃO...")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Payload: {payload}")
    print()
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=60
        )
        
        print(f"📡 Status HTTP: {response.status_code}")
        print(f"📡 Headers da resposta: {dict(response.headers)}")
        print()
        
        # Mostrar resposta completa
        print("=" * 60)
        print("RESPOSTA COMPLETA:")
        print("=" * 60)
        try:
            result = response.json()
            import json
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # Verificar se tem erro na resposta
            if 'error' in result:
                print(f"\n❌ ERRO NA API: {result['error']}")
            elif 'message' in result and result.get('sent') == False:
                print(f"\n❌ FALHA NO ENVIO: {result['message']}")
            elif result.get('sent') == True or 'id' in result:
                print(f"\n✅ MENSAGEM ENVIADA COM SUCESSO!")
                if 'id' in result:
                    print(f"   ID: {result['id']}")
            else:
                print(f"\n⚠️ Resposta inesperada - verifique acima")
                
        except Exception as e:
            print(f"Resposta (texto): {response.text}")
            print(f"❌ Erro ao processar JSON: {e}")
        
        print()
        
        if response.status_code in [200, 201]:
            print("✅ Requisição bem-sucedida (HTTP 200/201)")
            print("\n👉 AGORA VERIFIQUE O WHATSAPP DO CLIENTE!")
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT: A API não respondeu em 60 segundos")
    except requests.exceptions.RequestException as e:
        print(f"❌ ERRO DE CONEXÃO: {e}")
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {e}")

if __name__ == '__main__':
    testar_envio_whapi()

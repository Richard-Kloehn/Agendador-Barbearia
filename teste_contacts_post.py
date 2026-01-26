import requests
import json

WHAPI_TOKEN = "OxR8uL8Hjf5Usq7KzCdbE84xgEuT2Ibr"
WHAPI_URL = "https://gate.whapi.cloud"

def validar_numeros(numeros_lista):
    """Valida números usando POST /contacts da WHAPI"""
    headers = {
        "Authorization": f"Bearer {WHAPI_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    url = f"{WHAPI_URL}/contacts"
    
    payload = {
        "force_check": False,
        "contacts": numeros_lista
    }
    
    print(f"📤 Enviando requisição para {url}")
    print(f"   Números: {numeros_lista}")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"\n✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n📋 Resposta completa:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            print(f"\n{'=' * 70}")
            print("RESULTADO DA VALIDAÇÃO")
            print('=' * 70)
            
            if isinstance(data, list):
                for resultado in data:
                    numero = resultado.get('input', 'N/A')
                    status = resultado.get('status', 'N/A')
                    wa_id = resultado.get('wa_id', 'N/A')
                    
                    print(f"\n📱 Número: {numero}")
                    print(f"   Status: {status}")
                    
                    if status == 'valid':
                        print(f"   ✅ VÁLIDO!")
                        print(f"   WhatsApp ID: {wa_id}")
                        print(f"   → Use este Chat ID: {wa_id}")
                    else:
                        print(f"   ❌ INVÁLIDO - Número não tem WhatsApp")
            else:
                print("⚠️ Formato de resposta inesperado")
                
        else:
            print(f"❌ Erro na requisição:")
            print(response.text)
            
    except Exception as e:
        print(f"⚠️ Exceção: {str(e)}")

print("=" * 70)
print("VALIDAÇÃO DE NÚMEROS COM POST /contacts")
print("=" * 70)

# Testar os números problemáticos em diferentes formatos
print("\n🧪 TESTE 1: Números com 13 dígitos (formato atual)")
numeros_teste_1 = [
    "5547991557386",  # Barbearia
    "5548992032706",  # Cliente 1
    "5547992849526",  # Cliente 2
]
validar_numeros(numeros_teste_1)

print("\n\n" + "=" * 70)
print("🧪 TESTE 2: Números com 12 dígitos (sem um 9)")
numeros_teste_2 = [
    "554791557386",   # Barbearia
    "554892032706",   # Cliente 1
    "554792849526",   # Cliente 2
]
validar_numeros(numeros_teste_2)

print("\n\n" + "=" * 70)
print("🧪 TESTE 3: Número exemplo do suporte WHAPI")
numeros_teste_3 = [
    "559281723241",   # Exemplo DDD 92 do suporte
]
validar_numeros(numeros_teste_3)

print("\n" + "=" * 70)
print("💡 CONCLUSÃO")
print("=" * 70)
print("O método POST /contacts retorna o wa_id correto para cada número.")
print("Sempre use o wa_id retornado para enviar mensagens!")
print("=" * 70)

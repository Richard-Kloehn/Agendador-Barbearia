import requests

# Configuração WHAPI
WHAPI_TOKEN = "OxR8uL8Hjf5Usq7KzCdbE84xgEuT2Ibr"
WHAPI_URL = "https://gate.whapi.cloud"

def verificar_numero_checkphones(numero: str):
    """Usa o método checkPhones recomendado pelo suporte WHAPI"""
    headers = {
        "Authorization": f"Bearer {WHAPI_TOKEN}",
        "Content-Type": "application/json"
    }
    
    url = f"{WHAPI_URL}/checkPhones"
    
    # Testar diferentes formatos
    formatos = [
        numero,
        f"+{numero}" if not numero.startswith('+') else numero,
        numero.replace('+', '')
    ]
    
    for formato in formatos:
        payload = {
            "phones": [formato]
        }
        
        try:
            print(f"\n🔍 Testando formato: {formato}")
            response = requests.post(url, json=payload, headers=headers)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Response: {data}")
                
                if data and len(data) > 0:
                    resultado = data[0]
                    if resultado.get('exists'):
                        print(f"   ✅ EXISTE NO WHATSAPP!")
                        print(f"   WhatsApp ID: {resultado.get('id')}")
                        return resultado
                    else:
                        print(f"   ❌ Não existe no WhatsApp")
            else:
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   ⚠️ Erro: {str(e)}")
    
    return None

print("=" * 70)
print("TESTE checkPhones - Método recomendado pelo WHAPI")
print("=" * 70)

# Testar os números problemáticos
numeros = [
    ("5547991557386", "Barbearia - formato atual"),
    ("554791557386", "Barbearia - sem um 9"),
    ("47991557386", "Barbearia - sem código país"),
    ("5548992032706", "Cliente 1 - formato atual"),
    ("554892032706", "Cliente 1 - sem um 9"),
]

for numero, descricao in numeros:
    print(f"\n{'=' * 70}")
    print(f"📱 {descricao}")
    print(f"   Número: {numero}")
    print('=' * 70)
    
    resultado = verificar_numero_checkphones(numero)
    
    if resultado:
        print(f"\n✅ ENCONTRADO! Formato correto para usar: {resultado.get('id')}")

print("\n" + "=" * 70)

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
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            contacts = data.get('contacts', [])
            
            print(f"\n{'=' * 70}")
            print(f"VALIDAÇÃO DE {len(contacts)} NÚMEROS")
            print('=' * 70)
            
            for resultado in contacts:
                numero = resultado.get('input', 'N/A')
                status = resultado.get('status', 'N/A')
                wa_id = resultado.get('wa_id', 'N/A')
                
                print(f"\n📱 Input: {numero}")
                
                if status == 'valid':
                    # Extrair apenas o número (sem @s.whatsapp.net)
                    numero_correto = wa_id.replace('@s.whatsapp.net', '')
                    print(f"   ✅ VÁLIDO!")
                    print(f"   Chat ID correto: {wa_id}")
                    print(f"   Número normalizado: {numero_correto}")
                    
                    # Mostrar diferença
                    if numero != numero_correto:
                        print(f"   🔧 WHAPI corrigiu: {numero} → {numero_correto}")
                else:
                    print(f"   ❌ INVÁLIDO - Número não tem WhatsApp")
                    
            return contacts
        else:
            print(f"❌ Erro: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"⚠️ Erro: {str(e)}")
        return None

print("=" * 70)
print("🔍 DESCOBRINDO O FORMATO CORRETO COM WHAPI")
print("=" * 70)

# Números do sistema com 13 dígitos
numeros_sistema = [
    "5547991557386",
    "5548992032706",
    "5547992849526",
]

print("\n📋 Números atuais no sistema (13 dígitos):")
for num in numeros_sistema:
    print(f"   • {num}")

contacts = validar_numeros(numeros_sistema)

if contacts:
    print("\n\n" + "=" * 70)
    print("💡 CONCLUSÃO IMPORTANTE")
    print("=" * 70)
    print("\n✅ DESCOBERTA:")
    print("   • WHAPI normaliza automaticamente para 12 dígitos")
    print("   • Para DDD 47 e 48 (SC), remove o 9 extra")
    print("   • Formato correto: 55 + DDD + 8 dígitos")
    print("\n📝 CORREÇÕES NECESSÁRIAS:")
    print("   • 5547991557386 → 554791557386")
    print("   • 5548992032706 → 554892032706")
    print("   • 5547992849526 → 554792849526")
    print("\n🔧 AÇÃO:")
    print("   • Atualizar função formatar_numero() para retornar 12 dígitos")
    print("   • Ou usar POST /contacts antes de enviar para obter wa_id correto")
    print("   • Sempre enviar para o Chat ID retornado pela API")

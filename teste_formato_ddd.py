import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Configuração WHAPI
WHAPI_TOKEN = "OxR8uL8Hjf5Usq7KzCdbE84xgEuT2Ibr"
WHAPI_URL = "https://gate.whapi.cloud"

def formatar_numero_teste(numero: str) -> str:
    """Testa formatação com as regras do WHAPI"""
    numero_limpo = ''.join(filter(str.isdigit, numero))
    
    if not numero_limpo.startswith('55'):
        numero_limpo = '55' + numero_limpo
    
    if len(numero_limpo) >= 4:
        ddd = numero_limpo[2:4]
        ddds_com_9 = ['11', '12', '13', '14', '15', '16', '17', '18', '19', 
                      '21', '22', '24', '27', '28']
        
        if len(numero_limpo) == 13:
            if ddd not in ddds_com_9:
                if numero_limpo[4] == '9':
                    numero_limpo = numero_limpo[:4] + numero_limpo[5:]
                    print(f"   ➜ Removido '9' para DDD {ddd}")
    
    return numero_limpo

def verificar_numero_whapi(numero_formatado: str):
    """Verifica se número tem WhatsApp usando API WHAPI"""
    headers = {
        "Authorization": f"Bearer {WHAPI_TOKEN}"
    }
    
    url = f"{WHAPI_URL}/contacts/{numero_formatado}"
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            tem_whatsapp = data.get('is_whatsapp', False)
            nome = data.get('name', 'N/A')
            
            if tem_whatsapp:
                print(f"   ✅ TEM WhatsApp! Nome: {nome}")
                return True
            else:
                print(f"   ❌ NÃO tem WhatsApp")
                return False
        else:
            print(f"   ⚠️ Erro na consulta: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ⚠️ Erro: {str(e)}")
        return False

print("=" * 60)
print("TESTE DE FORMATAÇÃO - REGRAS WHAPI PARA BRASIL")
print("=" * 60)

# Números para testar
numeros_teste = [
    ("4791557386", "47", "SC - Barbearia (sem 9 inicial)"),
    ("47991557386", "47", "SC - Barbearia (com 9 inicial)"),
    ("48992032706", "48", "SC - Cliente"),
    ("11987654321", "11", "SP - deve manter o 9"),
]

print("\n📋 Testando formatação:\n")

for numero_original, ddd, descricao in numeros_teste:
    print(f"Número: {numero_original} (DDD {ddd} - {descricao})")
    numero_formatado = formatar_numero_teste(numero_original)
    print(f"   Formatado: {numero_formatado} ({len(numero_formatado)} dígitos)")
    verificar_numero_whapi(numero_formatado)
    print()

print("\n" + "=" * 60)
print("VERIFICAÇÃO DOS NÚMEROS ATUAIS NO SISTEMA")
print("=" * 60)

# Números que estão no limite de 5 chats
numeros_sistema = [
    "5547991557386",  # Original do sistema
    "5548992032706",
    "5547992849526",
]

print("\nNúmeros que estão nos 5 chats permitidos:\n")
for num in numeros_sistema:
    print(f"Sistema: {num}")
    ddd = num[2:4]
    print(f"   DDD: {ddd}")
    
    # Verificar se deveria ter ou não o 9
    ddds_com_9 = ['11', '12', '13', '14', '15', '16', '17', '18', '19', 
                  '21', '22', '24', '27', '28']
    
    if ddd in ddds_com_9:
        print(f"   ℹ️ DDD {ddd} DEVE ter 9 após o DDD")
    else:
        print(f"   ℹ️ DDD {ddd} NÃO deve ter 9 após o DDD")
    
    # Analisar estrutura
    if len(num) == 13 and num[4] == '9':
        print(f"   ⚠️ Tem 9 na posição 5: {num[:4]}|9|{num[5:]}")
        if ddd not in ddds_com_9:
            print(f"   🔧 Deveria ser: {num[:4]}{num[5:]}")
    
    verificar_numero_whapi(num)
    print()

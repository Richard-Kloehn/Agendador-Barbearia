"""
Teste final do sistema de WhatsApp com validação automática
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.whapi_service import WhapiService
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("🧪 TESTE FINAL - VALIDAÇÃO AUTOMÁTICA + ENVIO")
print("=" * 70)

# Inicializar serviço
whapi = WhapiService()

if not whapi.esta_configurado():
    print("❌ WHAPI não configurado!")
    sys.exit(1)

# Números para testar (com formatos variados)
numeros_teste = [
    ("47991557386", "Barbearia (sem 55)"),
    ("5547991557386", "Barbearia (13 dígitos)"),
    ("(48) 99203-2706", "Cliente 1 (formatado)"),
]

print("\n📋 Testando números:\n")

for numero, descricao in numeros_teste:
    print(f"{'=' * 70}")
    print(f"📱 {descricao}: {numero}")
    print('=' * 70)
    
    # 1. Validar número
    print(f"\n1️⃣ Validando número...")
    validacao = whapi.validar_numero_whatsapp(numero)
    
    print(f"\nResultado da validação:")
    print(f"   Válido: {validacao['valido']}")
    print(f"   WhatsApp ID: {validacao['wa_id']}")
    print(f"   Número normalizado: {validacao['numero']}")
    
    if validacao['valido']:
        print(f"\n2️⃣ Enviando mensagem de teste...")
        
        # Enviar com validar=False pois já validamos acima
        sucesso = whapi.enviar_mensagem(
            numero, 
            f"✅ Teste FINAL - Validação automática funcionando!\n\nNúmero testado: {numero}\nNúmero correto: {validacao['numero']}",
            validar=False  # Já validamos manualmente
        )
        
        if sucesso:
            print(f"\n✅ SUCESSO! Mensagem enviada e deve chegar com 2 ticks (✓✓)")
        else:
            print(f"\n❌ Falha no envio")
    else:
        print(f"\n⚠️ Número inválido - não enviando mensagem")
    
    print()

print("\n" + "=" * 70)
print("💡 RESUMO DO SISTEMA")
print("=" * 70)
print("""
✅ Sistema agora implementa:
   1. Validação automática via POST /contacts
   2. Normalização do número pela API WHAPI
   3. Uso do wa_id correto para envio
   4. Para DDD 47/48 (SC): formato correto é 12 dígitos (sem 9 extra)

📊 Fluxo de envio:
   1. Usuário fornece número (qualquer formato)
   2. Sistema chama validar_numero_whatsapp()
   3. WHAPI retorna wa_id normalizado (ex: 554791557386@s.whatsapp.net)
   4. Sistema extrai número correto (554791557386)
   5. Envia mensagem com formato correto
   6. Resultado: 2 ticks (✓✓) - mensagem entregue!

⚙️ Configuração:
   • Validação habilitada por padrão (validar=True)
   • Para desabilitar: enviar_mensagem(numero, msg, validar=False)
   • Recomendado: sempre usar validação para garantir entrega
""")
print("=" * 70)

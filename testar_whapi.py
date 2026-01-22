"""
Script de teste para integração whapi.cloud
============================================
Testa o envio de mensagens via whapi.cloud
"""

import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.whapi_service import WhapiService

def main():
    print("=" * 60)
    print("🧪 TESTE DE INTEGRAÇÃO WHAPI.CLOUD")
    print("=" * 60)
    
    # Criar instância do serviço
    whapi = WhapiService()
    
    # Verificar configuração
    print("\n📋 1. Verificando configuração...")
    if whapi.esta_configurado():
        print("   ✅ WHAPI_API_TOKEN: Configurado")
        print("   ✅ WHAPI_PHONE_ID: Configurado")
        print(f"   ✅ WHAPI_API_URL: {whapi.api_url}")
    else:
        print("   ❌ ERRO: whapi.cloud não está configurado!")
        print("\n   Configure as seguintes variáveis de ambiente:")
        print("   - WHAPI_API_TOKEN: Token da API do whapi.cloud")
        print("   - WHAPI_PHONE_ID: ID do canal/número no whapi.cloud")
        print("\n   Veja o guia: CONFIGURACAO_WHAPI.md")
        return
    
    # Verificar status do canal
    print("\n📡 2. Verificando status do canal...")
    status = whapi.verificar_status_canal()
    
    if 'erro' in status:
        print(f"   ⚠️ Não foi possível verificar: {status['erro']}")
    else:
        print("   ✅ Canal conectado e funcionando")
    
    # Solicitar número para teste
    print("\n📱 3. Teste de envio de mensagem")
    print("   Digite o número do destinatário (com DDD)")
    print("   Exemplo: 11987654321 ou (11) 98765-4321")
    
    numero = input("\n   Número: ").strip()
    
    if not numero:
        print("   ❌ Número não informado. Cancelando teste.")
        return
    
    # Criar mensagem de teste
    mensagem = """🧪 *Teste de Integração whapi.cloud*

Esta é uma mensagem de teste enviada automaticamente pelo sistema de agendamento da barbearia.

Se você recebeu esta mensagem, significa que:
✅ A integração com whapi.cloud está funcionando
✅ As mensagens automáticas estão ativas
✅ O sistema está pronto para uso

_Mensagem enviada em: 21/01/2026_"""
    
    # Enviar mensagem
    print("\n📤 4. Enviando mensagem de teste...")
    print(f"   Destinatário: {numero}")
    
    sucesso = whapi.enviar_mensagem(numero, mensagem)
    
    print("\n" + "=" * 60)
    if sucesso:
        print("✅ SUCESSO! Mensagem enviada com sucesso!")
        print("\n📱 Verifique o WhatsApp do número informado.")
        print("=" * 60)
    else:
        print("❌ FALHA! Não foi possível enviar a mensagem.")
        print("\n🔍 Possíveis causas:")
        print("   • Token inválido ou expirado")
        print("   • Phone ID incorreto")
        print("   • Canal desconectado no whapi.cloud")
        print("   • Número de telefone inválido")
        print("\n📖 Consulte o guia: CONFIGURACAO_WHAPI.md")
        print("=" * 60)

if __name__ == '__main__':
    main()

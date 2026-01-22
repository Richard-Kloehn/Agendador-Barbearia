"""
Teste Simples - Enviar para seu número
=======================================
Envia mensagem de teste diretamente para 47991557386
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.whapi_service import WhapiService

def main():
    print("\n" + "="*60)
    print("📱 TESTE DIRETO - WHAPI.CLOUD")
    print("="*60)
    
    # Verificar configuração
    token = os.getenv('WHAPI_API_TOKEN')
    phone_id = os.getenv('WHAPI_PHONE_ID')
    
    print(f"\n🔍 Verificando configuração...")
    print(f"   Token: {'✅ Configurado' if token else '❌ NÃO configurado'}")
    print(f"   Phone ID: {'✅ Configurado' if phone_id else '❌ NÃO configurado'}")
    
    if not token:
        print("\n❌ ERRO: WHAPI_API_TOKEN não está configurado no .env")
        return
    
    if not phone_id:
        print("\n❌ ERRO: WHAPI_PHONE_ID não está configurado no .env")
        print("   Você precisa pegar esse ID no painel do whapi.cloud")
        return
    
    # Criar serviço
    whapi = WhapiService()
    
    # Seu número
    seu_numero = "47991557386"
    
    # Criar mensagem de teste (simulando um lembrete)
    data_teste = datetime.now() + timedelta(days=1)
    data_formatada = data_teste.strftime('%d/%m')
    hora_formatada = "14:00"
    dia_semana = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 
                  'Sexta-feira', 'Sábado', 'Domingo'][data_teste.weekday()]
    
    hora_atual = datetime.now().hour
    if hora_atual < 12:
        saudacao = "Bom dia"
    elif hora_atual < 18:
        saudacao = "Boa tarde"
    else:
        saudacao = "Boa noite"
    
    mensagem = f"""{saudacao}, Cliente Teste! ✂️

✅ Confirmação de Agendamento

📅 *Data:* {dia_semana}, {data_formatada}
🕐 *Horário:* {hora_formatada}
✂️ *Serviço:* Corte + Barba
👤 *Barbeiro:* Carlos

❌ *Caso precise cancelar*, acesse o site e faça o cancelamento:
http://localhost:5000

⚠️ *Importante:* Esta é uma mensagem automática. Não é necessário responder.

Barbearia aguarda você! 💈

---
🧪 Esta é uma mensagem de TESTE do sistema de automação whapi.cloud"""
    
    # Enviar
    print(f"\n📤 Enviando mensagem de teste para: {seu_numero}")
    print(f"   (será formatado para: 55{seu_numero})")
    
    sucesso = whapi.enviar_mensagem(seu_numero, mensagem)
    
    print("\n" + "="*60)
    if sucesso:
        print("✅ SUCESSO! Mensagem enviada com sucesso!")
        print("="*60)
        print(f"\n📱 Verifique seu WhatsApp: {seu_numero}")
        print("\n💡 Se a mensagem chegou, a integração está funcionando!")
        print("   O sistema vai enviar lembretes automáticos 24h antes dos agendamentos.")
    else:
        print("❌ FALHA ao enviar mensagem")
        print("="*60)
        print("\n🔍 Possíveis problemas:")
        print("   1. WHAPI_PHONE_ID incorreto no arquivo .env")
        print("   2. Canal desconectado no painel: https://panel.whapi.cloud")
        print("   3. Token expirado ou inválido")
        print("   4. Problemas de conexão com a API")
        print("\n📖 Veja os logs acima para mais detalhes")
    
    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    main()

"""
Teste Rápido - whapi.cloud
===========================
Envia um lembrete de teste usando suas credenciais
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("\n" + "="*60)
    print("📱 TESTE RÁPIDO - WHAPI.CLOUD")
    print("="*60)
    
    # Verificar configuração
    token = os.getenv('WHAPI_API_TOKEN')
    phone_id = os.getenv('WHAPI_PHONE_ID')
    
    if not token:
        print("\n❌ ERRO: WHAPI_API_TOKEN não configurado no arquivo .env")
        print("   Configure o token obtido em: https://panel.whapi.cloud")
        return
    
    if not phone_id:
        print("\n⚠️ AVISO: WHAPI_PHONE_ID não configurado")
        print("   Você precisa pegar o Phone ID na tela de configurações do canal")
        print("   É algo como: 5511987654321@c.us")
        print("\n   Por enquanto, vou testar apenas a conexão...")
    
    print(f"\n✅ Token configurado: {token[:20]}...")
    if phone_id:
        print(f"✅ Phone ID: {phone_id}")
    
    # Testar com banco de dados
    print("\n" + "="*60)
    print("🗄️ TESTANDO COM BANCO DE DADOS")
    print("="*60)
    
    try:
        from app import app, db
        from models import Agendamento
        
        with app.app_context():
            # Buscar agendamento para amanhã
            amanha = datetime.now() + timedelta(days=1)
            inicio = amanha.replace(hour=0, minute=0, second=0)
            fim = amanha.replace(hour=23, minute=59, second=59)
            
            agendamentos = Agendamento.query.filter(
                Agendamento.data_hora >= inicio,
                Agendamento.data_hora <= fim,
                Agendamento.telefone != ''
            ).all()
            
            if not agendamentos:
                print("\n⚠️ Nenhum agendamento encontrado para amanhã")
                print("   Crie um agendamento para testar o envio")
                
                # Mostrar agendamentos futuros
                futuros = Agendamento.query.filter(
                    Agendamento.data_hora > datetime.now(),
                    Agendamento.telefone != ''
                ).order_by(Agendamento.data_hora).limit(5).all()
                
                if futuros:
                    print(f"\n📋 Agendamentos futuros encontrados:")
                    for ag in futuros:
                        data_str = ag.data_hora.strftime('%d/%m %H:%M')
                        print(f"   • {ag.nome_cliente} - {data_str} - Tel: {ag.telefone}")
                    
                    print("\n💡 Quer testar com um destes agendamentos? (s/n)")
                    resposta = input("   Resposta: ").strip().lower()
                    
                    if resposta == 's':
                        print("\n📤 Enviando lembrete de teste...")
                        from services.whapi_service import enviar_lembrete_whatsapp
                        
                        sucesso = enviar_lembrete_whatsapp(futuros[0])
                        
                        if sucesso:
                            print("\n✅ SUCESSO! Mensagem enviada!")
                            print(f"   Verifique o WhatsApp: {futuros[0].telefone}")
                        else:
                            print("\n❌ Falha ao enviar mensagem")
                            print("   Verifique se o WHAPI_PHONE_ID está correto")
                else:
                    print("\n⚠️ Nenhum agendamento futuro encontrado no banco")
                    
            else:
                print(f"\n✅ {len(agendamentos)} agendamento(s) encontrado(s) para amanhã:")
                for ag in agendamentos:
                    hora_str = ag.data_hora.strftime('%H:%M')
                    print(f"   • {ag.nome_cliente} às {hora_str} - Tel: {ag.telefone}")
                
                print("\n📤 Enviando lembrete de teste para o primeiro agendamento...")
                from services.whapi_service import enviar_lembrete_whatsapp
                
                sucesso = enviar_lembrete_whatsapp(agendamentos[0])
                
                if sucesso:
                    print("\n" + "="*60)
                    print("✅ SUCESSO! Mensagem de teste enviada!")
                    print("="*60)
                    print(f"\n📱 Verifique o WhatsApp: {agendamentos[0].telefone}")
                    print(f"👤 Cliente: {agendamentos[0].nome_cliente}")
                    print(f"📅 Horário: {agendamentos[0].data_hora.strftime('%d/%m %H:%M')}")
                else:
                    print("\n" + "="*60)
                    print("❌ FALHA ao enviar mensagem")
                    print("="*60)
                    print("\n🔍 Verifique:")
                    print("   1. WHAPI_PHONE_ID está correto no .env")
                    print("   2. Canal está conectado em: https://panel.whapi.cloud")
                    print("   3. Número de telefone está no formato correto")
                
    except Exception as e:
        print(f"\n❌ Erro ao acessar banco de dados: {e}")
        print("   Certifique-se de que o banco está configurado")
    
    print("\n" + "="*60)

if __name__ == '__main__':
    main()

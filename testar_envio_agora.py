"""
Script para Testar Envio de WhatsApp IMEDIATAMENTE
===================================================
Envia uma mensagem de teste para o primeiro agendamento encontrado
sem precisar esperar o agendamento automático.
"""

from app import app
from database import db
from models import Agendamento
from services.whatsapp_service import enviar_lembrete_whatsapp

def testar_envio_imediato():
    """Envia mensagem de teste imediatamente"""
    with app.app_context():
        print("\n" + "="*60)
        print("TESTE IMEDIATO DE ENVIO DE WHATSAPP")
        print("="*60)
        
        # Busca agendamentos
        agendamentos = Agendamento.query.filter_by(status='confirmado').all()
        
        if not agendamentos:
            print("\n❌ Nenhum agendamento encontrado.")
            print("\n💡 Crie um agendamento primeiro em: http://localhost:5000")
            return
        
        print(f"\n📋 Total de agendamentos encontrados: {len(agendamentos)}")
        print("\nAgendamentos disponíveis:\n")
        
        for i, ag in enumerate(agendamentos, 1):
            data_hora = ag.data_hora.strftime('%d/%m/%Y às %H:%M')
            barbeiro = ag.barbeiro.nome if ag.barbeiro else "N/A"
            servico = ag.servico.nome if ag.servico else "N/A"
            
            print(f"{i}. {ag.nome_cliente}")
            print(f"   Telefone: {ag.telefone}")
            print(f"   Data/Hora: {data_hora}")
            print(f"   Barbeiro: {barbeiro}")
            print(f"   Serviço: {servico}")
            print()
        
        # Escolher agendamento
        if len(agendamentos) == 1:
            escolha = 1
            print("📱 Enviando para o único agendamento encontrado...\n")
        else:
            try:
                escolha = int(input(f"Escolha o agendamento (1-{len(agendamentos)}): "))
                if escolha < 1 or escolha > len(agendamentos):
                    print("❌ Opção inválida!")
                    return
            except ValueError:
                print("❌ Entrada inválida!")
                return
        
        agendamento = agendamentos[escolha - 1]
        
        print("\n" + "-"*60)
        print("🚀 INICIANDO ENVIO...")
        print("-"*60)
        print(f"\n📤 Destinatário: {agendamento.nome_cliente}")
        print(f"📱 Telefone: {agendamento.telefone}")
        print(f"\n⏳ Aguarde... O navegador será aberto automaticamente.")
        print("   Na primeira vez, você precisará escanear o QR Code.\n")
        
        # Enviar mensagem
        try:
            sucesso = enviar_lembrete_whatsapp(agendamento)
            
            print("\n" + "="*60)
            if sucesso:
                print("✅ MENSAGEM ENVIADA COM SUCESSO!")
                print("="*60)
                print(f"\n🎉 A mensagem foi enviada para {agendamento.telefone}")
                print("📱 Verifique seu WhatsApp!")
            else:
                print("❌ FALHA AO ENVIAR MENSAGEM")
                print("="*60)
                print("\n📋 Verifique os logs em: whatsapp_automation.log")
                print("💡 Possíveis causas:")
                print("   - WhatsApp Web não está logado")
                print("   - Número de telefone inválido")
                print("   - Problemas de conexão")
            print("\n" + "="*60 + "\n")
            
        except Exception as e:
            print(f"\n❌ Erro ao enviar: {e}")
            print("📋 Verifique os logs para mais detalhes\n")


if __name__ == "__main__":
    print("\n⚠️  ATENÇÃO:")
    print("Este script irá abrir o navegador e enviar uma mensagem de teste")
    print("para o agendamento selecionado.\n")
    
    resposta = input("Deseja continuar? (s/n): ")
    
    if resposta.lower() == 's':
        testar_envio_imediato()
    else:
        print("\n❌ Teste cancelado.")

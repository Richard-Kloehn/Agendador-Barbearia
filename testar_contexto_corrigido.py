"""Script para testar se o contexto foi corrigido"""
from app import app
from database import db
from models import Agendamento
from datetime import datetime, timedelta

def testar_agendamento_recente():
    """Verifica o último agendamento criado"""
    with app.app_context():
        # Buscar último agendamento
        ultimo = Agendamento.query.order_by(Agendamento.id.desc()).first()
        
        if not ultimo:
            print("❌ Nenhum agendamento encontrado")
            return
        
        print("\n" + "="*60)
        print("ÚLTIMO AGENDAMENTO CRIADO")
        print("="*60)
        print(f"ID: {ultimo.id}")
        print(f"Cliente: {ultimo.nome_cliente}")
        print(f"Telefone: {ultimo.telefone}")
        print(f"Data/Hora: {ultimo.data_hora}")
        print(f"Barbeiro: {ultimo.barbeiro.nome if ultimo.barbeiro else 'N/A'}")
        print(f"Serviço: {ultimo.servico.nome if ultimo.servico else 'N/A'}")
        print(f"Status: {ultimo.status}")
        print(f"Criado em: {ultimo.criado_em}")
        print("="*60)
        
        # Calcular tempo até o agendamento
        agora = datetime.now()
        tempo_ate = ultimo.data_hora - agora
        horas_ate = tempo_ate.total_seconds() / 3600
        
        print(f"\n⏰ Tempo até o agendamento: {horas_ate:.1f} horas")
        
        if horas_ate <= 24:
            print("✅ Agendamento está a menos de 24h - WhatsApp deveria ter sido enviado AGORA")
        else:
            print(f"📅 Agendamento está a mais de 24h - Lembrete será enviado em {ultimo.data_hora - timedelta(hours=24)}")
        
        print("\n📌 VERIFICAR:")
        print(f"   - Telefone do teste: {ultimo.telefone}")
        print("   - Checar se mensagem chegou no WhatsApp")
        print("   - Verificar logs do servidor acima")
        print("="*60 + "\n")

if __name__ == '__main__':
    testar_agendamento_recente()

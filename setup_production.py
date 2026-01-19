"""
Script para configurar o banco de dados em produção
Execute no Shell do Render: python setup_production.py
"""
from app import app
from database import db
from models import HorarioBarbeiro, Barbeiro, ConfiguracaoBarbearia

def setup():
    with app.app_context():
        print("🔧 Configurando banco de dados em produção...")
        
        # Criar tabelas
        db.create_all()
        print("✓ Tabelas criadas/verificadas")
        
        # Obter configuração
        config = ConfiguracaoBarbearia.query.first()
        if not config:
            print("❌ Configuração não encontrada. Execute a aplicação primeiro.")
            return
        
        # Obter barbeiros
        barbeiros = Barbeiro.query.all()
        if not barbeiros:
            print("❌ Nenhum barbeiro encontrado.")
            return
        
        print(f"\n📋 Encontrados {len(barbeiros)} barbeiros")
        
        # Configurar horários para cada barbeiro
        for barbeiro in barbeiros:
            # Verificar se barbeiro já tem horários
            horarios_existentes = HorarioBarbeiro.query.filter_by(barbeiro_id=barbeiro.id).count()
            
            if horarios_existentes == 0:
                print(f"\n👤 Configurando horários para: {barbeiro.nome}")
                
                # Criar horários de segunda a sábado (dias 1-6)
                for dia in range(1, 7):
                    horario = HorarioBarbeiro(
                        barbeiro_id=barbeiro.id,
                        dia_semana=dia,
                        horario_inicio=config.horario_abertura,
                        horario_fim=config.horario_fechamento,
                        intervalo_almoco_inicio=config.intervalo_almoco_inicio,
                        intervalo_almoco_fim=config.intervalo_almoco_fim,
                        ativo=True
                    )
                    db.session.add(horario)
                
                db.session.commit()
                print(f"   ✓ Horários criados (Seg-Sáb: {config.horario_abertura}-{config.horario_fechamento})")
            else:
                print(f"✓ {barbeiro.nome} já possui {horarios_existentes} horários configurados")
        
        print("\n🎉 Setup concluído com sucesso!")
        print("\n📊 Resumo:")
        print(f"   - Barbeiros: {len(barbeiros)}")
        print(f"   - Horários por barbeiro: 6 dias (Seg-Sáb)")
        print(f"   - Horário: {config.horario_abertura} às {config.horario_fechamento}")

if __name__ == '__main__':
    setup()

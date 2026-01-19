"""
Script de migração para criar tabela de horários de barbeiros
e atualizar tabela de horários especiais
"""

from app import app
from database import db
from models import HorarioBarbeiro, HorarioEspecial, Barbeiro, ConfiguracaoBarbearia

def migrar():
    with app.app_context():
        print("Iniciando migração...")
        
        # Criar todas as tabelas (se não existirem)
        db.create_all()
        print("✓ Tabelas criadas/atualizadas")
        
        # Verificar se existem barbeiros sem horários
        barbeiros = Barbeiro.query.all()
        config = ConfiguracaoBarbearia.query.first()
        
        if config and barbeiros:
            print(f"\nEncontrados {len(barbeiros)} barbeiros")
            
            for barbeiro in barbeiros:
                # Verificar se barbeiro já tem horários
                horarios_existentes = HorarioBarbeiro.query.filter_by(barbeiro_id=barbeiro.id).count()
                
                if horarios_existentes == 0:
                    print(f"\nConfigurando horários padrão para: {barbeiro.nome}")
                    
                    # Criar horários padrão de segunda a sábado (dias 1-6)
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
                        dias_semana = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
                        print(f"  - {dias_semana[dia]}: {config.horario_abertura} às {config.horario_fechamento}")
                    
                    db.session.commit()
                    print(f"  ✓ Horários salvos para {barbeiro.nome}")
                else:
                    print(f"✓ {barbeiro.nome} já possui horários configurados")
        
        print("\n✓ Migração concluída com sucesso!")
        print("\nPróximos passos:")
        print("1. Acesse o painel admin")
        print("2. Vá em 'Horários'")
        print("3. Configure os horários individuais de cada barbeiro")

if __name__ == '__main__':
    migrar()

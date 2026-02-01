"""
Script para corrigir horários dos barbeiros no banco de produção
Executa automaticamente ao rodar a aplicação
"""
from app import app
from database import db
from models import Barbeiro, HorarioBarbeiro, ConfiguracaoBarbearia

def corrigir_horarios_producao():
    """Corrige horários dos barbeiros no banco de dados"""
    with app.app_context():
        # Verificar se é PostgreSQL (produção)
        db_url = app.config['SQLALCHEMY_DATABASE_URI']
        is_production = 'postgresql' in db_url
        
        print("="*70)
        print("🔧 CORREÇÃO DE HORÁRIOS DOS BARBEIROS")
        print("="*70)
        print(f"Ambiente: {'PRODUÇÃO (PostgreSQL)' if is_production else 'LOCAL (SQLite)'}")
        
        # 1. Corrigir configuração se necessário
        config = ConfiguracaoBarbearia.query.first()
        if config and config.dias_funcionamento == "0,1,2,3,4,5":
            print("\n📝 Corrigindo configuração de dias de funcionamento...")
            config.dias_funcionamento = "1,2,3,4,5,6"  # Segunda a Sábado
            db.session.commit()
            print("✅ Configuração atualizada!")
        
        # 2. Verificar e corrigir horários dos barbeiros
        barbeiros = Barbeiro.query.all()
        
        # Horários padrão corretos (1=segunda a 6=sábado, 0=domingo)
        horarios_padrao = [
            {'dia_semana': 1, 'horario_inicio': '09:00', 'horario_fim': '18:00', 
             'intervalo_almoco_inicio': '12:00', 'intervalo_almoco_fim': '13:00'},
            {'dia_semana': 2, 'horario_inicio': '09:00', 'horario_fim': '18:00',
             'intervalo_almoco_inicio': '12:00', 'intervalo_almoco_fim': '13:00'},
            {'dia_semana': 3, 'horario_inicio': '09:00', 'horario_fim': '18:00',
             'intervalo_almoco_inicio': '12:00', 'intervalo_almoco_fim': '13:00'},
            {'dia_semana': 4, 'horario_inicio': '09:00', 'horario_fim': '18:00',
             'intervalo_almoco_inicio': '12:00', 'intervalo_almoco_fim': '13:00'},
            {'dia_semana': 5, 'horario_inicio': '09:00', 'horario_fim': '18:00',
             'intervalo_almoco_inicio': '12:00', 'intervalo_almoco_fim': '13:00'},
            {'dia_semana': 6, 'horario_inicio': '09:00', 'horario_fim': '17:00',
             'intervalo_almoco_inicio': None, 'intervalo_almoco_fim': None}
        ]
        
        total_corrigidos = 0
        
        for barbeiro in barbeiros:
            print(f"\n👤 Verificando: {barbeiro.nome}")
            
            # Buscar horários existentes
            horarios_existentes = HorarioBarbeiro.query.filter_by(barbeiro_id=barbeiro.id).all()
            
            # Verificar se tem horários com dia 0 (que seria segunda no sistema antigo)
            tem_horario_dia_0 = any(h.dia_semana == 0 for h in horarios_existentes)
            
            if tem_horario_dia_0:
                print(f"   ⚠️ Horários com padrão antigo detectado! Corrigindo...")
                
                # Deletar todos os horários antigos
                HorarioBarbeiro.query.filter_by(barbeiro_id=barbeiro.id).delete()
                
                # Criar horários novos com padrão correto
                for horario_data in horarios_padrao:
                    horario = HorarioBarbeiro(
                        barbeiro_id=barbeiro.id,
                        dia_semana=horario_data['dia_semana'],
                        horario_inicio=horario_data['horario_inicio'],
                        horario_fim=horario_data['horario_fim'],
                        intervalo_almoco_inicio=horario_data['intervalo_almoco_inicio'],
                        intervalo_almoco_fim=horario_data['intervalo_almoco_fim'],
                        ativo=True
                    )
                    db.session.add(horario)
                    total_corrigidos += 1
                
                print(f"   ✅ {len(horarios_padrao)} horários corrigidos!")
            else:
                # Verificar se tem todos os horários necessários
                dias_existentes = {h.dia_semana for h in horarios_existentes}
                dias_necessarios = {h['dia_semana'] for h in horarios_padrao}
                dias_faltantes = dias_necessarios - dias_existentes
                
                if dias_faltantes:
                    print(f"   ⚠️ Faltam horários para dias: {dias_faltantes}")
                    
                    for dia in dias_faltantes:
                        horario_data = next(h for h in horarios_padrao if h['dia_semana'] == dia)
                        horario = HorarioBarbeiro(
                            barbeiro_id=barbeiro.id,
                            dia_semana=horario_data['dia_semana'],
                            horario_inicio=horario_data['horario_inicio'],
                            horario_fim=horario_data['horario_fim'],
                            intervalo_almoco_inicio=horario_data['intervalo_almoco_inicio'],
                            intervalo_almoco_fim=horario_data['intervalo_almoco_fim'],
                            ativo=True
                        )
                        db.session.add(horario)
                        total_corrigidos += 1
                    
                    print(f"   ✅ {len(dias_faltantes)} horários adicionados!")
                else:
                    print(f"   ✅ Horários OK!")
        
        if total_corrigidos > 0:
            db.session.commit()
            print(f"\n{'='*70}")
            print(f"✅ Total de horários corrigidos/adicionados: {total_corrigidos}")
            print("="*70)
        else:
            print(f"\n{'='*70}")
            print("✅ Todos os horários já estão corretos!")
            print("="*70)

if __name__ == '__main__':
    corrigir_horarios_producao()

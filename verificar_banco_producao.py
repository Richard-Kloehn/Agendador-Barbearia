"""
Script para verificar e corrigir dados no banco de produção (Postgres)
"""
from app import app
from database import db
from models import ConfiguracaoBarbearia, Barbeiro, HorarioBarbeiro, Servico

def verificar_banco():
    with app.app_context():
        print("="*70)
        print("🔍 VERIFICANDO BANCO DE DADOS DE PRODUÇÃO")
        print("="*70)
        
        # Verificar URL do banco
        db_url = app.config['SQLALCHEMY_DATABASE_URI']
        if 'postgresql' in db_url:
            print("✅ Conectado ao PostgreSQL (Produção)")
        else:
            print("⚠️ Conectado ao SQLite (Local)")
        
        print(f"\n📊 DATABASE: {db_url[:50]}...")
        
        # 1. Verificar configuração
        print("\n" + "="*70)
        print("1️⃣ CONFIGURAÇÃO DA BARBEARIA")
        print("="*70)
        config = ConfiguracaoBarbearia.query.first()
        if config:
            print(f"Nome: {config.nome_barbearia}")
            print(f"Horário: {config.horario_abertura} - {config.horario_fechamento}")
            print(f"Dias de funcionamento: {config.dias_funcionamento}")
            print(f"   Interpretação: ", end="")
            dias = config.dias_funcionamento.split(',')
            dias_nomes = {
                '0': 'Domingo',
                '1': 'Segunda',
                '2': 'Terça',
                '3': 'Quarta',
                '4': 'Quinta',
                '5': 'Sexta',
                '6': 'Sábado'
            }
            print(', '.join([dias_nomes.get(d, d) for d in dias]))
            
            # Verificar se precisa atualizar
            if config.dias_funcionamento == "0,1,2,3,4,5":
                print("\n⚠️ ATENÇÃO: Configuração antiga detectada!")
                print("   Atual: 0,1,2,3,4,5 (padrão antigo)")
                print("   Deve ser: 1,2,3,4,5,6 (Segunda a Sábado)")
                
                resposta = input("\n🔧 Deseja corrigir? (s/n): ")
                if resposta.lower() == 's':
                    config.dias_funcionamento = "1,2,3,4,5,6"
                    db.session.commit()
                    print("✅ Configuração atualizada!")
            else:
                print("✅ Configuração correta!")
        else:
            print("❌ Nenhuma configuração encontrada!")
        
        # 2. Verificar barbeiros
        print("\n" + "="*70)
        print("2️⃣ BARBEIROS CADASTRADOS")
        print("="*70)
        barbeiros = Barbeiro.query.all()
        print(f"Total de barbeiros: {len(barbeiros)}")
        for b in barbeiros:
            print(f"\n   {b.id}. {b.nome}")
            print(f"      Ativo: {'✅' if b.ativo else '❌'}")
            print(f"      Foto: {b.foto_url}")
            print(f"      Serviços: {len(b.servicos)}")
        
        # 3. Verificar horários dos barbeiros
        print("\n" + "="*70)
        print("3️⃣ HORÁRIOS DOS BARBEIROS")
        print("="*70)
        
        dias_nomes = {
            0: 'Domingo',
            1: 'Segunda',
            2: 'Terça',
            3: 'Quarta',
            4: 'Quinta',
            5: 'Sexta',
            6: 'Sábado'
        }
        
        for barbeiro in barbeiros:
            print(f"\n📅 {barbeiro.nome}:")
            horarios = HorarioBarbeiro.query.filter_by(barbeiro_id=barbeiro.id).order_by(HorarioBarbeiro.dia_semana).all()
            
            if not horarios:
                print("   ❌ SEM HORÁRIOS CADASTRADOS!")
            else:
                for h in horarios:
                    status = "✅" if h.ativo else "❌"
                    almoco = ""
                    if h.intervalo_almoco_inicio and h.intervalo_almoco_fim:
                        almoco = f" (Almoço: {h.intervalo_almoco_inicio}-{h.intervalo_almoco_fim})"
                    print(f"   {status} {dias_nomes[h.dia_semana]}: {h.horario_inicio}-{h.horario_fim}{almoco}")
        
        # 4. Verificar serviços
        print("\n" + "="*70)
        print("4️⃣ SERVIÇOS CADASTRADOS")
        print("="*70)
        servicos = Servico.query.all()
        print(f"Total de serviços: {len(servicos)}")
        for s in servicos:
            status = "✅" if s.ativo else "❌"
            print(f"   {status} {s.nome}: {s.duracao}min - R$ {s.preco:.2f}")
        
        print("\n" + "="*70)
        print("✅ VERIFICAÇÃO CONCLUÍDA")
        print("="*70)

if __name__ == '__main__':
    verificar_banco()

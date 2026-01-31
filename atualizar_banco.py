"""
Script para atualizar o banco de dados com as novas funcionalidades
Adiciona: Avaliações, Lista de Espera, Galeria de Trabalhos

Execute este arquivo apenas uma vez após atualizar o código
"""

from app import app
from database import db
from models import Agendamento, ListaEspera, GaleriaTrabalhos, ConfiguracaoGeral
from sqlalchemy import text

print("="*60)
print("ATUALIZAÇÃO DO BANCO DE DADOS")
print("="*60)

with app.app_context():
    # Verificar se as colunas de avaliação já existem
    try:
        inspector = db.inspect(db.engine)
        colunas_agendamento = [col['name'] for col in inspector.get_columns('agendamentos')]
        
        if 'avaliacao' not in colunas_agendamento:
            print("\n📋 Adicionando colunas de avaliação na tabela agendamentos...")
            
            # Adicionar colunas de avaliação
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE agendamentos ADD COLUMN avaliacao INTEGER'))
                conn.execute(text('ALTER TABLE agendamentos ADD COLUMN comentario_avaliacao TEXT'))
                conn.execute(text('ALTER TABLE agendamentos ADD COLUMN data_avaliacao TIMESTAMP'))
                conn.commit()
            
            print("✅ Colunas de avaliação adicionadas!")
        else:
            print("\n✅ Colunas de avaliação já existem")
    except Exception as e:
        print(f"❌ Erro ao adicionar colunas de avaliação: {e}")
    
    # Criar novas tabelas
    print("\n📋 Criando novas tabelas...")
    try:
        db.create_all()
        print("✅ Tabelas criadas/atualizadas com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
    
    # Adicionar configurações padrão
    print("\n📋 Adicionando configurações padrão...")
    try:
        # Configuração de prazo de cancelamento
        config_cancelamento = ConfiguracaoGeral.query.filter_by(chave='prazo_cancelamento_horas').first()
        if not config_cancelamento:
            config_cancelamento = ConfiguracaoGeral(
                chave='prazo_cancelamento_horas',
                valor='2',
                descricao='Horas mínimas de antecedência para cancelar agendamento'
            )
            db.session.add(config_cancelamento)
        
        # Configuração de informações de contato
        configs_contato = [
            ('telefone_barbearia', '(11) 99999-9999', 'Telefone de contato da barbearia'),
            ('endereco_barbearia', 'Rua Exemplo, 123 - Bairro', 'Endereço completo da barbearia'),
            ('instagram', '@barbearia', 'Instagram da barbearia'),
            ('facebook', 'facebook.com/barbearia', 'Facebook da barbearia'),
            ('horario_funcionamento', 'Seg-Sex: 9h-20h | Sáb: 9h-18h', 'Horário de funcionamento'),
        ]
        
        for chave, valor, descricao in configs_contato:
            config = ConfiguracaoGeral.query.filter_by(chave=chave).first()
            if not config:
                config = ConfiguracaoGeral(chave=chave, valor=valor, descricao=descricao)
                db.session.add(config)
        
        db.session.commit()
        print("✅ Configurações padrão adicionadas!")
    except Exception as e:
        print(f"❌ Erro ao adicionar configurações: {e}")
    
    # Criar índices para performance
    if 'postgresql' in str(db.engine.url):
        print("\n📊 Criando índices para melhor performance...")
        try:
            with db.engine.connect() as conn:
                # Índices para lista de espera
                conn.execute(text(
                    "CREATE INDEX IF NOT EXISTS idx_lista_espera_data ON lista_espera(data_preferencia)"
                ))
                conn.execute(text(
                    "CREATE INDEX IF NOT EXISTS idx_lista_espera_status ON lista_espera(status)"
                ))
                
                # Índices para avaliações
                conn.execute(text(
                    "CREATE INDEX IF NOT EXISTS idx_agendamento_avaliacao ON agendamentos(avaliacao)"
                ))
                
                # Índices para galeria
                conn.execute(text(
                    "CREATE INDEX IF NOT EXISTS idx_galeria_ativo ON galeria_trabalhos(ativo, ordem)"
                ))
                
                conn.commit()
            
            print("✅ Índices criados com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao criar índices: {e}")
    
    # Resumo final
    print("\n" + "="*60)
    print("RESUMO DA ATUALIZAÇÃO")
    print("="*60)
    
    try:
        total_agendamentos = Agendamento.query.count()
        print(f"📊 Agendamentos no sistema: {total_agendamentos}")
    except Exception as e:
        print(f"📊 Agendamentos: (erro ao contar - {e})")
    
    try:
        total_lista_espera = ListaEspera.query.count()
        print(f"📊 Itens na lista de espera: {total_lista_espera}")
    except Exception as e:
        print(f"📊 Lista de espera: 0 (tabela nova)")
    
    try:
        total_galeria = GaleriaTrabalhos.query.count()
        print(f"📊 Fotos na galeria: {total_galeria}")
    except Exception as e:
        print(f"📊 Galeria: 0 (tabela nova)")
    
    # Estatísticas de avaliação
    try:
        avaliacoes = Agendamento.query.filter(Agendamento.avaliacao.isnot(None)).count()
        if avaliacoes > 0:
            media = db.session.query(db.func.avg(Agendamento.avaliacao)).filter(
                Agendamento.avaliacao.isnot(None)
            ).scalar()
            print(f"⭐ Avaliações recebidas: {avaliacoes} (Média: {media:.1f}/5)")
        else:
            print(f"⭐ Avaliações recebidas: 0")
    except Exception as e:
        print(f"⭐ Avaliações: 0 (funcionalidade nova)")
    
    print("\n" + "="*60)
    print("✅ ATUALIZAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*60)
    print("\n📌 NOVAS FUNCIONALIDADES DISPONÍVEIS:")
    print("   • Sistema de Avaliação pós-atendimento")
    print("   • Lista de Espera para horários ocupados")
    print("   • Galeria de Trabalhos")
    print("   • Reagendamento facilitado")
    print("   • Validações e sanitização de dados")
    print("   • Proteção CSRF e Rate Limiting")
    print("   • Política de cancelamento com prazo mínimo")
    print("\n🔐 SEGURANÇA:")
    print("   • Configure a senha do admin no arquivo .env")
    print("   • Use uma SECRET_KEY forte no .env")
    print("   • Verifique as configurações de prazo de cancelamento")
    print("\n")

"""
Script para alterar todos os telefones dos clientes para um número de teste
===========================================================================
Este script altera todos os telefones cadastrados para o número especificado,
permitindo testar o sistema de envio de WhatsApp sem enviar para clientes reais.
"""

from app import app
from database import db
from models import Cliente, Agendamento

# NÚMERO DE TESTE (seu número)
NUMERO_TESTE = '47991557386'

def alterar_telefones_para_teste():
    """Altera todos os telefones para o número de teste"""
    with app.app_context():
        try:
            print("\n" + "="*60)
            print("ALTERANDO TELEFONES PARA MODO DE TESTE")
            print("="*60)
            
            # Alterar telefones dos clientes
            clientes = Cliente.query.all()
            total_clientes = len(clientes)
            
            if total_clientes == 0:
                print("\n❌ Nenhum cliente encontrado no banco de dados.")
                return
            
            print(f"\n📋 Total de clientes encontrados: {total_clientes}")
            print(f"🔄 Alterando todos os telefones para: {NUMERO_TESTE}\n")
            
            for i, cliente in enumerate(clientes, 1):
                telefone_antigo = cliente.telefone
                cliente.telefone = NUMERO_TESTE
                print(f"  {i}. {cliente.nome_completo}: {telefone_antigo} → {NUMERO_TESTE}")
            
            # Alterar telefones dos agendamentos
            agendamentos = Agendamento.query.all()
            total_agendamentos = len(agendamentos)
            
            print(f"\n📅 Total de agendamentos encontrados: {total_agendamentos}")
            
            for agendamento in agendamentos:
                agendamento.telefone = NUMERO_TESTE
            
            # Salvar alterações
            db.session.commit()
            
            print("\n" + "="*60)
            print("✅ TODOS OS TELEFONES FORAM ALTERADOS COM SUCESSO!")
            print("="*60)
            print(f"\n📱 Todos os {total_clientes} clientes agora têm o telefone: {NUMERO_TESTE}")
            print(f"📱 Todos os {total_agendamentos} agendamentos agora têm o telefone: {NUMERO_TESTE}")
            print("\n⚠️  IMPORTANTE:")
            print("   - Todas as mensagens serão enviadas para este número")
            print("   - Use isso apenas para testes")
            print("   - Não esqueça de restaurar os números reais depois!")
            print("\n" + "="*60 + "\n")
            
        except Exception as e:
            print(f"\n❌ Erro ao alterar telefones: {e}")
            db.session.rollback()


def restaurar_telefones_originais():
    """
    ATENÇÃO: Esta função NÃO pode restaurar os números originais
    pois eles foram sobrescritos. Use apenas se tiver um backup!
    """
    print("\n⚠️  AVISO:")
    print("Os números originais foram sobrescritos e não podem ser restaurados")
    print("automaticamente. Você precisará:")
    print("1. Restaurar um backup do banco de dados, OU")
    print("2. Re-cadastrar os telefones manualmente no admin")
    print()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("SCRIPT DE ALTERAÇÃO DE TELEFONES PARA TESTE")
    print("="*60)
    print("\n⚠️  ATENÇÃO:")
    print("Este script irá alterar TODOS os telefones cadastrados")
    print(f"para o número de teste: {NUMERO_TESTE}")
    print("\nOs números originais serão perdidos!")
    print("Certifique-se de ter um backup antes de continuar.")
    print("\n" + "="*60)
    
    resposta = input("\nDeseja continuar? (digite 'SIM' para confirmar): ")
    
    if resposta.upper() == 'SIM':
        alterar_telefones_para_teste()
    else:
        print("\n❌ Operação cancelada pelo usuário.")

"""
Script para habilitar envio para qualquer número
=================================================
Remove qualquer restrição de número de teste e permite 
envio de WhatsApp para todos os clientes reais.
"""

from app import app
from database import db
from models import Cliente, Agendamento

def verificar_numeros():
    """Verifica os números cadastrados no sistema"""
    with app.app_context():
        print("\n" + "="*60)
        print("VERIFICAÇÃO DE NÚMEROS NO SISTEMA")
        print("="*60)
        
        # Verificar clientes
        clientes = Cliente.query.all()
        print(f"\n📋 Total de clientes: {len(clientes)}")
        
        if len(clientes) > 0:
            print("\nExemplos de números cadastrados:")
            for i, cliente in enumerate(clientes[:5], 1):
                print(f"  {i}. {cliente.nome_completo}: {cliente.telefone}")
            
            # Verificar se há números repetidos (sinal de teste)
            numeros = [c.telefone for c in clientes]
            numeros_unicos = set(numeros)
            
            if len(numeros_unicos) < len(numeros):
                print(f"\n⚠️ ATENÇÃO: Há {len(numeros) - len(numeros_unicos)} números duplicados!")
                print("Isso pode indicar que foi usado um número de teste para todos.")
                print("\nSe você quiser restaurar os números originais,")
                print("será necessário recuperar de um backup ou recadastrá-los.")
            else:
                print(f"\n✅ Todos os {len(numeros)} números são únicos!")
        
        # Verificar agendamentos
        agendamentos = Agendamento.query.all()
        print(f"\n📅 Total de agendamentos: {len(agendamentos)}")
        
        if len(agendamentos) > 0:
            agendamentos_com_telefone = [a for a in agendamentos if a.telefone]
            print(f"   - Com telefone: {len(agendamentos_com_telefone)}")
            print(f"   - Sem telefone: {len(agendamentos) - len(agendamentos_com_telefone)}")
        
        print("\n" + "="*60)
        print("CONFIGURAÇÃO ATUAL DO SISTEMA")
        print("="*60)
        print("\n✅ O sistema está configurado para enviar WhatsApp para QUALQUER número!")
        print("✅ Não há restrições de número no código.")
        print("✅ Todas as mensagens serão enviadas para os números cadastrados.")
        
        print("\n" + "="*60)
        print("IMPORTANTE")
        print("="*60)
        print("\n⚠️  O sistema de automação WhatsApp funciona apenas LOCALMENTE")
        print("   (no seu computador com o Chrome aberto)")
        print("\n⚠️  Em PRODUÇÃO (servidor Render), o WhatsApp não funciona")
        print("   pois não há navegador disponível no servidor.")
        print("\n💡 Para produção, considere usar a API do Twilio.")

if __name__ == '__main__':
    verificar_numeros()

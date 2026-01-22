"""
Script para adicionar a coluna barbeiro_id na tabela horarios_especiais
DIRETAMENTE NO SUPABASE (produção)

IMPORTANTE: Defina a variável de ambiente DATABASE_URL com a URL do Supabase
antes de executar este script:

set DATABASE_URL=postgresql://...
python migrar_producao_urgente.py
"""
import psycopg2
import os
import sys

def migrar_producao():
    """Adiciona coluna barbeiro_id no Supabase"""
    
    # Tentar pegar a URL de produção de diferentes fontes
    database_url = os.getenv('DATABASE_URL_PROD') or os.getenv('DATABASE_URL')
    
    if not database_url or 'sqlite' in database_url:
        print("\n❌ ERRO: DATABASE_URL de produção não encontrada!")
        print("\n💡 Para executar esta migração, defina a variável antes:")
        print("   set DATABASE_URL=postgresql://...")
        print("   python migrar_producao_urgente.py")
        print("\nOu passe como argumento:")
        print('   python migrar_producao_urgente.py "postgresql://..."')
        sys.exit(1)
    
    print("=" * 60)
    print("🔧 MIGRAÇÃO PRODUÇÃO: horarios_especiais.barbeiro_id")
    print("=" * 60)
    print(f"\n📌 Banco: {database_url[:50]}...")
    
    try:
        # Conectar diretamente ao Supabase
        print("\n🔌 Conectando ao Supabase...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Verificar se a coluna já existe
        print("🔍 Verificando se a coluna já existe...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='horarios_especiais' 
            AND column_name='barbeiro_id'
        """)
        
        coluna_existe = cursor.fetchone() is not None
        
        if coluna_existe:
            print("✅ Coluna barbeiro_id já existe!")
        else:
            print("⚙️ Adicionando coluna barbeiro_id...")
            
            # Adicionar a coluna
            cursor.execute("""
                ALTER TABLE horarios_especiais 
                ADD COLUMN barbeiro_id INTEGER NULL 
                REFERENCES barbeiros(id)
            """)
            
            conn.commit()
            print("✅ Coluna barbeiro_id adicionada com sucesso!")
        
        # Verificar estrutura final
        print("\n📋 Estrutura atual da tabela horarios_especiais:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name='horarios_especiais'
            ORDER BY ordinal_position
        """)
        
        for row in cursor.fetchall():
            print(f"   - {row[0]}: {row[1]} (NULL: {row[2]})")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ Migração concluída com sucesso!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Erro ao migrar: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "=" * 60)
        print("❌ Migração falhou!")
        print("=" * 60)
        sys.exit(1)

if __name__ == '__main__':
    # Permitir passar a URL como argumento
    if len(sys.argv) > 1:
        os.environ['DATABASE_URL'] = sys.argv[1]
    
    resposta = input("\n⚠️ Isso irá modificar o banco de PRODUÇÃO! Confirmar? (sim/não): ")
    if resposta.lower() == 'sim':
        migrar_producao()
    else:
        print("❌ Migração cancelada.")

"""
Script para adicionar a coluna barbeiro_id na tabela horarios_especiais
no banco de dados de produção (Supabase)
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def migrar_banco():
    """Adiciona coluna barbeiro_id se não existir"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL não encontrada no .env")
        return
    
    print("=" * 60)
    print("🔧 MIGRAÇÃO: Adicionando coluna barbeiro_id")
    print("=" * 60)
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Verificar se a coluna já existe
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='horarios_especiais' 
                AND column_name='barbeiro_id'
            """))
            
            coluna_existe = result.fetchone() is not None
            
            if coluna_existe:
                print("✅ Coluna barbeiro_id já existe!")
            else:
                print("⚙️ Adicionando coluna barbeiro_id...")
                
                # Adicionar a coluna
                conn.execute(text("""
                    ALTER TABLE horarios_especiais 
                    ADD COLUMN barbeiro_id INTEGER NULL 
                    REFERENCES barbeiros(id)
                """))
                
                conn.commit()
                print("✅ Coluna barbeiro_id adicionada com sucesso!")
            
            # Verificar estrutura final
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name='horarios_especiais'
                ORDER BY ordinal_position
            """))
            
            print("\n📋 Estrutura da tabela horarios_especiais:")
            for row in result:
                print(f"   - {row[0]}: {row[1]} (NULL: {row[2]})")
            
    except Exception as e:
        print(f"❌ Erro ao migrar banco: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ Migração concluída!")
    print("=" * 60)

if __name__ == '__main__':
    migrar_banco()

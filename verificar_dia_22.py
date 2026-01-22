"""
Verificar configurações específicas do dia 22/01/2026
"""
import psycopg2
import sys

DATABASE_URL = sys.argv[1] if len(sys.argv) > 1 else None

if not DATABASE_URL:
    print("❌ Passe a URL do banco como argumento")
    sys.exit(1)

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("🔍 VERIFICANDO DIA 22/01/2026")
    print("=" * 60)
    
    # Verificar dias indisponíveis
    print("\n1️⃣ Dias bloqueados:")
    cursor.execute("""
        SELECT * FROM dias_indisponiveis 
        WHERE data = '2026-01-22'
    """)
    dias = cursor.fetchall()
    if dias:
        print(f"   ⚠️ ENCONTRADO DIA BLOQUEADO:")
        for dia in dias:
            print(f"      - ID: {dia[0]}, Data: {dia[1]}, Motivo: {dia[2] if len(dia) > 2 else 'N/A'}")
    else:
        print("   ✅ Nenhum bloqueio encontrado")
    
    # Verificar horários especiais
    print("\n2️⃣ Horários especiais:")
    cursor.execute("""
        SELECT * FROM horarios_especiais 
        WHERE data = '2026-01-22'
    """)
    especiais = cursor.fetchall()
    if especiais:
        print(f"   ⚠️ ENCONTRADO HORÁRIO ESPECIAL:")
        for esp in especiais:
            print(f"      - {esp}")
    else:
        print("   ✅ Nenhum horário especial")
    
    # Verificar horários dos barbeiros para quarta-feira (dia 22 é quarta)
    print("\n3️⃣ Horários dos barbeiros (quarta-feira = dia 4):")
    cursor.execute("""
        SELECT b.nome, hb.dia_semana, hb.horario_inicio, hb.horario_fim, hb.ativo
        FROM horarios_barbeiros hb
        JOIN barbeiros b ON b.id = hb.barbeiro_id
        WHERE hb.dia_semana = 4
        ORDER BY b.nome
    """)
    horarios = cursor.fetchall()
    if horarios:
        for h in horarios:
            print(f"   - {h[0]}: {h[2]}-{h[3]} (ativo: {h[4]})")
    else:
        print("   ⚠️ NENHUM BARBEIRO TRABALHA ÀS QUARTAS!")
    
    # Verificar todos os barbeiros ativos
    print("\n4️⃣ Barbeiros ativos:")
    cursor.execute("""
        SELECT id, nome, ativo FROM barbeiros ORDER BY id
    """)
    barbeiros = cursor.fetchall()
    for b in barbeiros:
        print(f"   - ID {b[0]}: {b[1]} (ativo: {b[2]})")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

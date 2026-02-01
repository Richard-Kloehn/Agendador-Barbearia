from datetime import datetime

# Testar dia 03/02/2026
data = datetime.strptime('03/02/2026', '%d/%m/%Y')
python_weekday = data.weekday()
dia_sistema = python_weekday + 1
if dia_sistema == 7:
    dia_sistema = 0

print(f"Data: 03/02/2026")
print(f"Dia da semana: {data.strftime('%A')}")
print(f"Python weekday(): {python_weekday} (0=segunda, 6=domingo)")
print(f"Dia no sistema: {dia_sistema} (1=segunda, 6=sábado, 0=domingo)")
print(f"\nDeveria buscar horários para dia_semana = {dia_sistema}")

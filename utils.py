"""
Utilitários para validação e sanitização de dados
"""
import re
try:
    import bleach
    BLEACH_DISPONIVEL = True
except ImportError:
    BLEACH_DISPONIVEL = False
from datetime import datetime, timedelta

def sanitizar_texto(texto):
    """Remove HTML e scripts maliciosos de texto"""
    if not texto:
        return ""
    # Remove tags HTML permitindo apenas texto puro
    if BLEACH_DISPONIVEL:
        return bleach.clean(texto, tags=[], strip=True).strip()
    else:
        # Fallback simples se bleach não estiver disponível
        import html
        return html.escape(texto).strip()

def validar_telefone_brasileiro(telefone):
    """Valida formato de telefone brasileiro"""
    if not telefone:
        return False
    
    # Remove tudo que não é dígito
    telefone_limpo = re.sub(r'\D', '', telefone)
    
    # Deve ter 10 ou 11 dígitos (com ou sem 9 no celular)
    if len(telefone_limpo) < 10 or len(telefone_limpo) > 11:
        return False
    
    # DDD deve ser válido (11-99)
    if telefone_limpo[:2] < '11' or telefone_limpo[:2] > '99':
        return False
    
    return True

def validar_email(email):
    """Valida formato de email"""
    if not email:
        return True  # Email é opcional
    
    # Padrão básico de email
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(padrao, email) is not None

def validar_nome(nome):
    """Valida nome (apenas letras, espaços e acentos)"""
    if not nome or len(nome) < 3:
        return False
    
    # Permite letras, espaços, acentos e apóstrofos
    padrao = r'^[a-zA-ZÀ-ÿ\s\']+$'
    return re.match(padrao, nome) is not None

def validar_data_futura(data_str):
    """Verifica se a data é futura (não pode agendar no passado)"""
    try:
        data = datetime.fromisoformat(data_str.replace('Z', '+00:00'))
        return data > datetime.now()
    except:
        return False

def validar_prazo_minimo(data_hora, horas_minimo=2):
    """Verifica se a data está dentro do prazo mínimo permitido"""
    try:
        if isinstance(data_hora, str):
            data_hora = datetime.fromisoformat(data_hora.replace('Z', '+00:00'))
        
        tempo_ate = data_hora - datetime.now()
        horas_ate = tempo_ate.total_seconds() / 3600
        
        return horas_ate >= horas_minimo
    except:
        return False

def formatar_telefone_display(telefone):
    """Formata telefone para exibição: (11) 99999-9999"""
    if not telefone:
        return ""
    
    telefone_limpo = re.sub(r'\D', '', telefone)
    
    if len(telefone_limpo) == 11:
        return f"({telefone_limpo[:2]}) {telefone_limpo[2:7]}-{telefone_limpo[7:]}"
    elif len(telefone_limpo) == 10:
        return f"({telefone_limpo[:2]}) {telefone_limpo[2:6]}-{telefone_limpo[6:]}"
    
    return telefone

def limpar_telefone(telefone):
    """Remove formatação do telefone, deixando apenas números"""
    if not telefone:
        return ""
    return re.sub(r'\D', '', telefone)

def validar_horario_comercial(data_hora):
    """Verifica se o horário está dentro do horário comercial (6h-23h)"""
    if isinstance(data_hora, str):
        data_hora = datetime.fromisoformat(data_hora.replace('Z', '+00:00'))
    
    hora = data_hora.hour
    return 6 <= hora <= 23

def validar_observacoes(observacoes, max_length=500):
    """Valida observações do agendamento"""
    if not observacoes:
        return True
    
    # Sanitizar
    obs_limpa = sanitizar_texto(observacoes)
    
    # Verificar tamanho
    return len(obs_limpa) <= max_length

def validar_dados_agendamento(dados):
    """Valida todos os dados de um agendamento"""
    erros = []
    
    # Nome
    if not validar_nome(dados.get('nome_cliente', '')):
        erros.append("Nome inválido. Use apenas letras e espaços.")
    
    # Telefone (opcional, mas se fornecido deve ser válido)
    telefone = dados.get('telefone', '')
    if telefone and not validar_telefone_brasileiro(telefone):
        erros.append("Telefone inválido. Use formato: (11) 99999-9999")
    
    # Email (opcional, mas se fornecido deve ser válido)
    if not validar_email(dados.get('email', '')):
        erros.append("Email inválido.")
    
    # Data e hora
    data_hora = dados.get('data_hora')
    if not data_hora:
        erros.append("Data e hora são obrigatórios.")
    else:
        if not validar_data_futura(data_hora):
            erros.append("Não é possível agendar para o passado.")
        
        if not validar_horario_comercial(data_hora):
            erros.append("Horário fora do período comercial (6h-23h).")
    
    # Observações
    if not validar_observacoes(dados.get('observacoes', '')):
        erros.append("Observações muito longas (máximo 500 caracteres).")
    
    # Barbeiro e Serviço
    if not dados.get('barbeiro_id'):
        erros.append("Selecione um barbeiro.")
    
    if not dados.get('servico_id'):
        erros.append("Selecione um serviço.")
    
    return erros

def sanitizar_dados_agendamento(dados):
    """Sanitiza todos os dados de entrada de um agendamento"""
    return {
        'nome_cliente': sanitizar_texto(dados.get('nome_cliente', '')),
        'telefone': limpar_telefone(dados.get('telefone', '')),
        'email': sanitizar_texto(dados.get('email', '')),
        'data_hora': dados.get('data_hora'),
        'barbeiro_id': int(dados.get('barbeiro_id', 0)) if dados.get('barbeiro_id') else None,
        'servico_id': int(dados.get('servico_id', 0)) if dados.get('servico_id') else None,
        'observacoes': sanitizar_texto(dados.get('observacoes', ''))[:500]  # Limita a 500 chars
    }

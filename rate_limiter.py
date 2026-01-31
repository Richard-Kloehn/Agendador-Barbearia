"""
Middleware de Rate Limiting para proteger API de spam
======================================================
"""

from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta
import threading

# Dicionário para armazenar tentativas por IP
# Estrutura: {ip: {'tentativas': int, 'primeira_tentativa': datetime, 'bloqueado_ate': datetime}}
rate_limit_data = {}
rate_limit_lock = threading.Lock()

# Configurações
MAX_TENTATIVAS_POR_PERIODO = 10  # Máximo de requisições
PERIODO_MINUTOS = 5  # Em 5 minutos
TEMPO_BLOQUEIO_MINUTOS = 15  # Tempo de bloqueio após exceder

def limpar_dados_antigos():
    """Remove dados de IPs que não fazem requisições há mais de 1 hora"""
    with rate_limit_lock:
        agora = datetime.now()
        ips_para_remover = []
        
        for ip, dados in rate_limit_data.items():
            # Se última tentativa foi há mais de 1 hora, limpar
            if (agora - dados['primeira_tentativa']).total_seconds() > 3600:
                ips_para_remover.append(ip)
        
        for ip in ips_para_remover:
            del rate_limit_data[ip]

def rate_limit(max_requests=MAX_TENTATIVAS_POR_PERIODO, periodo_minutos=PERIODO_MINUTOS):
    """
    Decorator para rate limiting
    
    Args:
        max_requests: Número máximo de requisições permitidas
        periodo_minutos: Período de tempo em minutos
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Obter IP do cliente
            ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            if ip:
                ip = ip.split(',')[0].strip()  # Primeiro IP se houver múltiplos
            else:
                ip = request.remote_addr
            
            agora = datetime.now()
            
            with rate_limit_lock:
                # Limpar dados antigos periodicamente
                if len(rate_limit_data) % 100 == 0:  # A cada 100 acessos
                    limpar_dados_antigos()
                
                # Se IP não existe, criar entrada
                if ip not in rate_limit_data:
                    rate_limit_data[ip] = {
                        'tentativas': 1,
                        'primeira_tentativa': agora,
                        'bloqueado_ate': None
                    }
                    return f(*args, **kwargs)
                
                dados = rate_limit_data[ip]
                
                # Verificar se está bloqueado
                if dados['bloqueado_ate'] and agora < dados['bloqueado_ate']:
                    tempo_restante = int((dados['bloqueado_ate'] - agora).total_seconds() / 60)
                    return jsonify({
                        'erro': f'Muitas tentativas. Aguarde {tempo_restante} minuto(s) e tente novamente.',
                        'bloqueado': True,
                        'tempo_restante_minutos': tempo_restante
                    }), 429
                
                # Se bloqueio expirou, resetar
                if dados['bloqueado_ate'] and agora >= dados['bloqueado_ate']:
                    dados['tentativas'] = 1
                    dados['primeira_tentativa'] = agora
                    dados['bloqueado_ate'] = None
                    return f(*args, **kwargs)
                
                # Verificar se período expirou
                tempo_decorrido = (agora - dados['primeira_tentativa']).total_seconds() / 60
                if tempo_decorrido > periodo_minutos:
                    # Resetar contador
                    dados['tentativas'] = 1
                    dados['primeira_tentativa'] = agora
                    return f(*args, **kwargs)
                
                # Incrementar tentativas
                dados['tentativas'] += 1
                
                # Verificar se excedeu limite
                if dados['tentativas'] > max_requests:
                    dados['bloqueado_ate'] = agora + timedelta(minutes=TEMPO_BLOQUEIO_MINUTOS)
                    return jsonify({
                        'erro': f'Muitas tentativas. Você foi temporariamente bloqueado por {TEMPO_BLOQUEIO_MINUTOS} minutos.',
                        'bloqueado': True,
                        'tempo_restante_minutos': TEMPO_BLOQUEIO_MINUTOS
                    }), 429
                
                # Aviso quando está próximo do limite
                if dados['tentativas'] >= max_requests - 2:
                    restantes = max_requests - dados['tentativas']
                    print(f"⚠️ IP {ip} próximo do limite: {dados['tentativas']}/{max_requests} tentativas")
                
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def obter_estatisticas_rate_limit():
    """Retorna estatísticas de rate limiting para monitoramento"""
    with rate_limit_lock:
        total_ips = len(rate_limit_data)
        ips_bloqueados = sum(1 for dados in rate_limit_data.values() 
                            if dados['bloqueado_ate'] and dados['bloqueado_ate'] > datetime.now())
        
        return {
            'total_ips_rastreados': total_ips,
            'ips_bloqueados': ips_bloqueados,
            'detalhes': [
                {
                    'ip': ip,
                    'tentativas': dados['tentativas'],
                    'bloqueado': dados['bloqueado_ate'] > datetime.now() if dados['bloqueado_ate'] else False
                }
                for ip, dados in list(rate_limit_data.items())[:10]  # Primeiros 10
            ]
        }

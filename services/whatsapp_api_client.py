"""
Cliente API de WhatsApp - Para usar no site Render
===================================================
Este módulo faz requisições HTTP para o servidor VPS
que roda o script de automação WhatsApp.
"""

import requests
import os
from models import Agendamento

# URL do servidor VPS onde roda o whatsapp_api_server.py
WHATSAPP_API_URL = os.getenv('WHATSAPP_API_URL', '')  # Ex: http://seu-vps-ip:5001
WHATSAPP_API_TOKEN = os.getenv('WHATSAPP_API_TOKEN', '')

def esta_configurado():
    """Verifica se a API de WhatsApp está configurada"""
    return bool(WHATSAPP_API_URL and WHATSAPP_API_TOKEN)

def enviar_mensagem_whatsapp(numero, mensagem):
    """Envia mensagem via API do VPS"""
    if not esta_configurado():
        print("⚠️ API de WhatsApp não configurada (variáveis de ambiente ausentes)")
        return False
    
    try:
        response = requests.post(
            f'{WHATSAPP_API_URL}/enviar',
            json={'numero': numero, 'mensagem': mensagem},
            headers={'Authorization': f'Bearer {WHATSAPP_API_TOKEN}'},
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"✅ WhatsApp enviado para {numero}")
            return True
        else:
            print(f"❌ Erro ao enviar WhatsApp: {response.json().get('erro', 'Erro desconhecido')}")
            return False
    
    except requests.exceptions.Timeout:
        print(f"⏱️ Timeout ao enviar WhatsApp para {numero}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão com API WhatsApp: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado ao enviar WhatsApp: {e}")
        return False

def enviar_confirmacao_agendamento(agendamento):
    """Envia confirmação de agendamento"""
    if not isinstance(agendamento, Agendamento):
        print("❌ Objeto de agendamento inválido")
        return False
    
    if not agendamento.telefone:
        print("⚠️ Agendamento sem telefone")
        return False
    
    # Criar mensagem de confirmação
    from datetime import datetime as dt
    saudacao = "Bom dia" if dt.now().hour < 12 else ("Boa tarde" if dt.now().hour < 18 else "Boa noite")
    
    data_formatada = agendamento.data_hora.strftime('%d/%m')
    hora_formatada = agendamento.data_hora.strftime('%H:%M')
    dia_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo'][agendamento.data_hora.weekday()]
    
    nome_barbeiro = agendamento.barbeiro.nome if agendamento.barbeiro else "um dos nossos barbeiros"
    nome_servico = agendamento.servico.nome if agendamento.servico else "serviço"
    
    mensagem = f"""{saudacao}, {agendamento.nome_cliente}! ✂️

✅ Confirmação de Agendamento

📅 *Data:* {dia_semana}, {data_formatada}
🕐 *Horário:* {hora_formatada}
✂️ *Serviço:* {nome_servico}
👤 *Barbeiro:* {nome_barbeiro}

⚠️ *Importante:* Esta é uma mensagem automática.

Navalha's Barber Club aguarda você! 💈"""
    
    numero = agendamento.telefone
    if not numero.startswith('55'):
        numero = '55' + numero
    
    return enviar_mensagem_whatsapp(numero, mensagem)

def enviar_lembrete_whatsapp(agendamento):
    """Envia lembrete 24h antes"""
    if not isinstance(agendamento, Agendamento):
        return False
    
    if not agendamento.telefone:
        return False
    
    from datetime import datetime as dt
    saudacao = "Bom dia" if dt.now().hour < 12 else ("Boa tarde" if dt.now().hour < 18 else "Boa noite")
    
    data_formatada = agendamento.data_hora.strftime('%d/%m')
    hora_formatada = agendamento.data_hora.strftime('%H:%M')
    
    nome_barbeiro = agendamento.barbeiro.nome if agendamento.barbeiro else "um dos nossos barbeiros"
    
    mensagem = f"""{saudacao}, {agendamento.nome_cliente}! ✂️

🔔 *Lembrete de Agendamento*

Seu horário é AMANHÃ!

📅 Data: {data_formatada}
🕐 Horário: {hora_formatada}
👤 Barbeiro: {nome_barbeiro}

Até logo! 💈"""
    
    numero = agendamento.telefone
    if not numero.startswith('55'):
        numero = '55' + numero
    
    return enviar_mensagem_whatsapp(numero, mensagem)

from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

# Configuração Twilio
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')

def enviar_lembrete_whatsapp(agendamento):
    """
    Envia lembrete de agendamento via WhatsApp usando Twilio
    
    Para configurar:
    1. Criar conta no Twilio (https://www.twilio.com)
    2. Ativar WhatsApp Sandbox ou configurar número próprio
    3. Adicionar credenciais no arquivo .env
    """
    
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        print("⚠️  Credenciais Twilio não configuradas. Lembrete não enviado.")
        return False
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Formatar data e hora
        data_formatada = agendamento.data_hora.strftime('%d/%m/%Y às %H:%M')
        
        # URL de confirmação
        base_url = os.getenv('BASE_URL', 'http://localhost:5000')
        url_confirmacao = f"{base_url}/confirmar/{agendamento.token_confirmacao}"
        
        # Incluir informações de barbeiro e serviço
        barbeiro_info = f"Barbeiro: {agendamento.barbeiro.nome}\n" if agendamento.barbeiro else ""
        servico_info = f"Serviço: {agendamento.servico.nome}\n" if agendamento.servico else ""
        
        # Mensagem
        mensagem = f"""
Olá {agendamento.nome_cliente}! 👋

Este é um lembrete do seu agendamento na barbearia:

📅 Data: {data_formatada}
{barbeiro_info}{servico_info}
Por favor, confirme sua presença acessando:
{url_confirmacao}

Se não puder comparecer, cancele pelo mesmo link para liberar o horário.

Caso não responda, seu horário será automaticamente confirmado.

Obrigado! ✂️
        """.strip()
        
        # Enviar mensagem
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=mensagem,
            to=f'whatsapp:+55{agendamento.telefone}'
        )
        
        print(f"✅ Lembrete enviado para {agendamento.nome_cliente}: {message.sid}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao enviar lembrete: {str(e)}")
        return False

def enviar_confirmacao_agendamento(agendamento):
    """Envia confirmação imediata após criação do agendamento"""
    
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        print("⚠️  Credenciais Twilio não configuradas.")
        return False
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        data_formatada = agendamento.data_hora.strftime('%d/%m/%Y às %H:%M')
        
        # Incluir informações de barbeiro e serviço
        barbeiro_info = f"Barbeiro: {agendamento.barbeiro.nome}\n" if agendamento.barbeiro else ""
        servico_info = f"Serviço: {agendamento.servico.nome}\n" if agendamento.servico else ""
        
        mensagem = f"""
✅ Agendamento confirmado!

Olá {agendamento.nome_cliente},

Seu horário foi agendado com sucesso:

📅 {data_formatada}
{barbeiro_info}{servico_info}
Você receberá um lembrete 24 horas antes.

Obrigado! ✂️
        """.strip()
        
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=mensagem,
            to=f'whatsapp:+55{agendamento.telefone}'
        )
        
        print(f"✅ Confirmação enviada: {message.sid}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao enviar confirmação: {str(e)}")
        return False

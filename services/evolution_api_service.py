"""
Serviço de WhatsApp usando Evolution API
==========================================
API REST gratuita e open source para WhatsApp
Repositório: https://github.com/EvolutionAPI/evolution-api
"""

import requests
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class EvolutionAPIService:
    """Cliente para Evolution API"""
    
    def __init__(self):
        # URL da sua instância Evolution API (pode ser hospedada no Railway/Render)
        self.api_url = os.getenv('EVOLUTION_API_URL', '').rstrip('/')
        # API Key global (configurada no Evolution API)
        self.api_key = os.getenv('EVOLUTION_API_KEY', '')
        # Nome da instância (configurável, ex: "barbearia")
        self.instance_name = os.getenv('EVOLUTION_INSTANCE_NAME', 'barbearia')
        
    def esta_configurado(self) -> bool:
        """Verifica se a API está configurada"""
        configurado = bool(self.api_url and self.api_key)
        if not configurado:
            logger.warning("⚠️ Evolution API não configurada (EVOLUTION_API_URL e EVOLUTION_API_KEY)")
        else:
            logger.info(f"✅ Evolution API configurada: {self.api_url}")
        return configurado
    
    def formatar_numero(self, numero: str) -> str:
        """
        Formata número para padrão do WhatsApp
        Ex: 47992849526 -> 5547992849526
        """
        # Remove caracteres não numéricos
        numero_limpo = ''.join(filter(str.isdigit, numero))
        
        # Adiciona código do Brasil se não tiver
        if not numero_limpo.startswith('55'):
            numero_limpo = '55' + numero_limpo
        
        return numero_limpo
    
    def verificar_status_instancia(self) -> dict:
        """Verifica status da instância"""
        if not self.esta_configurado():
            return {'status': 'error', 'message': 'API não configurada'}
        
        try:
            headers = {
                'apikey': self.api_key
            }
            
            response = requests.get(
                f'{self.api_url}/instance/connectionState/{self.instance_name}',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'status': 'error', 'message': f'HTTP {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Erro ao verificar status: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def enviar_mensagem(self, numero: str, mensagem: str) -> bool:
        """
        Envia mensagem de texto via Evolution API
        
        Args:
            numero: Número do destinatário (ex: 47992849526)
            mensagem: Texto da mensagem
            
        Returns:
            bool: True se enviado com sucesso
        """
        if not self.esta_configurado():
            logger.error("⚠️ Evolution API não configurada")
            return False
        
        try:
            numero_formatado = self.formatar_numero(numero)
            
            headers = {
                'apikey': self.api_key,
                'Content-Type': 'application/json'
            }
            
            # Formato do payload para Evolution API
            payload = {
                'number': numero_formatado,
                'text': mensagem
            }
            
            url = f'{self.api_url}/message/sendText/{self.instance_name}'
            
            logger.info(f"🔄 Enviando mensagem via Evolution API")
            logger.info(f"   URL: {url}")
            logger.info(f"   Para: {numero_formatado}")
            logger.info(f"   Instância: {self.instance_name}")
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=60
            )
            
            logger.info(f"📡 Resposta HTTP: {response.status_code}")
            
            if response.status_code in [200, 201]:
                result = response.json()
                logger.info(f"✅ Mensagem enviada com sucesso via Evolution API")
                logger.info(f"   Resposta: {result}")
                return True
            else:
                logger.error(f"❌ Erro Evolution API ({response.status_code}): {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error(f"⏱️ Timeout ao enviar mensagem para {numero}")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao enviar mensagem: {e}")
            return False
    
    def obter_qrcode(self) -> dict:
        """Obtém QR Code para conectar a instância"""
        if not self.esta_configurado():
            return {'error': 'API não configurada'}
        
        try:
            headers = {
                'apikey': self.api_key
            }
            
            response = requests.get(
                f'{self.api_url}/instance/connect/{self.instance_name}',
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f'HTTP {response.status_code}: {response.text}'}
                
        except Exception as e:
            return {'error': str(e)}


# Instância global
_evolution_service = EvolutionAPIService()


def enviar_confirmacao_agendamento(agendamento) -> bool:
    """
    Envia confirmação de agendamento via Evolution API
    
    Args:
        agendamento: Objeto Agendamento do modelo
        
    Returns:
        bool: True se enviado com sucesso
    """
    if not agendamento.telefone:
        logger.warning("⚠️ Agendamento sem telefone")
        return False
    
    # Determinar saudação baseada no horário ATUAL
    hora_atual = datetime.now().hour
    if hora_atual < 12:
        saudacao = "Bom dia"
    elif hora_atual < 18:
        saudacao = "Boa tarde"
    else:
        saudacao = "Boa noite"
    
    # Formatar data e hora
    data_formatada = agendamento.data_hora.strftime('%d/%m/%Y')
    hora_formatada = agendamento.data_hora.strftime('%H:%M')
    
    dias_semana = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 
                  'Sexta-feira', 'Sábado', 'Domingo']
    dia_semana = dias_semana[agendamento.data_hora.weekday()]
    
    # Informações do agendamento
    nome_barbeiro = agendamento.barbeiro.nome if agendamento.barbeiro else "um de nossos barbeiros"
    nome_servico = agendamento.servico.nome if agendamento.servico else "serviço"
    
    # Nome da barbearia
    try:
        from models import ConfiguracaoBarbearia
        from database import db
        config = ConfiguracaoBarbearia.query.first()
        nome_barbearia = config.nome_barbearia if config and config.nome_barbearia else "Navalha's Barber Club"
    except:
        nome_barbearia = "Navalha's Barber Club"
    
    # Criar mensagem
    mensagem = f"""{saudacao}, {agendamento.nome_cliente}! ✂️

✅ Confirmação de Agendamento

📅 Data: {dia_semana}, {data_formatada}
🕐 Horário: {hora_formatada}
✂️ Serviço: {nome_servico}
👤 Barbeiro: {nome_barbeiro}

❌ Caso precise cancelar, acesse:
https://agendador-barbearia.up.railway.app

⚠️ Importante: Esta é uma mensagem automática. Não é necessário responder.

{nome_barbearia} aguarda você! 💈"""
    
    return _evolution_service.enviar_mensagem(agendamento.telefone, mensagem)


def enviar_lembrete_whatsapp(agendamento) -> bool:
    """
    Envia lembrete 24h antes via Evolution API
    
    Args:
        agendamento: Objeto Agendamento do modelo
        
    Returns:
        bool: True se enviado com sucesso
    """
    if not agendamento.telefone:
        logger.warning("⚠️ Agendamento sem telefone")
        return False
    
    # Determinar saudação baseada no horário ATUAL
    hora_atual = datetime.now().hour
    if hora_atual < 12:
        saudacao = "Bom dia"
    elif hora_atual < 18:
        saudacao = "Boa tarde"
    else:
        saudacao = "Boa noite"
    
    # Formatar data e hora (sem o ano)
    data_formatada = agendamento.data_hora.strftime('%d/%m')
    hora_formatada = agendamento.data_hora.strftime('%H:%M')
    
    dias_semana = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 
                  'Sexta-feira', 'Sábado', 'Domingo']
    dia_semana = dias_semana[agendamento.data_hora.weekday()]
    
    # Informações do agendamento
    nome_barbeiro = agendamento.barbeiro.nome if agendamento.barbeiro else "um dos nossos barbeiros"
    nome_servico = agendamento.servico.nome if agendamento.servico else "serviço"
    
    # Nome da barbearia
    try:
        from models import ConfiguracaoBarbearia
        from database import db
        config = ConfiguracaoBarbearia.query.first()
        nome_barbearia = config.nome_barbearia if config and config.nome_barbearia else "Navalha's Barber Club"
    except:
        nome_barbearia = "Navalha's Barber Club"
    
    # Criar mensagem de lembrete
    mensagem = f"""{saudacao}, {agendamento.nome_cliente}! ✂️

⏰ Lembrete de Agendamento

📅 Data: {dia_semana}, {data_formatada}
🕐 Horário: {hora_formatada}
✂️ Serviço: {nome_servico}
👤 Barbeiro: {nome_barbeiro}

❌ Caso precise cancelar, acesse:
https://agendador-barbearia.up.railway.app

⚠️ Importante: Esta é uma mensagem automática. Não é necessário responder.

{nome_barbearia} aguarda você! 💈"""
    
    return _evolution_service.enviar_mensagem(agendamento.telefone, mensagem)

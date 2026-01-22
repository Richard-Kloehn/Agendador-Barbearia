"""
Serviço de WhatsApp integrado com whapi.cloud
==============================================
Envia mensagens automáticas via whapi.cloud API
Documentação: https://whapi.cloud/pt/docs
"""

import requests
import os
from datetime import datetime
from typing import Optional

class WhapiService:
    """Cliente para integração com whapi.cloud"""
    
    def __init__(self):
        self.api_url = os.getenv('WHAPI_API_URL', 'https://gate.whapi.cloud')
        self.api_token = os.getenv('WHAPI_API_TOKEN', '')
        # Channel ID não é mais necessário - o token já identifica o canal
        
    def esta_configurado(self) -> bool:
        """Verifica se a API está configurada"""
        return bool(self.api_token)
    
    def formatar_numero(self, numero: str) -> str:
        """
        Formata número para padrão internacional
        Ex: (11) 98765-4321 -> 5511987654321
        """
        # Remove caracteres não numéricos
        numero_limpo = ''.join(filter(str.isdigit, numero))
        
        # Adiciona código do Brasil se não tiver
        if not numero_limpo.startswith('55'):
            numero_limpo = '55' + numero_limpo
        
        return numero_limpo
    
    def enviar_mensagem(self, numero: str, mensagem: str) -> bool:
        """
        Envia mensagem de texto via whapi.cloud
        
        Args:
            numero: Número do destinatário (formato: (11) 98765-4321 ou 11987654321)
            mensagem: Texto da mensagem
            
        Returns:
            bool: True se enviado com sucesso
        """
        if not self.esta_configurado():
            print("⚠️ whapi.cloud não configurado (defina WHAPI_API_TOKEN)")
            return False
        
        try:
            numero_formatado = self.formatar_numero(numero)
            
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'typing_time': 0,
                'to': numero_formatado,
                'body': mensagem
            }
            
            # URL completa incluindo o channel ID
            url = f'{self.api_url}/messages/text'
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✅ WhatsApp enviado para {numero} via whapi.cloud")
                print(f"   ID da mensagem: {result.get('id', 'N/A')}")
                return True
            else:
                # Tentar obter mais detalhes do erro
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', error_data.get('error', 'Erro desconhecido'))
                    print(f"❌ Erro whapi.cloud ({response.status_code}): {error_msg}")
                    print(f"   Resposta completa: {error_data}")
                except:
                    print(f"❌ Erro whapi.cloud ({response.status_code}): {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            print(f"⏱️ Timeout ao enviar WhatsApp para {numero}")
            return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro de conexão com whapi.cloud: {e}")
            return False
        except Exception as e:
            print(f"❌ Erro inesperado ao enviar WhatsApp: {e}")
            return False
    
    def enviar_confirmacao_agendamento(self, agendamento) -> bool:
        """
        Envia confirmação de agendamento
        
        Args:
            agendamento: Objeto Agendamento do modelo
            
        Returns:
            bool: True se enviado com sucesso
        """
        if not agendamento.telefone:
            print("⚠️ Agendamento sem telefone")
            return False
        
        # Determinar saudação baseada no horário
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
        
        # Dia da semana em português
        dias_semana = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 
                      'Sexta-feira', 'Sábado', 'Domingo']
        dia_semana = dias_semana[agendamento.data_hora.weekday()]
        
        # Informações do agendamento
        nome_barbeiro = agendamento.barbeiro.nome if agendamento.barbeiro else "um de nossos barbeiros"
        nome_servico = agendamento.servico.nome if agendamento.servico else "serviço"
        
        # Criar mensagem personalizada
        mensagem = f"""{saudacao}, {agendamento.nome_cliente}! ✂️

✅ *Agendamento Confirmado*

📅 *Data:* {dia_semana}, {data_formatada}
🕐 *Horário:* {hora_formatada}
✂️ *Serviço:* {nome_servico}
👤 *Profissional:* {nome_barbeiro}

📍 *Local:* Navalha's Barber Club

⚠️ *IMPORTANTE:*
• Chegue com 5 minutos de antecedência
• Em caso de imprevistos, avise com antecedência
• Esta é uma mensagem automática

Nos vemos em breve! 💈"""
        
        return self.enviar_mensagem(agendamento.telefone, mensagem)
    
    def enviar_lembrete_24h(self, agendamento) -> bool:
        """
        Envia lembrete 24 horas antes do agendamento
        Usa a mesma mensagem do script anterior com selenium
        
        Args:
            agendamento: Objeto Agendamento do modelo
            
        Returns:
            bool: True se enviado com sucesso
        """
        if not agendamento.telefone:
            print("⚠️ Agendamento sem telefone")
            return False
        
        # Determinar saudação baseada no horário
        hora_atual = datetime.now().hour
        if hora_atual < 12:
            saudacao = "Bom dia"
        elif hora_atual < 18:
            saudacao = "Boa tarde"
        else:
            saudacao = "Boa noite"
        
        # Formatar data e hora (sem o ano, igual ao selenium)
        data_formatada = agendamento.data_hora.strftime('%d/%m')
        hora_formatada = agendamento.data_hora.strftime('%H:%M')
        
        # Dia da semana em português
        dias_semana = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 
                      'Sexta-feira', 'Sábado', 'Domingo']
        dia_semana = dias_semana[agendamento.data_hora.weekday()]
        
        # Informações do agendamento
        nome_barbeiro = agendamento.barbeiro.nome if agendamento.barbeiro else "um dos nossos barbeiros"
        nome_servico = agendamento.servico.nome if agendamento.servico else "serviço"
        
        # Nome da barbearia (tentar pegar do banco)
        try:
            from models import ConfiguracaoBarbearia
            config = ConfiguracaoBarbearia.query.first()
            nome_barbearia = config.nome_barbearia if config and config.nome_barbearia else "Navalha's Barber Club"
        except:
            nome_barbearia = "Navalha's Barber Club"
        
        # URL do site para cancelamento
        base_url = os.getenv('BASE_URL', 'http://localhost:5000')
        
        # Criar mensagem (igual ao script selenium)
        mensagem = f"""{saudacao}, {agendamento.nome_cliente}! ✂️

✅ Confirmação de Agendamento

📅 *Data:* {dia_semana}, {data_formatada}
🕐 *Horário:* {hora_formatada}
✂️ *Serviço:* {nome_servico}
👤 *Barbeiro:* {nome_barbeiro}

❌ *Caso precise cancelar*, acesse o site e faça o cancelamento:
{base_url}

⚠️ *Importante:* Esta é uma mensagem automática. Não é necessário responder.

{nome_barbearia} aguarda você! 💈"""
        
        return self.enviar_mensagem(agendamento.telefone, mensagem)
    
    def enviar_lembrete_2h(self, agendamento) -> bool:
        """
        Envia lembrete 2 horas antes do agendamento
        
        Args:
            agendamento: Objeto Agendamento do modelo
            
        Returns:
            bool: True se enviado com sucesso
        """
        if not agendamento.telefone:
            print("⚠️ Agendamento sem telefone")
            return False
        
        hora_formatada = agendamento.data_hora.strftime('%H:%M')
        nome_barbeiro = agendamento.barbeiro.nome if agendamento.barbeiro else "um de nossos barbeiros"
        
        mensagem = f"""⏰ *Seu horário é HOJE!*

Olá, {agendamento.nome_cliente}!

Seu agendamento é daqui a pouco:

🕐 *Horário:* {hora_formatada}
👤 *Profissional:* {nome_barbeiro}

📍 *Local:* Navalha's Barber Club

Estamos te esperando! ✂️💈"""
        
        return self.enviar_mensagem(agendamento.telefone, mensagem)
    
    def verificar_status_canal(self) -> dict:
        """
        Verifica o status do canal/número no whapi.cloud
        
        Returns:
            dict: Informações do canal
        """
        if not self.esta_configurado():
            return {'erro': 'API não configurada'}
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_token}'
            }
            
            response = requests.get(
                f'{self.api_url}/settings',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'erro': f'Status {response.status_code}'}
                
        except Exception as e:
            return {'erro': str(e)}


# Instância global do serviço
_whapi_service = WhapiService()

# Funções de conveniência para manter compatibilidade com código existente
def enviar_confirmacao_agendamento(agendamento) -> bool:
    """Envia confirmação de agendamento"""
    return _whapi_service.enviar_confirmacao_agendamento(agendamento)

def enviar_lembrete_whatsapp(agendamento) -> bool:
    """Envia lembrete de agendamento"""
    return _whapi_service.enviar_lembrete_24h(agendamento)

def enviar_lembrete_2h(agendamento) -> bool:
    """Envia lembrete 2 horas antes"""
    return _whapi_service.enviar_lembrete_2h(agendamento)

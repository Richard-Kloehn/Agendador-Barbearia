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
        # Garantir que URL não tenha barra final
        api_url = os.getenv('WHAPI_API_URL', 'https://gate.whapi.cloud')
        self.api_url = api_url.rstrip('/')
        self.api_token = os.getenv('WHAPI_API_TOKEN', '')
        self.channel_id = os.getenv('WHAPI_CHANNEL_ID', '')  # ID do canal (opcional)
        
    def esta_configurado(self) -> bool:
        """Verifica se a API está configurada"""
        configurado = bool(self.api_token)
        if not configurado:
            print("⚠️ WHAPI_API_TOKEN não configurado nas variáveis de ambiente")
        else:
            # Mostrar apenas primeiros e últimos caracteres do token para segurança
            token_preview = f"{self.api_token[:8]}...{self.api_token[-4:]}" if len(self.api_token) > 12 else "***"
            print(f"✅ WHAPI configurado (Token: {token_preview})")
        return configurado
    
    def validar_numero_whatsapp(self, numero: str) -> dict:
        """
        Valida número no WhatsApp usando POST /contacts da WHAPI.
        Retorna o wa_id correto normalizado pela API.
        
        RECOMENDADO usar este método antes de enviar mensagens!
        
        Args:
            numero: Número no formato (XX) XXXXX-XXXX ou similar
            
        Returns:
            dict: {
                'valido': bool,         # True se número tem WhatsApp ativo
                'wa_id': str,           # ID do chat (ex: 5547991557386@s.whatsapp.net)
                'numero': str           # Número formatado (ex: 5547991557386)
            }
        """
        # Primeiro formata o número com as regras do Whapi
        numero_formatado = self.formatar_numero(numero)
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        url = f"{self.api_url}/contacts"
        payload = {
            "force_check": False,
            "contacts": [numero_formatado]
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                contacts = data.get('contacts', [])
                
                if contacts and len(contacts) > 0:
                    resultado = contacts[0]
                    status = resultado.get('status')
                    wa_id = resultado.get('wa_id')
                    
                    if status == 'valid' and wa_id:
                        # Extrair apenas o número (sem @s.whatsapp.net)
                        numero_correto = wa_id.replace('@s.whatsapp.net', '')
                        print(f"✅ Número validado: {numero} -> {numero_correto}")
                        
                        return {
                            'valido': True,
                            'wa_id': wa_id,
                            'numero': numero_correto
                        }
                    else:
                        print(f"❌ Número inválido: {numero} (não tem WhatsApp)")
                        return {
                            'valido': False,
                            'wa_id': None,
                            'numero': numero_formatado
                        }
            
            print(f"⚠️ Erro ao validar número: HTTP {response.status_code}")
            # Em caso de erro, retorna formato básico
            return {
                'valido': None,  # Desconhecido
                'wa_id': None,
                'numero': numero_formatado
            }
            
        except Exception as e:
            print(f"⚠️ Exceção ao validar número: {e}")
            return {
                'valido': None,
                'wa_id': None,
                'numero': numero_formatado
            }
    
    def formatar_numero(self, numero: str) -> str:
        """
        Formata número brasileiro seguindo as regras oficiais do Whapi:
        
        - DDDs 11-19, 21, 22, 24, 27, 28: OBRIGATÓRIO adicionar "9" após o DDD
        - Outros DDDs: REMOVER o "9" se presente
        - Formato final: 55DDNXXXXXXXX (ex: 5547991557386 ou 559281723241)
        
        Para validação completa, use validar_numero_whatsapp().
        
        Args:
            numero: Número no formato (XX) XXXXX-XXXX ou similar
            
        Returns:
            str: Número formatado no padrão Whapi
        """
        if not numero:
            raise ValueError("Número de telefone vazio")
        
        # Remove caracteres não numéricos
        numero_limpo = ''.join(filter(str.isdigit, numero))
        
        if not numero_limpo:
            raise ValueError(f"Número inválido (sem dígitos): {numero}")
        
        # Remove código do Brasil se tiver
        if numero_limpo.startswith('55'):
            numero_limpo = numero_limpo[2:]
        
        if len(numero_limpo) < 10:
            raise ValueError(f"Número muito curto: {numero_limpo}")
        
        # Extrair DDD e resto do número
        ddd = numero_limpo[:2]
        resto = numero_limpo[2:]
        
        # DDDs que OBRIGATORIAMENTE precisam do 9
        ddds_com_9 = ['11', '12', '13', '14', '15', '16', '17', '18', '19',
                      '21', '22', '24', '27', '28']
        
        if ddd in ddds_com_9:
            # Verificar se já tem o 9
            if resto.startswith('9') and len(resto) == 9:
                # Já está correto
                numero_final = numero_limpo
            elif len(resto) == 8:
                # Adicionar o 9
                numero_final = ddd + '9' + resto
                print(f"   ➕ Adicionado 9 para DDD {ddd}")
            else:
                # Já tem 9 dígitos e começa com 9, manter
                numero_final = numero_limpo
        else:
            # Outros DDDs: REMOVER o 9 se presente
            if resto.startswith('9') and len(resto) == 9:
                # Remover o 9
                numero_final = ddd + resto[1:]
                print(f"   ➖ Removido 9 para DDD {ddd}")
            else:
                # Já está sem o 9
                numero_final = numero_limpo
        
        # Adicionar código do Brasil
        return '55' + numero_final
    
    def enviar_mensagem(self, numero: str, mensagem: str, validar: bool = True) -> bool:
        """
        Envia mensagem de texto via whapi.cloud
        
        Args:
            numero: Número do destinatário (formato: (11) 98765-4321 ou 11987654321)
            mensagem: Texto da mensagem
            validar: Se True, valida o número antes de enviar usando POST /contacts (recomendado)
            
        Returns:
            bool: True se enviado com sucesso
        """
        if not self.esta_configurado():
            print("⚠️ whapi.cloud não configurado (defina WHAPI_API_TOKEN)")
            return False
        
        try:
            # Validar número antes de enviar (obtém wa_id correto)
            if validar:
                validacao = self.validar_numero_whatsapp(numero)
                
                if validacao['valido'] == False:
                    print(f"❌ Número {numero} não tem WhatsApp ativo")
                    return False
                
                # Usar wa_id retornado pela API (formato: 554791557386@s.whatsapp.net)
                if validacao['wa_id']:
                    # Converter para formato @c.us que a API de envio usa
                    numero_envio = validacao['wa_id'].replace('@s.whatsapp.net', '')
                else:
                    numero_envio = validacao['numero']
            else:
                # Formatação básica sem validação
                numero_envio = self.formatar_numero(numero)
            
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            # Formato correto do payload WHAPI para mensagens de texto
            payload = {
                'to': numero_envio,  # Apenas o número, sem @c.us ou @s.whatsapp.net
                'body': mensagem     # 'body' ao invés de 'message'
            }
            
            # Endpoint correto do WHAPI para enviar mensagem de texto
            url = f'{self.api_url}/messages/text'
            
            print(f"🔄 Enviando WhatsApp via WHAPI")
            print(f"   URL: {url}")
            print(f"   Para: {numero_envio}")
            print(f"   Número original: {numero}")
            print(f"   Payload: {payload}")
            print(f"   Token: {self.api_token[:10]}...{self.api_token[-4:]}")
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=60  # Aumentar para 60 segundos
            )
            
            print(f"📡 Resposta HTTP: {response.status_code}")
            print(f"📄 Resposta completa (raw): {response.text}")
            
            if response.status_code in [200, 201]:
                try:
                    result = response.json()
                    print(f"📋 JSON da resposta: {result}")
                    
                    # Verificar se houve erro na resposta mesmo com status 200
                    if 'error' in result or 'errors' in result:
                        print(f"❌ WHAPI retornou erro: {result}")
                        return False
                    
                    print(f"✅ WhatsApp enviado para {numero} via whapi.cloud")
                    print(f"   Número formatado: {numero_envio}")
                    print(f"   ID da mensagem: {result.get('id', result.get('message_id', 'N/A'))}")
                    return True
                except Exception as e:
                    print(f"❌ Erro ao processar resposta JSON: {e}")
                    print(f"   Resposta raw: {response.text}")
                    return False
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
        
        # Determinar saudação baseada no horário ATUAL (quando a mensagem é enviada)
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
        
        # Nome da barbearia
        try:
            from models import ConfiguracaoBarbearia
            config = ConfiguracaoBarbearia.query.first()
            nome_barbearia = config.nome_barbearia if config and config.nome_barbearia else "Navalha's Barber Club"
        except:
            nome_barbearia = "Navalha's Barber Club"
        
        # URL correto do site
        base_url = 'https://agendador-barbearia.up.railway.app'
        
        # Criar mensagem personalizada
        mensagem = f"""{saudacao}, {agendamento.nome_cliente}! ✂️

✅ Confirmação de Agendamento

📅 Data: {dia_semana}, {data_formatada}
🕐 Horário: {hora_formatada}
✂️ Serviço: {nome_servico}
👤 Barbeiro: {nome_barbeiro}

❌ Caso precise cancelar, acesse:
{base_url}

⚠️ Importante: Esta é uma mensagem automática. Não é necessário responder.

{nome_barbearia} aguarda você! 💈"""
        
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
        
        # Determinar saudação baseada no horário ATUAL (quando o lembrete é enviado)
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
        
        # URL correto do site
        base_url = 'https://agendador-barbearia.up.railway.app'
        
        # Criar mensagem (igual ao script selenium)
        mensagem = f"""{saudacao}, {agendamento.nome_cliente}! ✂️

✅ Confirmação de Agendamento

📅 Data: {dia_semana}, {data_formatada}
🕐 Horário: {hora_formatada}
✂️ Serviço: {nome_servico}
👤 Barbeiro: {nome_barbeiro}

❌ Caso precise cancelar, acesse:
{base_url}

⚠️ Importante: Esta é uma mensagem automática. Não é necessário responder.

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

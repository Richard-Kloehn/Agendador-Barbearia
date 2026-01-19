"""
Serviço de WhatsApp usando Automação Web
==========================================
Sistema profissional para envio de mensagens WhatsApp
com proteção contra bloqueio e sistema de fila.
"""

import time
import logging
import os
import shutil
import threading
from datetime import datetime, time as time_obj
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException
)
from urllib.parse import quote
from webdriver_manager.chrome import ChromeDriverManager
import queue

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('whatsapp_automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WhatsAppService:
    """
    Serviço profissional de WhatsApp com proteção contra bloqueio
    """
    
    # Limites de segurança
    MAX_MENSAGENS_POR_HORA = 15  # Bem conservador
    INTERVALO_ENTRE_MENSAGENS = 8  # 8 segundos (seguro)
    INTERVALO_MINIMO_MESMA_CONVERSA = 60  # 1 minuto entre mensagens para mesmo número
    
    def __init__(self):
        self.driver = None
        self.wait_timeout = 30
        self.fila_mensagens = queue.Queue()
        self.mensagens_enviadas_hora = []
        self.ultimos_envios = {}  # {numero: timestamp}
        self.lock = threading.Lock()
        self.is_running = False
        self.worker_thread = None
        self.headless = False  # Será determinado automaticamente
        
    def obter_saudacao(self):
        """Retorna saudação apropriada baseada no horário"""
        hora_atual = datetime.now().hour
        
        if 5 <= hora_atual < 12:
            return "Bom dia"
        elif 12 <= hora_atual < 18:
            return "Boa tarde"
        else:
            return "Boa noite"
    
    def criar_mensagem_confirmacao(self, agendamento):
        """Cria mensagem de confirmação personalizada"""
        from models import ConfiguracaoBarbearia
        from database import db
        
        saudacao = self.obter_saudacao()
        
        # Formatar data e hora
        data_formatada = agendamento.data_hora.strftime('%d/%m')  # Sem o ano
        hora_formatada = agendamento.data_hora.strftime('%H:%M')
        dia_semana = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 
                     'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo'][agendamento.data_hora.weekday()]
        
        # Informações do agendamento
        nome_barbeiro = agendamento.barbeiro.nome if agendamento.barbeiro else "um dos nossos barbeiros"
        nome_servico = agendamento.servico.nome if agendamento.servico else "serviço"
        
        # Nome da barbearia do banco de dados
        try:
            config = ConfiguracaoBarbearia.query.first()
            nome_barbearia = config.nome_barbearia if config else "Barbearia"
        except:
            nome_barbearia = "Barbearia"
        
        # URL do site para cancelamento
        base_url = os.getenv('BASE_URL', 'http://localhost:5000')
        
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
        
        return mensagem
    
    def iniciar_navegador(self, limpar_sessao=False, tentar_novamente=True, forcar_visivel=False):
        """
        Inicia o navegador Chrome de forma inteligente
        
        - Primeira vez (sem sessão): Abre VISÍVEL para escanear QR Code
        - Já logado (com sessão): Abre INVISÍVEL (headless)
        """
        try:
            session_dir = os.path.abspath('whatsapp_session')
            
            # Detecta se é primeira vez ou já está logado
            sessao_existe = os.path.exists(session_dir) and os.path.isdir(session_dir)
            tem_arquivos_sessao = False
            
            if sessao_existe:
                # Verifica se tem arquivos de sessão (não apenas pasta vazia)
                try:
                    arquivos = os.listdir(session_dir)
                    tem_arquivos_sessao = len(arquivos) > 0
                except:
                    tem_arquivos_sessao = False
            
            # Determina modo de operação
            if forcar_visivel:
                self.headless = False
                modo = "VISÍVEL (forçado)"
            elif not sessao_existe or not tem_arquivos_sessao:
                # Primeira vez - precisa escanear QR Code
                self.headless = False
                modo = "VISÍVEL (primeira vez - para escanear QR Code)"
            else:
                # Já está logado - pode usar headless
                self.headless = True
                modo = "INVISÍVEL (já logado - modo headless)"
            
            logger.info(f"Iniciando navegador em modo: {modo}")
            
            if limpar_sessao and os.path.exists(session_dir):
                logger.info("Limpando sessão anterior...")
                try:
                    shutil.rmtree(session_dir)
                    logger.info("Sessão anterior removida")
                    self.headless = False  # Força visível após limpar
                except Exception as e:
                    logger.warning(f"Não foi possível remover a sessão: {e}")
            
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-software-rasterizer')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-notifications')
            chrome_options.add_argument('--disable-popup-blocking')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--disable-infobars')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
            chrome_options.add_argument('--remote-debugging-port=9222')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            chrome_options.add_argument(f'--user-data-dir={session_dir}')
            chrome_options.add_argument('--profile-directory=Default')
            
            # Adiciona headless se aplicável
            if self.headless:
                chrome_options.add_argument('--headless=new')
                logger.info("✅ Modo invisível ativado - navegador não será exibido")
            else:
                chrome_options.add_argument('--start-maximized')
                logger.info("👁️ Modo visível ativado - você verá o navegador")
            
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            prefs = {
                'profile.default_content_setting_values.notifications': 2,
                'profile.default_content_setting_values.media_stream_mic': 2,
                'profile.default_content_setting_values.media_stream_camera': 2,
            }
            chrome_options.add_experimental_option('prefs', prefs)
            
            logger.info("Configurando ChromeDriver...")
            service = Service(ChromeDriverManager().install())
            
            logger.info("Iniciando Chrome...")
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Maximiza a janela (se não for headless)
            if not self.headless:
                try:
                    self.driver.maximize_window()
                except:
                    pass
            
            logger.info("✅ Navegador iniciado com sucesso!")
            return True
            
        except WebDriverException as e:
            logger.error(f"Erro ao iniciar o navegador: {e}")
            
            # Se falhou em headless, tenta visível
            if self.headless and tentar_novamente:
                logger.warning("Falha no modo invisível. Tentando em modo visível...")
                return self.iniciar_navegador(limpar_sessao=False, tentar_novamente=False, forcar_visivel=True)
            
            # Se falhou visível, tenta limpar sessão
            if tentar_novamente and not limpar_sessao:
                logger.error("Tentando novamente com sessão limpa...")
                return self.iniciar_navegador(limpar_sessao=True, tentar_novamente=False)
            
            logger.error("Falha ao iniciar navegador")
            return False
            
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            return False
    
    def abrir_whatsapp_web(self):
        """Abre o WhatsApp Web e aguarda login"""
        try:
            logger.info("Acessando WhatsApp Web...")
            self.driver.get("https://web.whatsapp.com")
            
            if not self.headless:
                logger.info("👁️ Aguardando login (escaneie o QR Code se aparecer)...")
            else:
                logger.info("✅ Carregando sessão salva...")
            
            wait = WebDriverWait(self.driver, 60)
            wait.until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
            )
            
            if not self.headless:
                logger.info("✅ Login realizado com sucesso! Sessão salva para próximas execuções.")
            else:
                logger.info("✅ Sessão restaurada com sucesso!")
            
            time.sleep(3)
            return True
            
        except TimeoutException:
            logger.error("Timeout ao aguardar login")
            return False
        except Exception as e:
            logger.error(f"Erro ao abrir WhatsApp Web: {e}")
            return False
    
    def pode_enviar_mensagem(self, numero):
        """Verifica se pode enviar mensagem (limites de segurança)"""
        agora = time.time()
        
        # Limpa mensagens antigas da contagem por hora
        self.mensagens_enviadas_hora = [t for t in self.mensagens_enviadas_hora if agora - t < 3600]
        
        # Verifica limite por hora
        if len(self.mensagens_enviadas_hora) >= self.MAX_MENSAGENS_POR_HORA:
            tempo_espera = 3600 - (agora - self.mensagens_enviadas_hora[0])
            logger.warning(f"Limite de {self.MAX_MENSAGENS_POR_HORA} mensagens/hora atingido. Aguarde {tempo_espera:.0f}s")
            return False, tempo_espera
        
        # Verifica intervalo mínimo para o mesmo número
        if numero in self.ultimos_envios:
            tempo_desde_ultimo = agora - self.ultimos_envios[numero]
            if tempo_desde_ultimo < self.INTERVALO_MINIMO_MESMA_CONVERSA:
                tempo_espera = self.INTERVALO_MINIMO_MESMA_CONVERSA - tempo_desde_ultimo
                logger.info(f"Aguardando intervalo mínimo para {numero}: {tempo_espera:.0f}s")
                return False, tempo_espera
        
        return True, 0
    
    def enviar_mensagem(self, numero, mensagem):
        """Envia uma mensagem com todas as proteções"""
        try:
            with self.lock:
                pode_enviar, tempo_espera = self.pode_enviar_mensagem(numero)
                
                if not pode_enviar:
                    if tempo_espera > 0:
                        logger.info(f"Aguardando {tempo_espera:.0f}s antes de enviar...")
                        time.sleep(tempo_espera)
            
            numero_limpo = ''.join(filter(str.isdigit, numero))
            
            if len(numero_limpo) < 10:
                logger.error(f"Número inválido: {numero}")
                return False
            
            logger.info(f"Enviando mensagem para {numero_limpo}...")
            
            mensagem_codificada = quote(mensagem)
            url = f"https://web.whatsapp.com/send?phone={numero_limpo}&text={mensagem_codificada}"
            
            self.driver.get(url)
            
            wait = WebDriverWait(self.driver, self.wait_timeout)
            
            try:
                botao_enviar = wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//button[@aria-label="Enviar"]')
                    )
                )
                time.sleep(2)  # Pausa extra para segurança
                botao_enviar.click()
                
                logger.info(f"✅ Mensagem enviada para {numero_limpo}!")
                
                # Registra o envio
                with self.lock:
                    self.mensagens_enviadas_hora.append(time.time())
                    self.ultimos_envios[numero] = time.time()
                
                # Pausa obrigatória entre mensagens
                time.sleep(self.INTERVALO_ENTRE_MENSAGENS)
                return True
                
            except TimeoutException:
                try:
                    botao_enviar = wait.until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//span[@data-icon="send"]')
                        )
                    )
                    botao_enviar.click()
                    logger.info(f"✅ Mensagem enviada para {numero_limpo}!")
                    
                    with self.lock:
                        self.mensagens_enviadas_hora.append(time.time())
                        self.ultimos_envios[numero] = time.time()
                    
                    time.sleep(self.INTERVALO_ENTRE_MENSAGENS)
                    return True
                except:
                    logger.error("Não foi possível encontrar o botão de enviar")
                    return False
            
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
            return False
    
    def fechar(self):
        """Fecha o navegador de forma segura"""
        try:
            if self.driver:
                logger.info("Fechando o navegador...")
                self.driver.quit()
                logger.info("Navegador fechado!")
        except Exception as e:
            logger.error(f"Erro ao fechar navegador: {e}")


# Instância global do serviço
_whatsapp_service = None


def obter_servico_whatsapp():
    """Obtém a instância única do serviço WhatsApp"""
    global _whatsapp_service
    if _whatsapp_service is None:
        _whatsapp_service = WhatsAppService()
    return _whatsapp_service


def enviar_lembrete_whatsapp(agendamento):
    """
    Envia lembrete de agendamento via WhatsApp (24h antes)
    
    NOTA: Só deve ser chamado para agendamentos que faltam 23-24h
    """
    try:
        servico = obter_servico_whatsapp()
        
        # Verifica se o navegador está iniciado
        if servico.driver is None:
            logger.info("Iniciando navegador para envio de lembrete...")
            if not servico.iniciar_navegador():
                logger.error("Falha ao iniciar navegador")
                return False
            
            if not servico.abrir_whatsapp_web():
                logger.error("Falha ao abrir WhatsApp Web")
                return False
        
        # Cria mensagem personalizada
        mensagem = servico.criar_mensagem_confirmacao(agendamento)
        
        # Envia mensagem
        numero = agendamento.telefone
        if not numero.startswith('55'):
            numero = '55' + numero
        
        sucesso = servico.enviar_mensagem(numero, mensagem)
        
        if sucesso:
            logger.info(f"✅ Lembrete enviado para {agendamento.nome_cliente}")
        else:
            logger.error(f"❌ Falha ao enviar lembrete para {agendamento.nome_cliente}")
        
        return sucesso
        
    except Exception as e:
        logger.error(f"Erro ao enviar lembrete: {e}")
        return False


def enviar_confirmacao_agendamento(agendamento):
    """
    Envia confirmação/lembrete se o agendamento está a 24h ou menos
    Se for mais de 24h, não envia (será enviado pelo scheduler)
    
    IMPORTANTE: Envia de forma ASSÍNCRONA para não bloquear a resposta ao cliente
    """
    from datetime import datetime, timedelta
    
    try:
        # Calcula tempo até o agendamento
        agora = datetime.now()
        tempo_ate_agendamento = agendamento.data_hora - agora
        horas_ate_agendamento = tempo_ate_agendamento.total_seconds() / 3600
        
        # Se faltar mais de 24 horas, não envia agora (scheduler enviará depois)
        if horas_ate_agendamento > 24:
            logger.info(f"Agendamento de {agendamento.nome_cliente} está a {horas_ate_agendamento:.1f}h. Lembrete será enviado automaticamente 24h antes.")
            return True
        
        # Se faltar 24h ou menos, envia em segundo plano (não bloqueia a resposta)
        logger.info(f"Agendamento de {agendamento.nome_cliente} está a {horas_ate_agendamento:.1f}h. Agendando envio assíncrono...")
        
        def enviar_em_background():
            """Envia mensagem em thread separada"""
            try:
                enviar_lembrete_whatsapp(agendamento)
            except Exception as e:
                logger.error(f"Erro no envio assíncrono: {e}")
        
        # Inicia thread para envio em segundo plano
        thread = threading.Thread(target=enviar_em_background, daemon=True)
        thread.start()
        
        # Retorna imediatamente sem esperar o envio
        logger.info("Envio agendado com sucesso - retornando ao cliente")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao verificar tempo do agendamento: {e}")
        return False

"""
Script de Automação do WhatsApp Web
====================================
Este script utiliza Selenium para automatizar o envio de mensagens pelo WhatsApp Web.

Requisitos:
- Chrome/Chromium instalado
- ChromeDriver compatível com a versão do Chrome
- Conexão com internet

Uso:
    python test_whatsapp_automation.py
"""

import time
import logging
import os
import shutil
from datetime import datetime
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


class WhatsAppAutomation:
    """Classe para automação de envio de mensagens pelo WhatsApp Web"""
    
    def __init__(self, headless=False):
        """
        Inicializa o navegador Chrome com configurações otimizadas
        
        Args:
            headless (bool): Se True, executa o navegador em modo headless (sem interface)
        """
        self.driver = None
        self.headless = headless
        self.wait_timeout = 30
        
    def iniciar_navegador(self, limpar_sessao=False):
        """
        Inicia o navegador Chrome com as configurações necessárias
        
        Args:
            limpar_sessao (bool): Se True, limpa a sessão anterior antes de iniciar
        """
        try:
            logger.info("Iniciando o navegador Chrome...")
            
            # Define o diretório da sessão
            session_dir = os.path.abspath('whatsapp_session')
            
            # Limpa a sessão se solicitado
            if limpar_sessao and os.path.exists(session_dir):
                logger.info("Limpando sessão anterior...")
                try:
                    shutil.rmtree(session_dir)
                    logger.info("Sessão anterior removida")
                except Exception as e:
                    logger.warning(f"Não foi possível remover a sessão: {e}")
            
            chrome_options = Options()
            
            # Configurações essenciais para evitar crashes
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-software-rasterizer')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-notifications')
            chrome_options.add_argument('--disable-popup-blocking')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--start-maximized')
            
            # Configurações adicionais para estabilidade
            chrome_options.add_argument('--disable-infobars')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
            chrome_options.add_argument('--remote-debugging-port=9222')
            
            # User agent para evitar detecção de bot
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Mantém a sessão do WhatsApp (não precisa escanear QR code toda vez)
            chrome_options.add_argument(f'--user-data-dir={session_dir}')
            chrome_options.add_argument('--profile-directory=Default')
            
            if self.headless:
                chrome_options.add_argument('--headless=new')
            
            # Remove mensagens de log desnecessárias
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Preferences adicionais
            prefs = {
                'profile.default_content_setting_values.notifications': 2,
                'profile.default_content_setting_values.media_stream_mic': 2,
                'profile.default_content_setting_values.media_stream_camera': 2,
            }
            chrome_options.add_experimental_option('prefs', prefs)
            
            # Usa webdriver-manager para baixar automaticamente o ChromeDriver correto
            logger.info("Configurando ChromeDriver...")
            service = Service(ChromeDriverManager().install())
            
            # Inicializa o driver
            logger.info("Iniciando Chrome...")
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Maximiza a janela (se não for headless)
            if not self.headless:
                try:
                    self.driver.maximize_window()
                except:
                    pass
            
            logger.info("Navegador iniciado com sucesso!")
            return True
            
        except WebDriverException as e:
            logger.error(f"Erro ao iniciar o navegador: {e}")
            logger.error("Tentando novamente com sessão limpa...")
            
            # Tenta novamente limpando a sessão
            if not limpar_sessao:
                return self.iniciar_navegador(limpar_sessao=True)
            
            logger.error("Falha ao iniciar mesmo com sessão limpa")
            logger.error("Verifique se o Google Chrome está instalado corretamente")
            return False
            
        except Exception as e:
            logger.error(f"Erro inesperado ao iniciar navegador: {e}")
            return False
    
    def abrir_whatsapp_web(self):
        """Abre o WhatsApp Web e aguarda o login do usuário"""
        try:
            logger.info("Acessando WhatsApp Web...")
            self.driver.get("https://web.whatsapp.com")
            
            logger.info("Aguardando login do usuário...")
            logger.info("Por favor, escaneie o QR Code com seu celular (se necessário)")
            
            # Aguarda até que a página principal do WhatsApp carregue
            # Verifica a presença da barra de pesquisa como indicador de login bem-sucedido
            wait = WebDriverWait(self.driver, 60)  # 60 segundos para fazer login
            wait.until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
            )
            
            logger.info("Login realizado com sucesso!")
            time.sleep(2)  # Aguarda estabilização da página
            return True
            
        except TimeoutException:
            logger.error("Timeout ao aguardar login. O QR Code não foi escaneado a tempo.")
            return False
        except Exception as e:
            logger.error(f"Erro ao abrir WhatsApp Web: {e}")
            return False
    
    def enviar_mensagem(self, numero, mensagem):
        """
        Envia uma mensagem para um número específico
        
        Args:
            numero (str): Número de telefone no formato internacional (ex: 5511999999999)
            mensagem (str): Texto da mensagem a ser enviada
            
        Returns:
            bool: True se a mensagem foi enviada com sucesso, False caso contrário
        """
        try:
            # Remove caracteres não numéricos do número
            numero_limpo = ''.join(filter(str.isdigit, numero))
            
            if len(numero_limpo) < 10:
                logger.error(f"Número inválido: {numero}")
                return False
            
            logger.info(f"Enviando mensagem para {numero_limpo}...")
            
            # Codifica a mensagem para URL
            mensagem_codificada = quote(mensagem)
            
            # Monta a URL do WhatsApp com o número e mensagem
            url = f"https://web.whatsapp.com/send?phone={numero_limpo}&text={mensagem_codificada}"
            
            # Navega para a URL
            self.driver.get(url)
            
            # Aguarda a página carregar
            wait = WebDriverWait(self.driver, self.wait_timeout)
            
            # Aguarda o botão de enviar aparecer
            try:
                botao_enviar = wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//button[@aria-label="Enviar"]')
                    )
                )
                time.sleep(1)  # Pequena pausa para estabilidade
                
                # Clica no botão de enviar
                botao_enviar.click()
                
                logger.info(f"Mensagem enviada com sucesso para {numero_limpo}!")
                time.sleep(2)  # Aguarda o envio ser processado
                return True
                
            except TimeoutException:
                # Tenta XPath alternativo
                try:
                    botao_enviar = wait.until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//span[@data-icon="send"]')
                        )
                    )
                    botao_enviar.click()
                    logger.info(f"Mensagem enviada com sucesso para {numero_limpo}!")
                    time.sleep(2)
                    return True
                except:
                    logger.error("Não foi possível encontrar o botão de enviar")
                    return False
            
        except TimeoutException:
            logger.error(f"Timeout ao tentar enviar mensagem para {numero}")
            return False
        except NoSuchElementException as e:
            logger.error(f"Elemento não encontrado: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
            return False
    
    def enviar_mensagens_lote(self, contatos):
        """
        Envia mensagens para múltiplos contatos
        
        Args:
            contatos (list): Lista de dicionários com 'numero' e 'mensagem'
                Exemplo: [{'numero': '5511999999999', 'mensagem': 'Olá!'}]
        
        Returns:
            dict: Estatísticas de envio (sucesso, falha)
        """
        resultados = {
            'sucesso': 0,
            'falha': 0,
            'total': len(contatos)
        }
        
        logger.info(f"Iniciando envio em lote para {len(contatos)} contatos...")
        
        for i, contato in enumerate(contatos, 1):
            numero = contato.get('numero')
            mensagem = contato.get('mensagem')
            
            if not numero or not mensagem:
                logger.warning(f"Contato {i} inválido (faltando número ou mensagem)")
                resultados['falha'] += 1
                continue
            
            logger.info(f"Processando contato {i}/{len(contatos)}")
            
            if self.enviar_mensagem(numero, mensagem):
                resultados['sucesso'] += 1
            else:
                resultados['falha'] += 1
            
            # Pausa entre envios para evitar bloqueio
            if i < len(contatos):
                time.sleep(3)
        
        logger.info(f"Envio em lote concluído: {resultados['sucesso']} sucesso, {resultados['falha']} falha")
        return resultados
    
    def fechar(self):
        """Fecha o navegador e limpa recursos"""
        try:
            if self.driver:
                logger.info("Fechando o navegador...")
                self.driver.quit()
                logger.info("Navegador fechado com sucesso!")
        except Exception as e:
            logger.error(f"Erro ao fechar navegador: {e}")


def teste_envio_simples():
    """Função de teste para envio simples de mensagem"""
    whatsapp = WhatsAppAutomation(headless=False)
    
    try:
        print("\n" + "="*60)
        print("INICIANDO NAVEGADOR...")
        print("="*60)
        print("\nCaso apareça algum erro, será tentado automaticamente")
        print("com a limpeza da sessão anterior.\n")
        
        # Inicia o navegador
        if not whatsapp.iniciar_navegador():
            logger.error("Falha ao iniciar navegador. Encerrando...")
            input("\nPressione Enter para sair...")
            return
        
        # Abre o WhatsApp Web
        if not whatsapp.abrir_whatsapp_web():
            logger.error("Falha ao acessar WhatsApp Web. Encerrando...")
            return
        
        # Solicita informações do usuário
        print("\n" + "="*60)
        print("TESTE DE ENVIO DE MENSAGEM - WHATSAPP WEB")
        print("="*60)
        
        numero = input("\nDigite o número com DDD (ex: 11999999999): ")
        
        # Adiciona código do país se não tiver
        if not numero.startswith('55'):
            numero = '55' + numero
        
        print("\nDigite a mensagem (pressione Enter duas vezes para finalizar):")
        linhas = []
        while True:
            linha = input()
            if linha:
                linhas.append(linha)
            else:
                break
        
        mensagem = '\n'.join(linhas) if linhas else "Mensagem de teste"
        
        # Envia a mensagem
        print("\n" + "-"*60)
        if whatsapp.enviar_mensagem(numero, mensagem):
            print("✓ Mensagem enviada com sucesso!")
        else:
            print("✗ Falha ao enviar mensagem.")
        print("-"*60)
        
        # Aguarda antes de fechar
        input("\nPressione Enter para fechar o navegador...")
        
    except KeyboardInterrupt:
        logger.info("\nOperação cancelada pelo usuário")
    except Exception as e:
        logger.error(f"Erro no teste: {e}")
    finally:
        whatsapp.fechar()


def teste_envio_lote():
    """Função de teste para envio em lote"""
    whatsapp = WhatsAppAutomation(headless=False)
    
    try:
        print("\n" + "="*60)
        print("INICIANDO NAVEGADOR...")
        print("="*60)
        print("\nCaso apareça algum erro, será tentado automaticamente")
        print("com a limpeza da sessão anterior.\n")
        
        # Inicia o navegador
        if not whatsapp.iniciar_navegador():
            logger.error("Falha ao iniciar navegador. Encerrando...")
            input("\nPressione Enter para sair...")
            return
        
        # Abre o WhatsApp Web
        if not whatsapp.abrir_whatsapp_web():
            logger.error("Falha ao acessar WhatsApp Web. Encerrando...")
            return
        
        # Exemplo de envio em lote
        contatos = [
            {
                'numero': '5511999999999',  # Substitua pelo número de teste
                'mensagem': 'Olá! Esta é uma mensagem de teste 1.'
            },
            {
                'numero': '5511988888888',  # Substitua pelo número de teste
                'mensagem': 'Olá! Esta é uma mensagem de teste 2.'
            }
        ]
        
        print("\n" + "="*60)
        print("TESTE DE ENVIO EM LOTE - WHATSAPP WEB")
        print("="*60)
        print(f"\nSerão enviadas {len(contatos)} mensagens")
        print("ATENÇÃO: Modifique os números no código antes de executar!")
        
        resposta = input("\nDeseja continuar? (s/n): ")
        
        if resposta.lower() == 's':
            resultados = whatsapp.enviar_mensagens_lote(contatos)
            
            print("\n" + "-"*60)
            print("RESULTADOS:")
            print(f"Total: {resultados['total']}")
            print(f"Sucesso: {resultados['sucesso']}")
            print(f"Falha: {resultados['falha']}")
            print("-"*60)
        
        # Aguarda antes de fechar
        input("\nPressione Enter para fechar o navegador...")
        
    except KeyboardInterrupt:
        logger.info("\nOperação cancelada pelo usuário")
    except Exception as e:
        logger.error(f"Erro no teste: {e}")
    finally:
        whatsapp.fechar()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("SCRIPT DE AUTOMAÇÃO DO WHATSAPP WEB")
    print("="*60)
    print("\nEscolha o tipo de teste:")
    print("1 - Envio simples (uma mensagem)")
    print("2 - Envio em lote (múltiplas mensagens)")
    print("0 - Sair")
    
    escolha = input("\nOpção: ")
    
    if escolha == '1':
        teste_envio_simples()
    elif escolha == '2':
        teste_envio_lote()
    elif escolha == '0':
        print("Encerrando...")
    else:
        print("Opção inválida!")

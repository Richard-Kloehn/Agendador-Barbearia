"""
Script de teste para a nova conta Whapi com validação correta de números
=========================================================================

Implementa as regras do suporte Whapi:
- Formato internacional sem o "+"
- Para DDDs 11-19, 21, 22, 24, 27, 28: OBRIGATÓRIO adicionar "9" após o DDD
- Para outros DDDs: REMOVER o "9" se presente
- Validação via endpoint /contacts antes de enviar
"""

import requests
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class WhapiTester:
    """Testador da nova conta Whapi com formatação correta"""
    
    def __init__(self):
        self.api_url = os.getenv('WHAPI_API_URL', 'https://gate.whapi.cloud').rstrip('/')
        self.api_token = os.getenv('WHAPI_API_TOKEN', '')
        
        if not self.api_token:
            raise ValueError("❌ WHAPI_API_TOKEN não configurado nas variáveis de ambiente")
        
        print(f"✅ API URL: {self.api_url}")
        print(f"✅ Token: {self.api_token[:10]}...{self.api_token[-4:]}")
    
    def formatar_numero_brasileiro(self, numero: str) -> str:
        """
        Formata número brasileiro seguindo as regras do Whapi
        
        Regras:
        - DDDs 11-19, 21, 22, 24, 27, 28: adicionar 9 após DDD
        - Outros DDDs: remover 9 se presente
        
        Args:
            numero: Número no formato (XX) XXXXX-XXXX ou similar
            
        Returns:
            str: Número formatado (ex: 5547991557386)
        """
        # Remove caracteres não numéricos
        numero_limpo = ''.join(filter(str.isdigit, numero))
        
        # Remove 55 se tiver
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
                print(f"   ➕ Adicionado 9 para DDD {ddd}: {numero_limpo} -> {numero_final}")
            else:
                # Já tem 9 dígitos e começa com 9, manter
                numero_final = numero_limpo
        else:
            # Outros DDDs: REMOVER o 9 se presente
            if resto.startswith('9') and len(resto) == 9:
                # Remover o 9
                numero_final = ddd + resto[1:]
                print(f"   ➖ Removido 9 para DDD {ddd}: {numero_limpo} -> {numero_final}")
            else:
                # Já está sem o 9
                numero_final = numero_limpo
        
        # Adicionar código do Brasil
        return '55' + numero_final
    
    def validar_numero_whatsapp(self, numero: str) -> dict:
        """
        Valida número usando o endpoint /contacts da Whapi
        
        Args:
            numero: Número já formatado (ex: 5547991557386)
            
        Returns:
            dict: {'valido': bool, 'wa_id': str, 'chat_id': str}
        """
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        url = f"{self.api_url}/contacts"
        payload = {
            "force_check": False,
            "contacts": [numero]
        }
        
        print(f"\n🔍 Validando número: {numero}")
        print(f"   URL: {url}")
        print(f"   Payload: {payload}")
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            print(f"   Status: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                contacts = data.get('contacts', [])
                
                if contacts and len(contacts) > 0:
                    resultado = contacts[0]
                    status = resultado.get('status')
                    wa_id = resultado.get('wa_id')
                    
                    if status == 'valid' and wa_id:
                        # Extrair o Chat ID correto
                        chat_id = wa_id  # Já vem no formato 559281723246@s.whatsapp.net
                        numero_correto = wa_id.replace('@s.whatsapp.net', '')
                        
                        print(f"   ✅ VÁLIDO!")
                        print(f"   📱 wa_id: {wa_id}")
                        print(f"   📞 Número: {numero_correto}")
                        
                        return {
                            'valido': True,
                            'wa_id': wa_id,
                            'numero': numero_correto,
                            'chat_id': chat_id
                        }
                    else:
                        print(f"   ❌ INVÁLIDO - Status: {status}")
                        return {
                            'valido': False,
                            'wa_id': None,
                            'numero': numero,
                            'chat_id': None
                        }
            
            print(f"   ⚠️ Erro: HTTP {response.status_code}")
            return {
                'valido': None,
                'wa_id': None,
                'numero': numero,
                'chat_id': None
            }
            
        except Exception as e:
            print(f"   ❌ Exceção: {e}")
            return {
                'valido': None,
                'wa_id': None,
                'numero': numero,
                'chat_id': None
            }
    
    def enviar_mensagem_teste(self, numero: str, mensagem: str) -> bool:
        """
        Envia mensagem de teste
        
        Args:
            numero: Número do destinatário (será formatado e validado)
            mensagem: Texto da mensagem
            
        Returns:
            bool: True se enviado com sucesso
        """
        print(f"\n{'='*70}")
        print(f"📤 TESTE DE ENVIO DE MENSAGEM")
        print(f"{'='*70}")
        
        # Passo 1: Formatar número
        print(f"\n1️⃣ Formatando número: {numero}")
        try:
            numero_formatado = self.formatar_numero_brasileiro(numero)
            print(f"   ✅ Formatado: {numero_formatado}")
        except Exception as e:
            print(f"   ❌ Erro na formatação: {e}")
            return False
        
        # Passo 2: Validar número
        print(f"\n2️⃣ Validando número com Whapi...")
        validacao = self.validar_numero_whatsapp(numero_formatado)
        
        if validacao['valido'] == False:
            print(f"   ❌ Número não tem WhatsApp ativo!")
            return False
        
        if not validacao['wa_id']:
            print(f"   ⚠️ Validação falhou, usando número formatado básico")
            numero_envio = numero_formatado
        else:
            # Usar apenas o número (sem @s.whatsapp.net)
            numero_envio = validacao['numero']
        
        # Passo 3: Enviar mensagem
        print(f"\n3️⃣ Enviando mensagem...")
        print(f"   Para: {numero_envio}")
        print(f"   Mensagem: {mensagem[:50]}...")
        
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        payload = {
            'to': numero_envio,
            'body': mensagem
        }
        
        url = f'{self.api_url}/messages/text'
        
        print(f"   URL: {url}")
        print(f"   Payload: {payload}")
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            
            print(f"   Status: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
            if response.status_code in [200, 201]:
                result = response.json()
                
                if 'error' in result or 'errors' in result:
                    print(f"   ❌ Erro na resposta: {result}")
                    return False
                
                print(f"   ✅ MENSAGEM ENVIADA COM SUCESSO!")
                print(f"   📨 ID: {result.get('id', result.get('message_id', 'N/A'))}")
                return True
            else:
                try:
                    error_data = response.json()
                    print(f"   ❌ Erro: {error_data}")
                except:
                    print(f"   ❌ Erro HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Exceção: {e}")
            return False


def main():
    """Função principal de teste"""
    print("\n" + "="*70)
    print("🧪 TESTE DA NOVA CONTA WHAPI")
    print("="*70)
    
    try:
        tester = WhapiTester()
    except ValueError as e:
        print(f"\n{e}")
        print("\n💡 Configure WHAPI_API_TOKEN no arquivo .env")
        return
    
    # Números de teste (substitua pelos seus números reais)
    numeros_teste = [
        # Formato (XX) 9XXXX-XXXX ou (XX) XXXXX-XXXX
        "(47) 99155-7386",  # DDD 47 (Santa Catarina) - remover 9
    ]
    
    mensagem_teste = """🧪 Mensagem de teste - Whapi.Cloud

Esta é uma mensagem automática de teste do sistema de agendamentos.

✅ Se você recebeu esta mensagem, o sistema está funcionando corretamente!

Navalha's Barber Club 💈"""
    
    print("\n📋 NÚMEROS PARA TESTE:")
    for i, num in enumerate(numeros_teste, 1):
        print(f"   {i}. {num}")
    
    print("\n⚠️ ATENÇÃO: A mensagem será enviada para TODOS os números acima!")
    print("Pressione Enter para continuar ou Ctrl+C para cancelar...")
    input()
    
    # Testar cada número
    resultados = []
    for numero in numeros_teste:
        sucesso = tester.enviar_mensagem_teste(numero, mensagem_teste)
        resultados.append((numero, sucesso))
        print("\n" + "-"*70 + "\n")
    
    # Resumo
    print("\n" + "="*70)
    print("📊 RESUMO DOS TESTES")
    print("="*70)
    
    for numero, sucesso in resultados:
        status = "✅ SUCESSO" if sucesso else "❌ FALHA"
        print(f"{status} - {numero}")
    
    sucessos = sum(1 for _, s in resultados if s)
    print(f"\n📈 Total: {sucessos}/{len(resultados)} mensagens enviadas com sucesso")
    
    if sucessos == len(resultados):
        print("\n🎉 Todos os testes passaram! A integração está funcionando perfeitamente!")
    elif sucessos > 0:
        print("\n⚠️ Alguns testes falharam. Verifique os logs acima.")
    else:
        print("\n❌ Todos os testes falharam. Verifique a configuração da API.")


if __name__ == "__main__":
    main()

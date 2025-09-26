"""
Serviço para integração com WhatsApp Business API
"""
import requests
import logging
from .config import Config

logger = logging.getLogger(__name__)

class WhatsAppService:
    """Classe para gerenciar operações com WhatsApp Business API"""
    
    def __init__(self):
        self.token = Config.WHATSAPP_TOKEN
        self.phone_number_id = Config.PHONE_NUMBER_ID
        self.base_url = f"https://graph.facebook.com/v17.0/{self.phone_number_id}"
    
    def enviar_mensagem(self, to, message):
        """
        Envia mensagem via WhatsApp Business API
        
        Args:
            to (str): Número do destinatário
            message (str): Mensagem a ser enviada
            
        Returns:
            bool: True se enviada com sucesso
        """
        try:
            url = f"{self.base_url}/messages"
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            data = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {"body": message}
            }
            
            logger.info(f"Enviando mensagem para {to}: '{message[:50]}...'")
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                logger.info(f"✅ Mensagem enviada com sucesso para {to}")
                return True
            elif response.status_code == 401:
                logger.error("❌ TOKEN EXPIRADO! Gere um novo token no Meta for Developers")
            else:
                logger.error(f"❌ Erro ao enviar mensagem: {response.status_code} - {response.text}")
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem WhatsApp: {e}")
            return False
    
    def enviar_mensagem_formatada(self, to, titulo, conteudo, rodape=None):
        """
        Envia mensagem formatada com título e conteúdo
        
        Args:
            to (str): Número do destinatário
            titulo (str): Título da mensagem
            conteudo (str): Conteúdo principal
            rodape (str): Rodapé opcional
            
        Returns:
            bool: True se enviada com sucesso
        """
        message = f"*{titulo}*\n\n{conteudo}"
        
        if rodape:
            message += f"\n\n_{rodape}_"
        
        return self.enviar_mensagem(to, message)
    
    def enviar_lista_gastos(self, to, gastos, titulo="📋 Lista de Gastos"):
        """
        Envia lista formatada de gastos
        
        Args:
            to (str): Número do destinatário
            gastos (list): Lista de gastos
            titulo (str): Título da lista
            
        Returns:
            bool: True se enviada com sucesso
        """
        if not gastos:
            return self.enviar_mensagem(to, "✅ Nenhum gasto encontrado!")
        
        conteudo = ""
        total = 0
        
        for gasto in gastos:
            descricao = gasto.get('Descrição', 'N/A')
            valor_str = str(gasto.get('Valor', '0'))
            data = gasto.get('Data', 'N/A')
            
            conteudo += f"• {descricao} - R$ {valor_str}\n"
            
            # Calcular total
            try:
                valor = float(valor_str.replace(',', '.'))
                total += valor
            except ValueError:
                pass
        
        conteudo += f"\n💰 *Total: R$ {total:.2f}*"
        
        return self.enviar_mensagem_formatada(to, titulo, conteudo)
    
    def enviar_saldo_mensal(self, to, total, mes_ano):
        """
        Envia saldo mensal formatado
        
        Args:
            to (str): Número do destinatário
            total (float): Total gasto
            mes_ano (str): Mês/ano no formato MM/YYYY
            
        Returns:
            bool: True se enviada com sucesso
        """
        titulo = f"💰 Saldo do mês {mes_ano}"
        conteudo = f"Total gasto: R$ {total:.2f}"
        
        # Adicionar contexto baseado no valor
        if total == 0:
            rodape = "Parabéns! Nenhum gasto registrado este mês! 🎉"
        elif total < 500:
            rodape = "Gastos controlados! Continue assim! 👍"
        elif total < 1000:
            rodape = "Atenção aos gastos! 📊"
        else:
            rodape = "Gastos elevados! Considere revisar seu orçamento. 📈"
        
        return self.enviar_mensagem_formatada(to, titulo, conteudo, rodape)
    
    def enviar_ajuda(self, to):
        """
        Envia mensagem de ajuda com todos os comandos
        
        Args:
            to (str): Número do destinatário
            
        Returns:
            bool: True se enviada com sucesso
        """
        titulo = "🤖 Comandos Disponíveis"
        
        conteudo = """💰 *Para registrar gastos:*
• mercado 50
• uber 25.50
• R$ 100 farmácia

📊 *Consultas:*
• saldo - Total do mês
• hoje - Gastos de hoje
• exportar - Link da planilha

🗑️ *Outros:*
• deletar - Remove último gasto
• ajuda - Esta mensagem"""
        
        rodape = "Digite qualquer gasto para começar!"
        
        return self.enviar_mensagem_formatada(to, titulo, conteudo, rodape)
    
    def enviar_erro_valor(self, to):
        """
        Envia mensagem de erro quando não consegue identificar o valor
        
        Args:
            to (str): Número do destinatário
            
        Returns:
            bool: True se enviada com sucesso
        """
        titulo = "❌ Valor não identificado"
        
        conteudo = """*Exemplos válidos:*
• mercado 50
• R$ 25.50 uber
• cinquenta reais farmácia
• 100 gasolina"""
        
        rodape = "Digite 'ajuda' para ver todos os comandos"
        
        return self.enviar_mensagem_formatada(to, titulo, conteudo, rodape)
"""
Serviço para integração com Telegram Bot API
"""
import requests
import logging
from .config import Config

logger = logging.getLogger(__name__)

class TelegramService:
    """Classe para gerenciar operações com Telegram Bot API"""
    
    def __init__(self):
        self.token = Config.TELEGRAM_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.token}"
    
    def enviar_mensagem(self, chat_id, message):
        """
        Envia mensagem via Telegram Bot API
        
        Args:
            chat_id (str): ID do chat
            message (str): Mensagem a ser enviada
            
        Returns:
            bool: True se enviada com sucesso
        """
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            logger.info(f"Enviando mensagem para {chat_id}: '{message[:50]}...'")
            
            response = requests.post(url, json=data)
            
            if response.status_code == 200:
                logger.info(f"✅ Mensagem enviada com sucesso para {chat_id}")
                return True
            else:
                logger.error(f"❌ Erro ao enviar mensagem: {response.status_code} - {response.text}")
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem Telegram: {e}")
            return False
    
    def enviar_mensagem_formatada(self, chat_id, titulo, conteudo, rodape=None):
        """
        Envia mensagem formatada com título e conteúdo
        
        Args:
            chat_id (str): ID do chat
            titulo (str): Título da mensagem
            conteudo (str): Conteúdo principal
            rodape (str): Rodapé opcional
            
        Returns:
            bool: True se enviada com sucesso
        """
        message = f"*{titulo}*\n\n{conteudo}"
        
        if rodape:
            message += f"\n\n_{rodape}_"
        
        return self.enviar_mensagem(chat_id, message)
    
    def enviar_lista_gastos(self, chat_id, gastos, titulo="📋 Lista de Gastos"):
        """
        Envia lista formatada de gastos
        
        Args:
            chat_id (str): ID do chat
            gastos (list): Lista de gastos
            titulo (str): Título da lista
            
        Returns:
            bool: True se enviada com sucesso
        """
        if not gastos:
            return self.enviar_mensagem(chat_id, "✅ Nenhum gasto encontrado!")
        
        conteudo = ""
        total = 0
        
        for gasto in gastos:
            descricao = gasto.get('Descrição', 'N/A')
            valor_str = str(gasto.get('Valor', '0'))
            
            conteudo += f"• {descricao} - R$ {valor_str}\n"
            
            # Calcular total
            try:
                valor = float(valor_str.replace(',', '.'))
                total += valor
            except ValueError:
                pass
        
        conteudo += f"\n💰 *Total: R$ {total:.2f}*"
        
        return self.enviar_mensagem_formatada(chat_id, titulo, conteudo)
    
    def enviar_saldo_mensal(self, chat_id, total, mes_ano):
        """
        Envia saldo mensal formatado
        
        Args:
            chat_id (str): ID do chat
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
        
        return self.enviar_mensagem_formatada(chat_id, titulo, conteudo, rodape)
    
    def enviar_ajuda(self, chat_id):
        """
        Envia mensagem de ajuda com todos os comandos
        
        Args:
            chat_id (str): ID do chat
            
        Returns:
            bool: True se enviada com sucesso
        """
        titulo = "🤖 Comandos Disponíveis"
        
        conteudo = """💰 *Para registrar gastos:*
• mercado 50
• uber 25.50
• R$ 100 farmácia

📊 *Consultas:*
• /saldo - Total do mês
• /hoje - Gastos de hoje
• /exportar - Link da planilha

🗑️ *Outros:*
• /deletar - Remove último gasto
• /ajuda - Esta mensagem"""
        
        rodape = "Digite qualquer gasto para começar!"
        
        return self.enviar_mensagem_formatada(chat_id, titulo, conteudo, rodape)
    
    def enviar_erro_valor(self, chat_id):
        """
        Envia mensagem de erro quando não consegue identificar o valor
        
        Args:
            chat_id (str): ID do chat
            
        Returns:
            bool: True se enviada com sucesso
        """
        titulo = "❌ Valor não identificado"
        
        conteudo = """*Exemplos válidos:*
• mercado 50
• R$ 25.50 uber
• cinquenta reais farmácia
• 100 gasolina"""
        
        rodape = "Digite /ajuda para ver todos os comandos"
        
        return self.enviar_mensagem_formatada(chat_id, titulo, conteudo, rodape)
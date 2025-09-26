"""
Serviço para integração com Google Sheets
"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import logging
import json
import tempfile
import os
from .config import Config

logger = logging.getLogger(__name__)

class SheetsService:
    """Classe para gerenciar operações com Google Sheets"""
    
    def __init__(self):
        self.client = None
        self.sheet = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Inicializa conexão com Google Sheets"""
        try:
            # Tentar usar credenciais da variável de ambiente primeiro
            if Config.GOOGLE_CREDENTIALS:
                # Credenciais via variável de ambiente (para deploy)
                credentials_dict = json.loads(Config.GOOGLE_CREDENTIALS)
                creds = ServiceAccountCredentials.from_json_keyfile_dict(
                    credentials_dict, 
                    Config.GOOGLE_SHEETS_SCOPES
                )
            else:
                # Credenciais via arquivo (para desenvolvimento local)
                creds = ServiceAccountCredentials.from_json_keyfile_name(
                    Config.CREDENTIALS_FILE, 
                    Config.GOOGLE_SHEETS_SCOPES
                )
            
            self.client = gspread.authorize(creds)
            self.sheet = self.client.open_by_key(Config.SHEET_ID).sheet1
            
            # Configurar cabeçalho se necessário
            self._setup_headers()
            
            logger.info("Google Sheets conectado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao conectar Google Sheets: {e}")
            self.sheet = None
    
    def _setup_headers(self):
        """Configura cabeçalho da planilha"""
        try:
            headers = self.sheet.row_values(1)
            expected_headers = ["Data", "Descrição", "Valor", "Categoria"]
            
            if not headers or headers != expected_headers:
                self.sheet.clear()
                self.sheet.append_row(expected_headers)
                logger.info("Cabeçalho da planilha configurado")
                
        except Exception as e:
            logger.error(f"Erro ao configurar cabeçalho: {e}")
    
    def is_connected(self):
        """Verifica se a conexão está ativa"""
        return self.sheet is not None
    
    def adicionar_gasto(self, descricao, valor, categoria):
        """
        Adiciona um novo gasto à planilha
        
        Args:
            descricao (str): Descrição do gasto
            valor (float): Valor do gasto
            categoria (str): Categoria do gasto
            
        Returns:
            bool: True se adicionado com sucesso
        """
        if not self.is_connected():
            logger.error("Google Sheets não conectado")
            return False
        
        try:
            hoje = datetime.now().strftime("%d/%m/%Y")
            self.sheet.append_row([hoje, descricao, f"{valor:.2f}", categoria])
            logger.info(f"Gasto adicionado: {descricao} - R$ {valor:.2f} ({categoria})")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar gasto: {e}")
            return False
    
    def obter_todos_gastos(self):
        """
        Obtém todos os gastos da planilha
        
        Returns:
            list: Lista de gastos
        """
        if not self.is_connected():
            return []
        
        try:
            records = self.sheet.get_all_records()
            return records
        except Exception as e:
            logger.error(f"Erro ao obter gastos: {e}")
            return []
    
    def calcular_saldo_mes(self, mes=None, ano=None):
        """
        Calcula total gasto no mês
        
        Args:
            mes (int): Mês (padrão: atual)
            ano (int): Ano (padrão: atual)
            
        Returns:
            float: Total gasto no mês
        """
        if mes is None:
            mes = datetime.now().month
        if ano is None:
            ano = datetime.now().year
        
        gastos = self.obter_todos_gastos()
        mes_ano = f"{mes:02d}/{ano}"
        total = 0
        
        for gasto in gastos:
            data_gasto = str(gasto.get('Data', ''))
            if mes_ano in data_gasto:
                valor = str(gasto.get('Valor', '0')).replace(',', '.')
                try:
                    total += float(valor)
                except ValueError:
                    continue
        
        return total
    
    def obter_gastos_hoje(self):
        """
        Obtém gastos do dia atual
        
        Returns:
            tuple: (lista_gastos, total)
        """
        gastos = self.obter_todos_gastos()
        hoje = datetime.now().strftime("%d/%m/%Y")
        gastos_hoje = []
        total = 0
        
        for gasto in gastos:
            if str(gasto.get('Data', '')) == hoje:
                gastos_hoje.append(gasto)
                valor = str(gasto.get('Valor', '0')).replace(',', '.')
                try:
                    total += float(valor)
                except ValueError:
                    continue
        
        return gastos_hoje, total
    
    def deletar_ultimo_gasto(self):
        """
        Deleta o último gasto registrado
        
        Returns:
            bool: True se deletado com sucesso
        """
        if not self.is_connected():
            return False
        
        try:
            records = self.sheet.get_all_records()
            if records:
                # +1 porque a primeira linha é cabeçalho
                ultima_linha = len(records) + 1
                self.sheet.delete_rows(ultima_linha)
                logger.info("Último gasto deletado com sucesso")
                return True
        except Exception as e:
            logger.error(f"Erro ao deletar gasto: {e}")
        
        return False
    
    def obter_gastos_por_categoria(self):
        """
        Agrupa gastos por categoria
        
        Returns:
            dict: Gastos agrupados por categoria
        """
        gastos = self.obter_todos_gastos()
        gastos_por_categoria = {}
        
        for gasto in gastos:
            categoria = gasto.get('Categoria', 'outros')
            valor_str = str(gasto.get('Valor', '0')).replace(',', '.')
            
            try:
                valor = float(valor_str)
                if categoria in gastos_por_categoria:
                    gastos_por_categoria[categoria] += valor
                else:
                    gastos_por_categoria[categoria] = valor
            except ValueError:
                continue
        
        return gastos_por_categoria
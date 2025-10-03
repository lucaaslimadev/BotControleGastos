#!/usr/bin/env python3
"""
Bot Multi-usuário com Controle de Acesso
"""
import json
import requests
import threading
from bot_otimizado import BotOtimizado

class BotMultiUsuario(BotOtimizado):
    def __init__(self):
        super().__init__()
        self.usuarios_file = 'usuarios.json'
        self.carregar_usuarios()
    
    def carregar_usuarios(self):
        """Carrega lista de usuários autorizados"""
        try:
            with open(self.usuarios_file, 'r') as f:
                self.usuarios_data = json.load(f)
        except FileNotFoundError:
            self.usuarios_data = {
                "usuarios_autorizados": [],
                "configuracoes": {"permitir_novos_usuarios": False, "requer_aprovacao": True}
            }
    
    def salvar_usuarios(self):
        """Salva lista de usuários"""
        with open(self.usuarios_file, 'w') as f:
            json.dump(self.usuarios_data, f, indent=2)
    
    def usuario_autorizado(self, chat_id):
        """Verifica se usuário está autorizado"""
        return any(u["chat_id"] == chat_id and u["ativo"] 
                  for u in self.usuarios_data["usuarios_autorizados"])
    
    def usuario_admin(self, chat_id):
        """Verifica se usuário é admin"""
        return any(u["chat_id"] == chat_id and u.get("admin", False) 
                  for u in self.usuarios_data["usuarios_autorizados"])
    
    def adicionar_usuario(self, chat_id, nome, admin=False):
        """Adiciona novo usuário"""
        if not self.usuario_autorizado(chat_id):
            self.usuarios_data["usuarios_autorizados"].append({
                "chat_id": chat_id,
                "nome": nome,
                "ativo": True,
                "admin": admin
            })
            self.salvar_usuarios()
            return True
        return False
    
    def processar_comando_admin(self, comando, chat_id, texto):
        """Comandos administrativos"""
        if not self.usuario_admin(chat_id):
            self.enviar_rapido(chat_id, "❌ Acesso negado")
            return
        
        if comando == "usuarios":
            usuarios = self.usuarios_data["usuarios_autorizados"]
            lista = "👥 *Usuários Autorizados:*\n\n"
            for u in usuarios:
                status = "✅" if u["ativo"] else "❌"
                admin_badge = " 👑" if u.get("admin") else ""
                lista += f"{status} {u['nome']} ({u['chat_id']}){admin_badge}\n"
            self.enviar_rapido(chat_id, lista)
        
        elif comando.startswith("add"):
            # /add 123456789 Nome
            parts = texto.split()
            if len(parts) >= 3:
                try:
                    new_chat_id = int(parts[1])
                    nome = " ".join(parts[2:])
                    if self.adicionar_usuario(new_chat_id, nome):
                        self.enviar_rapido(chat_id, f"✅ Usuário {nome} adicionado")
                        self.enviar_rapido(new_chat_id, "🎉 Você foi autorizado a usar o bot!")
                    else:
                        self.enviar_rapido(chat_id, "❌ Usuário já existe")
                except ValueError:
                    self.enviar_rapido(chat_id, "❌ ID inválido")
    
    def processar_mensagem(self, chat_id, texto):
        """Processamento com controle de acesso"""
        # Verificar autorização
        if not self.usuario_autorizado(chat_id):
            if texto == "/start":
                self.enviar_rapido(chat_id, """🔒 *Acesso Restrito*
                
Este bot é privado. Entre em contato com o administrador para solicitar acesso.

👤 Seu ID: `{}`""".format(chat_id))
            else:
                self.enviar_rapido(chat_id, "❌ Usuário não autorizado")
            return
        
        # Comandos administrativos
        if texto.startswith('/') and len(texto) > 1:
            comando = texto[1:].lower()
            
            if comando in ["usuarios", "add"] or comando.startswith("add"):
                self.processar_comando_admin(comando, chat_id, texto)
                return
        
        # Processamento normal
        super().processar_mensagem(chat_id, texto)
    
    def salvar_async(self, descricao, valor, categoria, chat_id):
        """Salvamento com identificação do usuário"""
        def salvar():
            try:
                # Adicionar identificação do usuário na descrição
                usuario = next((u["nome"] for u in self.usuarios_data["usuarios_autorizados"] 
                              if u["chat_id"] == chat_id), f"ID:{chat_id}")
                
                descricao_completa = f"{descricao} ({usuario})"
                
                if self.sheets.adicionar_gasto(descricao_completa, valor, categoria):
                    self.enviar_rapido(chat_id, f"✅ {descricao} - R$ {valor:.2f}\n📂 {categoria.title()}")
                else:
                    self.enviar_rapido(chat_id, "❌ Erro ao salvar")
            except:
                self.enviar_rapido(chat_id, "❌ Erro ao salvar")
        
        threading.Thread(target=salvar, daemon=True).start()

if __name__ == "__main__":
    bot = BotMultiUsuario()
    bot.executar()
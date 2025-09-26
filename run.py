#!/usr/bin/env python3
"""
Ponto de entrada principal da aplicação
Bot WhatsApp - Controle de Gastos
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.app import main

if __name__ == "__main__":
    main()
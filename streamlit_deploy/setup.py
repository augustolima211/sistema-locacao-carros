#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de configuração inicial para o LocAuto no Streamlit Cloud
Garante que os dados de backup sejam importados automaticamente
"""

import os
import sys
import sqlite3
from pathlib import Path

def setup_database():
    """Configura o banco de dados e importa dados se necessário"""
    
    # Verificar se o banco existe e tem dados
    db_path = "locauto.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se existem dados
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE ativo = 1")
        clientes_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM veiculos WHERE ativo = 1")
        veiculos_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"📊 Status atual: {clientes_count} clientes, {veiculos_count} veículos")
        
        # Se não há dados, importar backup
        if clientes_count == 0 or veiculos_count == 0:
            print("🔄 Importando dados de backup...")
            
            # Executar script de importação
            if os.path.exists("import_backup.py"):
                import import_backup
                import_backup.import_backup_data()
                print("✅ Dados importados com sucesso!")
            else:
                print("⚠️ Arquivo import_backup.py não encontrado")
        else:
            print("✅ Dados já existem no banco")
            
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
        return False
    
    return True

if __name__ == "__main__":
    setup_database()
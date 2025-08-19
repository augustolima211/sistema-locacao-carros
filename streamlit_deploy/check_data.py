#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar os dados importados no banco
"""

import sqlite3

def check_imported_data():
    """Verifica os dados importados no banco"""
    try:
        conn = sqlite3.connect('locauto.db')
        cursor = conn.cursor()
        
        # Contar registros
        cursor.execute('SELECT COUNT(*) FROM veiculos')
        total_veiculos = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM clientes')
        total_clientes = cursor.fetchone()[0]
        
        print(f"📊 Dados no banco:")
        print(f"   🚗 Total de veículos: {total_veiculos}")
        print(f"   👥 Total de clientes: {total_clientes}")
        
        # Mostrar alguns veículos
        print(f"\n🚗 Primeiros 5 veículos:")
        cursor.execute('SELECT modelo, placa, ano, cor, valor_diaria FROM veiculos LIMIT 5')
        for row in cursor.fetchall():
            print(f"   {row[0]} - {row[1]} ({row[2]}) - {row[3]} - R$ {row[4]:.2f}")
        
        # Mostrar alguns clientes
        print(f"\n👥 Primeiros 3 clientes:")
        cursor.execute('SELECT nome, cpf_cnpj, cidade FROM clientes LIMIT 3')
        for row in cursor.fetchall():
            print(f"   {row[0]} - {row[1]} - {row[2]}")
        
        conn.close()
        print(f"\n✅ Verificação concluída!")
        
    except Exception as e:
        print(f"❌ Erro ao verificar dados: {e}")

if __name__ == "__main__":
    check_imported_data()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para importar dados de backup no banco de dados LocAuto
Importa dados de veículos e clientes fornecidos pelo usuário
"""

import sqlite3
import pandas as pd
from io import StringIO
import re
from datetime import datetime

def clean_currency(value):
    """Remove formatação de moeda e converte para float"""
    if pd.isna(value) or value == '':
        return 0.0
    # Remove R$, espaços e vírgulas, substitui vírgula por ponto
    cleaned = str(value).replace('R$', '').replace(' ', '').replace(',', '.')
    cleaned = re.sub(r'[^\d.]', '', cleaned)
    try:
        return float(cleaned)
    except:
        return 0.0

def clean_text(value):
    """Remove espaços extras do texto"""
    if pd.isna(value) or value == '':
        return ''
    return str(value).strip()

def import_backup_data():
    """Importa os dados de backup fornecidos pelo usuário"""
    
    # Dados de veículos fornecidos
    veiculos_data = """,id,modelo,placa,ano,cor,valor_diaria,disponivel,data_cadastro,ativo
0,7,ARGO,QPQ3E24,2019,BRANCO,"R$ 80,00",1,2025-08-19 11:48:41,1
1,8,ARGO,RVV9I66,2023,BRANCO,"R$ 80,00",1,2025-08-19 11:49:16,1
2,3,FOD K ,GDH8111,2018,BRANCO ,"R$ 80,00",1,2025-08-19 11:46:12,1
3,10,FORD K ,FSS5E24,2018,BRANCO,"R$ 70,00",1,2025-08-19 13:10:24,1
4,4,HB20,FVN0F16,2019,PRETO,"R$ 80,00",1,2025-08-19 11:46:41,1
5,6,LOGAN,GFY4C68,2021,BRANCO,"R$ 80,00",1,2025-08-19 11:48:17,1
6,2,MOBI,QWR7J17,2020,BRANCO ,"R$ 80,00",1,2025-08-19 11:45:45,1
7,1,NOVO UNO ,RFL4J94,2020,BRANCO ,"R$ 80,00",1,2025-08-19 11:45:15,1
8,5,ONIX LT,QQA0J66,2019,BRANCO,"R$ 80,00",1,2025-08-19 11:47:53,1
9,9,SPIN ,EWU1I34,2013,BRANCO,"R$ 80,00",1,2025-08-19 11:50:06,1"""
    
    # Dados de clientes fornecidos
    clientes_data = """,id,nome,cpf_cnpj,telefone,endereco,rua,numero,complemento,bairro,cidade,uf,cep,email,data_cadastro,ativo
0,2,ALINE DE OLIVEIRA MORAIS MOREURA ,312.584.818-04,(35) 99913-0383,"RUA MONSENHOR JOSE MARIA MATHIAS SILVA , 67, AP, JARDIM CIDADE , PASSOS - MG, CEP: 37902138",RUA MONSENHOR JOSE MARIA MATHIAS SILVA ,67,AP,JARDIM CIDADE ,PASSOS,MG,37902138,,2025-08-19 11:37:01,1
1,1,CELSO ANTONIO DE MELO ,011.776.116-86,(35) 99170-4072,"RUA LUIZ CARLOS OLIVEIRA , 540, IVONE SIMAO CALIXTO, ITAU DE MINAS - MG, CEP: 37975000",RUA LUIZ CARLOS OLIVEIRA ,540,,IVONE SIMAO CALIXTO,ITAU DE MINAS,MG,37975000,,2025-08-19 11:34:33,1
2,4,NAILTON BISPO DE ROMA,098.422.466-12,,"RUA LIBRA , 34, SERRA VERDE , PASSOS  - MG, CEP: 37901310",RUA LIBRA ,34,,SERRA VERDE ,PASSOS ,MG,37901310,,2025-08-19 12:55:06,1
3,3,lago cunha soluções agricolas ltda ,57.334.181/0001-00,(35) 99707-2921,"RODOVIA MG-050, 802, ROVOVIA , PASSOS - MG, CEP: 37901-300",RODOVIA MG-050,802,,ROVOVIA ,PASSOS,MG,37901-300,,2025-08-19 11:43:06,1"""
    
    try:
        # Conectar ao banco de dados
        conn = sqlite3.connect('locauto.db')
        cursor = conn.cursor()
        
        print("🔄 Iniciando importação dos dados de backup...")
        
        # Processar dados de veículos
        print("\n📋 Importando veículos...")
        df_veiculos = pd.read_csv(StringIO(veiculos_data))
        
        for _, row in df_veiculos.iterrows():
            # Limpar e processar dados
            modelo = clean_text(row['modelo'])
            placa = clean_text(row['placa'])
            ano = int(row['ano']) if pd.notna(row['ano']) else 2020
            cor = clean_text(row['cor'])
            valor_diaria = clean_currency(row['valor_diaria'])
            disponivel = int(row['disponivel']) if pd.notna(row['disponivel']) else 1
            data_cadastro = row['data_cadastro'] if pd.notna(row['data_cadastro']) else datetime.now().isoformat()
            ativo = int(row['ativo']) if pd.notna(row['ativo']) else 1
            
            # Verificar se veículo já existe
            cursor.execute("SELECT id FROM veiculos WHERE placa = ?", (placa,))
            if cursor.fetchone():
                print(f"  ⚠️  Veículo {placa} já existe - pulando")
                continue
            
            # Inserir veículo
            cursor.execute("""
                INSERT INTO veiculos (modelo, placa, ano, cor, valor_diaria, disponivel, data_cadastro, ativo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (modelo, placa, ano, cor, valor_diaria, disponivel, data_cadastro, ativo))
            
            print(f"  ✅ Veículo adicionado: {modelo} - {placa}")
        
        # Processar dados de clientes
        print("\n👥 Importando clientes...")
        df_clientes = pd.read_csv(StringIO(clientes_data))
        
        for _, row in df_clientes.iterrows():
            # Limpar e processar dados
            nome = clean_text(row['nome'])
            cpf_cnpj = clean_text(row['cpf_cnpj'])
            telefone = clean_text(row['telefone'])
            endereco = clean_text(row['endereco'])
            rua = clean_text(row['rua'])
            numero = clean_text(row['numero'])
            complemento = clean_text(row['complemento'])
            bairro = clean_text(row['bairro'])
            cidade = clean_text(row['cidade'])
            uf = clean_text(row['uf'])
            cep = clean_text(row['cep'])
            email = clean_text(row['email'])
            data_cadastro = row['data_cadastro'] if pd.notna(row['data_cadastro']) else datetime.now().isoformat()
            ativo = int(row['ativo']) if pd.notna(row['ativo']) else 1
            
            # Verificar se cliente já existe
            cursor.execute("SELECT id FROM clientes WHERE cpf_cnpj = ?", (cpf_cnpj,))
            if cursor.fetchone():
                print(f"  ⚠️  Cliente {cpf_cnpj} já existe - pulando")
                continue
            
            # Inserir cliente
            cursor.execute("""
                INSERT INTO clientes (nome, cpf_cnpj, telefone, endereco, rua, numero, complemento, 
                                    bairro, cidade, uf, cep, email, data_cadastro, ativo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (nome, cpf_cnpj, telefone, endereco, rua, numero, complemento, 
                  bairro, cidade, uf, cep, email, data_cadastro, ativo))
            
            print(f"  ✅ Cliente adicionado: {nome}")
        
        # Confirmar alterações
        conn.commit()
        
        # Mostrar estatísticas finais
        cursor.execute("SELECT COUNT(*) FROM veiculos WHERE ativo = 1")
        total_veiculos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE ativo = 1")
        total_clientes = cursor.fetchone()[0]
        
        print(f"\n📊 Importação concluída com sucesso!")
        print(f"   🚗 Total de veículos: {total_veiculos}")
        print(f"   👥 Total de clientes: {total_clientes}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro durante a importação: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    import_backup_data()
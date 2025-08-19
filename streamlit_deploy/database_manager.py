import sqlite3
import pandas as pd
import os
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gerenciador de banco de dados SQLite para o sistema LocAuto"""
    
    def __init__(self, db_path: str = "locauto.db"):
        self.db_path = db_path
        self.init_database()
        self.migrate_csv_data()
    
    def init_database(self):
        """Inicializa o banco de dados e cria as tabelas necessárias"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabela de clientes
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS clientes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        cpf_cnpj TEXT UNIQUE NOT NULL,
                        telefone TEXT,
                        endereco TEXT,
                        rua TEXT,
                        numero TEXT,
                        complemento TEXT,
                        bairro TEXT,
                        cidade TEXT,
                        uf TEXT,
                        cep TEXT,
                        email TEXT,
                        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        ativo BOOLEAN DEFAULT 1
                    )
                """)
                
                # Tabela de veículos
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS veiculos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        modelo TEXT NOT NULL,
                        placa TEXT UNIQUE NOT NULL,
                        ano INTEGER,
                        cor TEXT,
                        valor_diaria REAL NOT NULL,
                        disponivel BOOLEAN DEFAULT 1,
                        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        ativo BOOLEAN DEFAULT 1
                    )
                """)
                
                # Tabela de faturas
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS faturas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        numero_fatura TEXT UNIQUE NOT NULL,
                        cliente_id INTEGER NOT NULL,
                        veiculo_id INTEGER NOT NULL,
                        data_inicio DATE NOT NULL,
                        data_fim DATE NOT NULL,
                        dias INTEGER NOT NULL,
                        valor_diaria REAL NOT NULL,
                        valor_total REAL NOT NULL,
                        observacoes TEXT,
                        data_emissao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status TEXT DEFAULT 'ativa',
                        FOREIGN KEY (cliente_id) REFERENCES clientes (id),
                        FOREIGN KEY (veiculo_id) REFERENCES veiculos (id)
                    )
                """)
                
                # Tabela de transações financeiras
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS transacoes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fatura_id INTEGER,
                        tipo TEXT NOT NULL, -- 'receita' ou 'despesa'
                        descricao TEXT NOT NULL,
                        valor REAL NOT NULL,
                        data_transacao DATE NOT NULL,
                        categoria TEXT,
                        data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (fatura_id) REFERENCES faturas (id)
                    )
                """)
                
                # Tabela de configurações
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS configuracoes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        chave TEXT UNIQUE NOT NULL,
                        valor TEXT NOT NULL,
                        descricao TEXT,
                        data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Inserir configuração inicial do número da fatura
                cursor.execute("""
                    INSERT OR IGNORE INTO configuracoes (chave, valor, descricao)
                    VALUES ('ultimo_numero_fatura', '0', 'Último número de fatura gerado')
                """)
                
                # Atualizar estrutura da tabela de clientes se necessário
                self._update_clientes_table(cursor)
                
                conn.commit()
                logger.info("Banco de dados inicializado com sucesso")
                
        except Exception as e:
            logger.error(f"Erro ao inicializar banco de dados: {e}")
            raise
    
    def _update_clientes_table(self, cursor):
        """Atualiza a estrutura da tabela de clientes adicionando novos campos de endereço"""
        try:
            # Verificar se as colunas já existem
            cursor.execute("PRAGMA table_info(clientes)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # Adicionar novas colunas se não existirem
            new_columns = [
                ('rua', 'TEXT'),
                ('numero', 'TEXT'),
                ('complemento', 'TEXT'),
                ('bairro', 'TEXT'),
                ('cidade', 'TEXT'),
                ('uf', 'TEXT'),
                ('cep', 'TEXT')
            ]
            
            for column_name, column_type in new_columns:
                if column_name not in columns:
                    cursor.execute(f"ALTER TABLE clientes ADD COLUMN {column_name} {column_type}")
                    logger.info(f"Coluna {column_name} adicionada à tabela clientes")
                    
        except Exception as e:
            logger.warning(f"Erro ao atualizar estrutura da tabela clientes: {e}")
    
    def backup_database(self, backup_path: Optional[str] = None) -> str:
        """Cria backup do banco de dados"""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_locauto_{timestamp}.db"
        
        try:
            # Cria diretório de backup se não existir
            backup_dir = "backups"
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            backup_full_path = os.path.join(backup_dir, backup_path)
            
            import shutil
            shutil.copy2(self.db_path, backup_full_path)
            logger.info(f"Backup criado: {backup_full_path}")
            return backup_full_path
        except Exception as e:
            logger.error(f"Erro ao criar backup: {e}")
            raise
    
    def auto_backup(self) -> Optional[str]:
        """Executa backup automático diário"""
        try:
            # Verifica se já foi feito backup hoje
            today = datetime.now().strftime('%Y%m%d')
            backup_dir = "backups"
            
            if os.path.exists(backup_dir):
                existing_backups = [f for f in os.listdir(backup_dir) if f.startswith(f"backup_locauto_{today}")]
                if existing_backups:
                    logger.info("Backup diário já realizado")
                    return os.path.join(backup_dir, existing_backups[0])
            
            # Cria backup
            backup_path = self.backup_database()
            
            # Remove backups antigos (mantém apenas os últimos 30 dias)
            self.cleanup_old_backups()
            
            return backup_path
        except Exception as e:
            logger.error(f"Erro no backup automático: {e}")
            return None
    
    def cleanup_old_backups(self, days_to_keep: int = 30):
        """Remove backups antigos"""
        try:
            from datetime import timedelta
            backup_dir = "backups"
            if not os.path.exists(backup_dir):
                return
            
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            for filename in os.listdir(backup_dir):
                if filename.startswith("backup_locauto_") and filename.endswith(".db"):
                    file_path = os.path.join(backup_dir, filename)
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    
                    if file_time < cutoff_date:
                        os.remove(file_path)
                        logger.info(f"Backup antigo removido: {filename}")
        except Exception as e:
            logger.error(f"Erro ao limpar backups antigos: {e}")
    
    def restore_database(self, backup_path: str) -> bool:
        """Restaura banco de dados a partir de backup"""
        try:
            if not os.path.exists(backup_path):
                logger.error(f"Arquivo de backup não encontrado: {backup_path}")
                return False
            
            # Substitui o banco atual pelo backup
            import shutil
            shutil.copy2(backup_path, self.db_path)
            
            logger.info(f"Banco restaurado a partir de: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Erro ao restaurar backup: {e}")
            return False
    
    def migrate_csv_data(self):
        """Migra dados dos arquivos CSV para o banco de dados"""
        try:
            # Migrar clientes
            if os.path.exists("clientes.csv"):
                df_clientes = pd.read_csv("clientes.csv")
                if not df_clientes.empty:
                    for _, row in df_clientes.iterrows():
                        self.execute_query("""
                            INSERT OR IGNORE INTO clientes (nome, cpf_cnpj, telefone, endereco, email)
                            VALUES (?, ?, ?, ?, ?)
                        """, (row.get('Nome', ''), row.get('CPF/CNPJ', ''), 
                              row.get('Telefone', ''), row.get('Endereço', ''), row.get('Email', '')))
            
            # Migrar veículos
            if os.path.exists("veiculos.csv"):
                df_veiculos = pd.read_csv("veiculos.csv")
                if not df_veiculos.empty:
                    for _, row in df_veiculos.iterrows():
                        self.execute_query("""
                            INSERT OR IGNORE INTO veiculos (modelo, placa, ano, cor, valor_diaria)
                            VALUES (?, ?, ?, ?, ?)
                        """, (row.get('Modelo', ''), row.get('Placa', ''), 
                              row.get('Ano', 0), row.get('Cor', ''), row.get('Valor Diária', 0)))
            
            # Migrar transações
            if os.path.exists("transacoes.csv"):
                df_transacoes = pd.read_csv("transacoes.csv")
                if not df_transacoes.empty:
                    for _, row in df_transacoes.iterrows():
                        self.execute_query("""
                            INSERT OR IGNORE INTO transacoes (tipo, descricao, valor, data_transacao, categoria)
                            VALUES (?, ?, ?, ?, ?)
                        """, (row.get('Tipo', ''), row.get('Descrição', ''), 
                              row.get('Valor', 0), row.get('Data', ''), row.get('Categoria', '')))
            
            logger.info("Migração de dados CSV concluída")
            
        except Exception as e:
            logger.warning(f"Erro na migração de dados CSV: {e}")
    
    def get_next_invoice_number(self) -> str:
        """Obtém o próximo número de fatura sequencial"""
        try:
            result = self.execute_query(
                "SELECT valor FROM configuracoes WHERE chave = 'ultimo_numero_fatura'",
                fetch_one=True
            )
            
            if result:
                ultimo_numero = int(result[0])
            else:
                ultimo_numero = 0
            
            novo_numero = ultimo_numero + 1
            
            # Atualizar o último número
            self.execute_query(
                "UPDATE configuracoes SET valor = ?, data_atualizacao = CURRENT_TIMESTAMP WHERE chave = 'ultimo_numero_fatura'",
                (str(novo_numero),)
            )
            
            return f"{novo_numero:06d}"
            
        except Exception as e:
            logger.error(f"Erro ao obter próximo número de fatura: {e}")
            return "000001"
    
    def execute_query(self, query: str, params: tuple = (), fetch_one: bool = False, fetch_all: bool = False):
        """Executa uma query no banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                if fetch_one:
                    return cursor.fetchone()
                elif fetch_all:
                    return cursor.fetchall()
                
                conn.commit()
                return cursor.lastrowid
                
        except Exception as e:
            logger.error(f"Erro ao executar query: {e}")
            raise
    
    def get_dataframe(self, query: str, params: tuple = ()) -> pd.DataFrame:
        """Retorna um DataFrame a partir de uma query"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                return pd.read_sql_query(query, conn, params=params)
        except Exception as e:
            logger.error(f"Erro ao obter DataFrame: {e}")
            return pd.DataFrame()
    
    def get_clientes(self) -> pd.DataFrame:
        """Retorna todos os clientes ativos"""
        return self.get_dataframe("SELECT * FROM clientes WHERE ativo = 1 ORDER BY nome")
    
    def get_veiculos(self) -> pd.DataFrame:
        """Retorna todos os veículos ativos"""
        return self.get_dataframe("SELECT * FROM veiculos WHERE ativo = 1 ORDER BY modelo")
    
    def get_faturas(self) -> pd.DataFrame:
        """Retorna todas as faturas com informações de cliente e veículo"""
        query = """
            SELECT f.*, c.nome as cliente_nome, v.modelo as veiculo_modelo, v.placa as veiculo_placa
            FROM faturas f
            JOIN clientes c ON f.cliente_id = c.id
            JOIN veiculos v ON f.veiculo_id = v.id
            ORDER BY f.data_emissao DESC
        """
        return self.get_dataframe(query)
    
    def get_transacoes(self) -> pd.DataFrame:
        """Retorna todas as transações"""
        return self.get_dataframe("SELECT * FROM transacoes ORDER BY data_transacao DESC")
    
    def add_cliente(self, nome: str, cpf_cnpj: str, telefone: str = "", endereco: str = "", 
                   email: str = "", rua: str = "", numero: str = "", complemento: str = "", 
                   bairro: str = "", cidade: str = "", uf: str = "", cep: str = "") -> int:
        """Adiciona um novo cliente"""
        return self.execute_query(
            """INSERT INTO clientes (nome, cpf_cnpj, telefone, endereco, rua, numero, 
                                    complemento, bairro, cidade, uf, cep, email) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (nome, cpf_cnpj, telefone, endereco, rua, numero, complemento, bairro, cidade, uf, cep, email)
        )
    
    def add_veiculo(self, modelo: str, placa: str, ano: int, cor: str, valor_diaria: float) -> int:
        """Adiciona um novo veículo"""
        return self.execute_query(
            "INSERT INTO veiculos (modelo, placa, ano, cor, valor_diaria) VALUES (?, ?, ?, ?, ?)",
            (modelo, placa, ano, cor, valor_diaria)
        )
    
    def add_fatura(self, numero_fatura: str, cliente_id: int, veiculo_id: int, 
                   data_inicio: str, data_fim: str, dias: int, valor_diaria: float, 
                   valor_total: float, observacoes: str = "", data_emissao: str = None) -> int:
        """Adiciona uma nova fatura"""
        if data_emissao is None:
            # Se não especificada, usar a data atual
            return self.execute_query(
                """INSERT INTO faturas (numero_fatura, cliente_id, veiculo_id, data_inicio, 
                                       data_fim, dias, valor_diaria, valor_total, observacoes) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (numero_fatura, cliente_id, veiculo_id, data_inicio, data_fim, 
                 dias, valor_diaria, valor_total, observacoes)
            )
        else:
            # Usar a data de emissão especificada
            return self.execute_query(
                """INSERT INTO faturas (numero_fatura, cliente_id, veiculo_id, data_inicio, 
                                       data_fim, dias, valor_diaria, valor_total, observacoes, data_emissao) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (numero_fatura, cliente_id, veiculo_id, data_inicio, data_fim, 
                 dias, valor_diaria, valor_total, observacoes, data_emissao)
            )
    
    def add_transacao(self, tipo: str, descricao: str, valor: float, data_transacao: str, 
                     categoria: str = "", fatura_id: Optional[int] = None) -> int:
        """Adiciona uma nova transação"""
        return self.execute_query(
            "INSERT INTO transacoes (fatura_id, tipo, descricao, valor, data_transacao, categoria) VALUES (?, ?, ?, ?, ?, ?)",
            (fatura_id, tipo, descricao, valor, data_transacao, categoria)
        )
    
    def get_cliente_by_id(self, cliente_id: int) -> Optional[Dict[str, Any]]:
        """Retorna um cliente pelo ID"""
        result = self.execute_query("SELECT * FROM clientes WHERE id = ?", (cliente_id,), fetch_one=True)
        if result:
            columns = ['id', 'nome', 'cpf_cnpj', 'telefone', 'endereco', 'rua', 'numero', 
                      'complemento', 'bairro', 'cidade', 'uf', 'cep', 'email', 'data_cadastro', 'ativo']
            return dict(zip(columns, result))
        return None
    
    def get_veiculo_by_id(self, veiculo_id: int) -> Optional[Dict[str, Any]]:
        """Retorna um veículo pelo ID"""
        result = self.execute_query("SELECT * FROM veiculos WHERE id = ?", (veiculo_id,), fetch_one=True)
        if result:
            columns = ['id', 'modelo', 'placa', 'ano', 'cor', 'valor_diaria', 'disponivel', 'data_cadastro', 'ativo']
            return dict(zip(columns, result))
        return None
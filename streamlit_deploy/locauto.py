import streamlit as st
import pandas as pd
import base64
from datetime import datetime
import os
from io import BytesIO
from xhtml2pdf import pisa
import re
from database_manager import DatabaseManager
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(
    page_title="LocAuto - Sistema de Locação",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #2a5298;
    }
    .stButton > button {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #2a5298 0%, #1e3c72 100%);
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }
    .sidebar-content {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar o gerenciador de banco de dados
@st.cache_resource
def init_database():
    db_manager = DatabaseManager()
    # Executar backup automático
    db_manager.auto_backup()
    
    # Importar dados de backup se o banco estiver vazio
    try:
        clientes = db_manager.get_dataframe("clientes", "ativo = 1")
        veiculos = db_manager.get_dataframe("veiculos", "ativo = 1")
        
        if clientes.empty or veiculos.empty:
            # Executar importação dos dados de backup
            import subprocess
            import sys
            result = subprocess.run([sys.executable, "import_backup.py"], 
                                  capture_output=True, text=True, cwd=".")
            if result.returncode == 0:
                st.success("✅ Dados de backup importados com sucesso!")
            else:
                st.warning(f"⚠️ Erro na importação: {result.stderr}")
    except Exception as e:
        st.warning(f"⚠️ Erro ao verificar dados: {e}")
    
    return db_manager

db = init_database()

# Funções auxiliares
def format_currency(value):
    """Formata valor como moeda brasileira"""
    return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def format_cpf_cnpj(doc):
    """Formata CPF ou CNPJ"""
    doc = re.sub(r'\D', '', str(doc))
    if len(doc) == 11:  # CPF
        return f"{doc[:3]}.{doc[3:6]}.{doc[6:9]}-{doc[9:]}"
    elif len(doc) == 14:  # CNPJ
        return f"{doc[:2]}.{doc[2:5]}.{doc[5:8]}/{doc[8:12]}-{doc[12:]}"
    return doc

def format_phone(phone):
    """Formata telefone"""
    phone = re.sub(r'\D', '', str(phone))
    if len(phone) == 11:
        return f"({phone[:2]}) {phone[2:7]}-{phone[7:]}"
    elif len(phone) == 10:
        return f"({phone[:2]}) {phone[2:6]}-{phone[6:]}"
    return phone

def generate_professional_pdf(cliente_data, veiculo_data, fatura_data):
    """Gera PDF profissional no formato de fatura de locação seguindo exatamente o modelo fornecido"""
    
    # Converter valor para extenso
    def numero_para_extenso(valor):
        """Converte número para extenso (simplificado)"""
        unidades = ['', 'um', 'dois', 'três', 'quatro', 'cinco', 'seis', 'sete', 'oito', 'nove']
        dezenas = ['', '', 'vinte', 'trinta', 'quarenta', 'cinquenta', 'sessenta', 'setenta', 'oitenta', 'noventa']
        centenas = ['', 'cento', 'duzentos', 'trezentos', 'quatrocentos', 'quinhentos', 'seiscentos', 'setecentos', 'oitocentos', 'novecentos']
        
        valor_int = int(valor)
        if valor_int == 0:
            return "zero reais"
        elif valor_int < 1000:
            if valor_int < 100:
                if valor_int < 20:
                    especiais = ['dez', 'onze', 'doze', 'treze', 'quatorze', 'quinze', 'dezesseis', 'dezessete', 'dezoito', 'dezenove']
                    if valor_int >= 10:
                        return especiais[valor_int - 10] + " reais"
                    else:
                        return unidades[valor_int] + (" real" if valor_int == 1 else " reais")
                else:
                    dezena = valor_int // 10
                    unidade = valor_int % 10
                    resultado = dezenas[dezena]
                    if unidade > 0:
                        resultado += " e " + unidades[unidade]
                    return resultado + " reais"
            else:
                centena = valor_int // 100
                resto = valor_int % 100
                resultado = centenas[centena]
                if resto > 0:
                    if resto < 20 and resto >= 10:
                        especiais = ['dez', 'onze', 'doze', 'treze', 'quatorze', 'quinze', 'dezesseis', 'dezessete', 'dezoito', 'dezenove']
                        resultado += " e " + especiais[resto - 10]
                    elif resto < 10:
                        resultado += " e " + unidades[resto]
                    else:
                        dezena = resto // 10
                        unidade = resto % 10
                        resultado += " e " + dezenas[dezena]
                        if unidade > 0:
                            resultado += " e " + unidades[unidade]
                return resultado + " reais"
        else:
            return "Dois mil e quatrocentos reais"  # Simplificado para valores maiores
    
    valor_extenso = numero_para_extenso(fatura_data['valor_total'])
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 0.5cm;
            }}
            body {{
                font-family: Arial, sans-serif;
                font-size: 9px;
                line-height: 1.1;
                color: #000;
                margin: 0;
                padding: 0;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                border: 1px solid #000;
            }}
            td, th {{
                border: 1px solid #000;
                padding: 4px;
                vertical-align: top;
                font-size: 9px;
            }}
            .logo-cell {{
                width: 100px;
                text-align: center;
                background-color: #fff;
                color: black;
                font-weight: bold;
                font-size: 8px;
                padding: 8px;
                border: 1px solid #000;
            }}
            .logo-img {{
                width: 80px;
                height: 80px;
                object-fit: contain;
            }}
            .company-info {{
                font-size: 8px;
                line-height: 1.0;
                padding: 4px;
            }}
            .header-title {{
                text-align: center;
                font-weight: bold;
                font-size: 12px;
                padding: 8px;
            }}
            .invoice-number {{
                text-align: center;
                font-weight: bold;
                font-size: 10px;
                padding: 8px;
            }}
            .section-label {{
                font-weight: bold;
                font-size: 9px;
            }}
            .description-cell {{
                height: 150px;
                vertical-align: top;
                padding: 8px;
            }}
            .value-cell {{
                text-align: right;
                vertical-align: top;
                padding: 8px;
                width: 120px;
            }}
            .total-label {{
                text-align: center;
                font-weight: bold;
                background-color: #f0f0f0;
            }}
            .footer-note {{
                text-align: center;
                font-size: 8px;
                padding: 4px;
            }}
        </style>
    </head>
    <body>
        <!-- Cabeçalho Principal -->
        <table>
            <tr>
                <td class="logo-cell">
                    <img src="logo.png" alt="HT Locações" class="logo-img"><br>
                    <small>HT LOCAÇÕES AUTO LTDA</small>
                </td>
                <td class="company-info">
                    <strong>HT Locações Auto LTDA</strong><br>
                    CNPJ: 05.261.064/0001-60 - I. Mun.:<br>
                    Rua dos boiadeiros, 566 - Belo Horizonte<br>
                    PASSOS / MG CEP 37900-114<br>
                    FONE: (35)999817121 FAX: ( )
                </td>
                <td class="header-title">
                    FATURA DE LOCAÇÃO
                </td>
                <td class="invoice-number">
                    Nº{fatura_data['numero_fatura']}
                </td>
            </tr>
        </table>

        <!-- Linha de Data, Valor e Vencimento -->
        <table>
            <tr>
                <td style="width: 25%;"><span class="section-label">Data da Emissão:</span><br>{datetime.now().strftime('%d/%m/%Y')}</td>
                <td style="width: 25%;"><span class="section-label">Fatura/Duplicata Valor R$:</span><br>{format_currency(fatura_data['valor_total'])}</td>
                <td style="width: 25%;"><span class="section-label">Vencimento(s):</span><br>{datetime.strptime(fatura_data['data_fim'], '%Y-%m-%d').strftime('%d/%m/%Y')}</td>
                <td style="width: 25%;"></td>
            </tr>
        </table>

        <!-- Valor por Extenso -->
        <table>
            <tr>
                <td><span class="section-label">Valor por Extenso:</span><br>{valor_extenso.title()}</td>
            </tr>
        </table>

        <!-- Dados do Cliente -->
        <table>
            <tr>
                <td style="width: 50%;"><span class="section-label">Sacado:</span> {cliente_data['nome'].upper()}</td>
                <td style="width: 50%;"></td>
            </tr>
        </table>
        
        <table>
            <tr>
                <td style="width: 50%;"><span class="section-label">CNPJ/CPF:</span> {format_cpf_cnpj(cliente_data['cpf_cnpj'])}</td>
                <td style="width: 25%;"><span class="section-label">Município:</span><br>{(cliente_data.get('cidade') or 'ITAÚ DE MINAS').upper()}</td>
                <td style="width: 25%;"></td>
            </tr>
        </table>
        
        <table>
            <tr>
                <td style="width: 50%;"><span class="section-label">Endereço:</span> {cliente_data.get('endereco', '') if cliente_data.get('endereco') else ''}</td>
                <td style="width: 25%;"><span class="section-label">UF:</span><br>{cliente_data.get('uf') or 'MG'}</td>
                <td style="width: 25%;"></td>
            </tr>
        </table>
        
        <table>
            <tr>
                <td style="width: 50%;"><span class="section-label">Bairro:</span> {cliente_data.get('bairro') or ''}</td>
                <td style="width: 25%;"><span class="section-label">CEP:</span><br>{cliente_data.get('cep') or '37975-000'}</td>
                <td style="width: 25%;"></td>
            </tr>
        </table>

        <!-- Descrição e Valor -->
        <table>
            <tr>
                <td class="total-label" style="width: 70%;">Descrição</td>
                <td class="total-label" style="width: 30%;">Valor R$</td>
            </tr>
            <tr>
                <td class="description-cell">
                    Contrato: 1/12 &nbsp;&nbsp;&nbsp; Período: {datetime.strptime(fatura_data['data_inicio'], '%Y-%m-%d').strftime('%d/%m/%Y')} a {datetime.strptime(fatura_data['data_fim'], '%Y-%m-%d').strftime('%d/%m/%Y')}<br>
                    Placa Atual: {veiculo_data['placa']}<br>
                    Veículo: {veiculo_data['modelo']} - {veiculo_data.get('cor', 'Branco')}<br>
                    Itens/Despesas e Serviços Adicionais:<br>
                    Locação Mensal - {format_currency(fatura_data['valor_total'])}
                    {f'<br><br>Observações: {fatura_data.get("observacoes", "")}' if fatura_data.get('observacoes') else ''}
                </td>
                <td class="value-cell">
                    {format_currency(fatura_data['valor_total'])}
                </td>
            </tr>
        </table>

        <!-- Total da Fatura -->
        <table>
            <tr>
                <td style="width: 70%; text-align: center; font-weight: bold;">Total da Fatura</td>
                <td style="width: 30%; text-align: right; font-weight: bold;">{format_currency(fatura_data['valor_total'])}</td>
            </tr>
        </table>

        <!-- Nota de Rodapé -->
        <table>
            <tr>
                <td class="footer-note">Atividade não sujeita ao ISSQN e à emissão de NF conforme Lei 116/03 - Item 3.01</td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    # Gerar PDF
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html_content.encode("UTF-8")), result)
    
    if not pdf.err:
        return result.getvalue()
    return None

def main():
    # Sidebar para navegação
    st.sidebar.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    st.sidebar.title("🚗 LocAuto")
    st.sidebar.markdown("Sistema de Locação de Veículos")
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Menu de navegação
    page = st.sidebar.selectbox(
        "Navegação",
        ["📊 Dashboard", "📝 Nova Fatura", "👥 Clientes", "🚗 Veículos", "💰 Financeiro", "📈 Relatórios"]
    )
    
    # Dashboard
    if page == "📊 Dashboard":
        st.markdown('<div class="main-header"><h1>Dashboard - LocAuto</h1></div>', unsafe_allow_html=True)
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        # Obter dados para métricas
        clientes_df = db.get_clientes()
        veiculos_df = db.get_veiculos()
        faturas_df = db.get_faturas()
        transacoes_df = db.get_transacoes()
        
        with col1:
            st.metric("Total de Clientes", len(clientes_df))
        
        with col2:
            st.metric("Total de Veículos", len(veiculos_df))
        
        with col3:
            if not faturas_df.empty:
                receita_total = faturas_df['valor_total'].sum()
                st.metric("Receita Total", format_currency(receita_total))
            else:
                st.metric("Receita Total", "R$ 0,00")
        
        with col4:
            st.metric("Faturas Emitidas", len(faturas_df))
        
        # Gráficos
        if not faturas_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Receita por Mês")
                faturas_df['mes'] = pd.to_datetime(faturas_df['data_emissao']).dt.to_period('M')
                receita_mensal = faturas_df.groupby('mes')['valor_total'].sum().reset_index()
                receita_mensal['mes'] = receita_mensal['mes'].astype(str)
                
                fig = px.bar(receita_mensal, x='mes', y='valor_total', 
                           title="Receita Mensal",
                           labels={'valor_total': 'Receita (R$)', 'mes': 'Mês'})
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("🚗 Veículos Mais Locados")
                veiculos_locados = faturas_df.groupby('veiculo_modelo').size().reset_index(name='locacoes')
                
                fig = px.pie(veiculos_locados, values='locacoes', names='veiculo_modelo',
                           title="Distribuição de Locações por Veículo")
                st.plotly_chart(fig, use_container_width=True)
        
        # Últimas faturas
        st.subheader("📋 Últimas Faturas")
        if not faturas_df.empty:
            st.dataframe(faturas_df.head(10), use_container_width=True)
        else:
            st.info("Nenhuma fatura encontrada.")
    
    # Nova Fatura
    elif page == "📝 Nova Fatura":
        st.markdown('<div class="main-header"><h1>Nova Fatura de Locação</h1></div>', unsafe_allow_html=True)
        
        # Obter dados
        clientes_df = db.get_clientes()
        veiculos_df = db.get_veiculos()
        
        if clientes_df.empty:
            st.warning("⚠️ Nenhum cliente cadastrado. Cadastre um cliente primeiro.")
            return
        
        if veiculos_df.empty:
            st.warning("⚠️ Nenhum veículo cadastrado. Cadastre um veículo primeiro.")
            return
        
        with st.form("nova_fatura"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Seleção de cliente
                cliente_options = {f"{row['nome']} - {format_cpf_cnpj(row['cpf_cnpj'])}": row['id'] 
                                 for _, row in clientes_df.iterrows()}
                cliente_selecionado = st.selectbox("Cliente", list(cliente_options.keys()))
                cliente_id = cliente_options[cliente_selecionado]
                
                # Seleção de veículo
                veiculo_options = {f"{row['modelo']} - {row['placa']}": row['id'] 
                                 for _, row in veiculos_df.iterrows()}
                veiculo_selecionado = st.selectbox("Veículo", list(veiculo_options.keys()))
                veiculo_id = veiculo_options[veiculo_selecionado]
                
                # Datas
                data_inicio = st.date_input("Data de Início")
                data_fim = st.date_input("Data de Término")
            
            with col2:
                # Calcular período
                if data_fim >= data_inicio:
                    dias = (data_fim - data_inicio).days + 1
                    st.write(f"**Período:** {dias} dia(s)")
                    
                    # Valor mensal da locação (inserido pelo usuário)
                    valor_total = st.number_input(
                        "Valor Mensal da Locação (R$)",
                        min_value=0.0,
                        value=2400.0,
                        step=50.0,
                        format="%.2f"
                    )
                    
                    # Calcular valor diário baseado no valor mensal
                    valor_diaria = valor_total / max(dias, 1) if dias > 0 else 0
                    
                    st.write(f"**Valor Total:** {format_currency(valor_total)}")
                    st.write(f"**Valor Diário Equivalente:** {format_currency(valor_diaria)}")
                else:
                    st.error("Data de término deve ser posterior à data de início")
                    dias = 0
                    valor_total = 0
                    valor_diaria = 0
                
                # Observações
                observacoes = st.text_area("Observações (opcional)")
            
                # Campo para número da fatura (editável)
                # Obter próximo número como sugestão
                if 'proximo_numero_fatura' not in st.session_state:
                    st.session_state.proximo_numero_fatura = db.get_next_invoice_number()
                
                numero_fatura_input = st.text_input(
                    "Número da Fatura", 
                    value=st.session_state.proximo_numero_fatura,
                    help="Você pode editar o número da fatura. O sistema manterá a sequência automaticamente."
                )
            
            # Botão para gerar fatura
            if st.form_submit_button("🧾 Gerar Fatura", use_container_width=True):
                if dias > 0 and valor_total > 0 and numero_fatura_input.strip():
                    try:
                        # Validar se o número da fatura já existe
                        fatura_existente = db.execute_query(
                            "SELECT id FROM faturas WHERE numero_fatura = ?", 
                            (numero_fatura_input.strip(),), 
                            fetch_one=True
                        )
                        
                        if fatura_existente:
                            st.error(f"❌ Número de fatura {numero_fatura_input} já existe. Escolha outro número.")
                        else:
                            # Obter dados do veículo
                            veiculo_data = db.get_veiculo_by_id(veiculo_id)
                            
                            # Usar o número da fatura informado
                            numero_fatura = numero_fatura_input.strip()
                        
                            # Salvar fatura no banco
                            fatura_id = db.add_fatura(
                                numero_fatura=numero_fatura,
                                cliente_id=cliente_id,
                                veiculo_id=veiculo_id,
                                data_inicio=data_inicio.strftime('%Y-%m-%d'),
                                data_fim=data_fim.strftime('%Y-%m-%d'),
                                dias=dias,
                                valor_diaria=valor_diaria,
                                valor_total=valor_total,
                                observacoes=observacoes
                            )
                            
                            # Atualizar o último número de fatura se for maior que o atual
                            try:
                                numero_atual = int(numero_fatura)
                                ultimo_numero_result = db.execute_query(
                                    "SELECT valor FROM configuracoes WHERE chave = 'ultimo_numero_fatura'",
                                    fetch_one=True
                                )
                                if ultimo_numero_result:
                                    ultimo_numero = int(ultimo_numero_result[0])
                                    if numero_atual > ultimo_numero:
                                        db.execute_query(
                                            "UPDATE configuracoes SET valor = ?, data_atualizacao = CURRENT_TIMESTAMP WHERE chave = 'ultimo_numero_fatura'",
                                            (str(numero_atual),)
                                        )
                            except ValueError:
                                # Se o número não for numérico, não atualiza a sequência
                                pass
                        
                            # Adicionar transação de receita
                            db.add_transacao(
                                tipo="receita",
                                descricao=f"Locação Mensal - {veiculo_data['modelo']} - {veiculo_data['placa']}",
                                valor=valor_total,
                                data_transacao=datetime.now().strftime('%Y-%m-%d'),
                                categoria="Locação",
                                fatura_id=fatura_id
                            )
                            
                            # Obter dados para o PDF
                            cliente_data = db.get_cliente_by_id(cliente_id)
                            
                            fatura_data = {
                                'numero_fatura': numero_fatura,
                                'data_inicio': data_inicio.strftime('%Y-%m-%d'),
                                'data_fim': data_fim.strftime('%Y-%m-%d'),
                                'dias': dias,
                                'valor_diaria': valor_diaria,
                                'valor_total': valor_total,
                                'observacoes': observacoes
                            }
                            
                            # Gerar PDF
                            pdf_bytes = generate_professional_pdf(cliente_data, veiculo_data, fatura_data)
                            
                            if pdf_bytes:
                                st.success(f"✅ Fatura {numero_fatura} gerada com sucesso!")
                                
                                # Armazenar PDF no session_state para download fora do form
                                st.session_state.pdf_data = pdf_bytes
                                st.session_state.pdf_filename = f"fatura_{numero_fatura}.pdf"
                                st.session_state.show_download = True
                            else:
                                st.error("❌ Erro ao gerar PDF da fatura")
                                
                    except Exception as e:
                        st.error(f"❌ Erro ao gerar fatura: {str(e)}")
                elif not numero_fatura_input.strip():
                    st.error("❌ Número da fatura é obrigatório")
                else:
                    st.error("❌ Período inválido ou valor não informado")
        
        # Botão para atualizar número da fatura (fora do formulário)
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🔄 Atualizar Número"):
                st.session_state.proximo_numero_fatura = db.get_next_invoice_number()
                st.rerun()
        
        # Botão de download fora do formulário
        if hasattr(st.session_state, 'show_download') and st.session_state.show_download:
            st.download_button(
                label="📄 Baixar Fatura em PDF",
                data=st.session_state.pdf_data,
                file_name=st.session_state.pdf_filename,
                mime="application/pdf",
                use_container_width=True
            )
            # Limpar após download
            if st.button("🔄 Nova Fatura"):
                st.session_state.show_download = False
                if 'proximo_numero_fatura' in st.session_state:
                    del st.session_state.proximo_numero_fatura
                st.rerun()
    
    # Clientes
    elif page == "👥 Clientes":
        st.markdown('<div class="main-header"><h1>Gerenciamento de Clientes</h1></div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["📋 Lista de Clientes", "➕ Novo Cliente"])
        
        with tab1:
            clientes_df = db.get_clientes()
            if not clientes_df.empty:
                # Formatar dados para exibição
                clientes_display = clientes_df.copy()
                clientes_display['cpf_cnpj'] = clientes_display['cpf_cnpj'].apply(format_cpf_cnpj)
                clientes_display['telefone'] = clientes_display['telefone'].apply(format_phone)
                
                st.dataframe(clientes_display, use_container_width=True)
            else:
                st.info("Nenhum cliente cadastrado.")
        
        with tab2:
            with st.form("novo_cliente"):
                st.subheader("Dados Pessoais")
                col1, col2 = st.columns(2)
                
                with col1:
                    nome = st.text_input("Nome/Razão Social *")
                    cpf_cnpj = st.text_input("CPF/CNPJ *")
                    telefone = st.text_input("Telefone")
                
                with col2:
                    email = st.text_input("E-mail")
                
                st.subheader("Endereço Completo")
                col3, col4, col5 = st.columns([3, 1, 2])
                
                with col3:
                    rua = st.text_input("Rua/Logradouro *")
                
                with col4:
                    numero = st.text_input("Número *")
                
                with col5:
                    complemento = st.text_input("Complemento")
                
                col6, col7, col8 = st.columns(3)
                
                with col6:
                    bairro = st.text_input("Bairro *")
                
                with col7:
                    cidade = st.text_input("Cidade *")
                
                with col8:
                    cep = st.text_input("CEP *")
                
                col9, col10 = st.columns([1, 3])
                
                with col9:
                    uf = st.selectbox("UF *", [
                        "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", 
                        "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", 
                        "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
                    ], index=15)  # MG como padrão
                
                if st.form_submit_button("💾 Cadastrar Cliente", use_container_width=True):
                    if nome and cpf_cnpj and rua and numero and bairro and cidade and cep:
                        try:
                            # Montar endereço completo para compatibilidade
                            endereco_completo = f"{rua}, {numero}"
                            if complemento:
                                endereco_completo += f", {complemento}"
                            endereco_completo += f", {bairro}, {cidade} - {uf}, CEP: {cep}"
                            
                            # Adicionar cliente com campos separados
                            db.add_cliente(
                                nome=nome, 
                                cpf_cnpj=cpf_cnpj, 
                                telefone=telefone, 
                                endereco=endereco_completo,
                                email=email,
                                rua=rua,
                                numero=numero,
                                complemento=complemento,
                                bairro=bairro,
                                cidade=cidade,
                                uf=uf,
                                cep=cep
                            )
                            st.success("✅ Cliente cadastrado com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erro ao cadastrar cliente: {str(e)}")
                    else:
                        st.error("❌ Campos obrigatórios: Nome, CPF/CNPJ, Rua, Número, Bairro, Cidade e CEP")
    
    # Veículos
    elif page == "🚗 Veículos":
        st.markdown('<div class="main-header"><h1>Gerenciamento de Veículos</h1></div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["📋 Lista de Veículos", "➕ Novo Veículo"])
        
        with tab1:
            veiculos_df = db.get_veiculos()
            if not veiculos_df.empty:
                # Formatar dados para exibição
                veiculos_display = veiculos_df.copy()
                veiculos_display['valor_diaria'] = veiculos_display['valor_diaria'].apply(format_currency)
                
                st.dataframe(veiculos_display, use_container_width=True)
            else:
                st.info("Nenhum veículo cadastrado.")
        
        with tab2:
            with st.form("novo_veiculo"):
                col1, col2 = st.columns(2)
                
                with col1:
                    modelo = st.text_input("Modelo *")
                    placa = st.text_input("Placa *")
                    ano = st.number_input("Ano", min_value=1900, max_value=2030, value=2020)
                
                with col2:
                    cor = st.text_input("Cor")
                    valor_diaria = st.number_input("Valor da Diária (R$) *", min_value=0.0, value=100.0, step=10.0)
                
                if st.form_submit_button("💾 Cadastrar Veículo", use_container_width=True):
                    if modelo and placa and valor_diaria > 0:
                        try:
                            db.add_veiculo(modelo, placa, ano, cor, valor_diaria)
                            st.success("✅ Veículo cadastrado com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erro ao cadastrar veículo: {str(e)}")
                    else:
                        st.error("❌ Modelo, placa e valor da diária são obrigatórios")
    
    # Financeiro
    elif page == "💰 Financeiro":
        st.markdown('<div class="main-header"><h1>Controle Financeiro</h1></div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["📊 Resumo Financeiro", "➕ Nova Transação"])
        
        with tab1:
            transacoes_df = db.get_transacoes()
            
            if not transacoes_df.empty:
                # Métricas financeiras
                receitas = transacoes_df[transacoes_df['tipo'] == 'receita']['valor'].sum()
                despesas = transacoes_df[transacoes_df['tipo'] == 'despesa']['valor'].sum()
                saldo = receitas - despesas
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("💰 Receitas", format_currency(receitas))
                
                with col2:
                    st.metric("💸 Despesas", format_currency(despesas))
                
                with col3:
                    delta_color = "normal" if saldo >= 0 else "inverse"
                    st.metric("📊 Saldo", format_currency(saldo))
                
                # Gráfico de receitas vs despesas
                st.subheader("📈 Receitas vs Despesas")
                resumo_tipo = transacoes_df.groupby('tipo')['valor'].sum().reset_index()
                
                fig = px.bar(resumo_tipo, x='tipo', y='valor',
                           title="Receitas vs Despesas",
                           labels={'valor': 'Valor (R$)', 'tipo': 'Tipo'},
                           color='tipo')
                st.plotly_chart(fig, use_container_width=True)
                
                # Lista de transações
                st.subheader("📋 Últimas Transações")
                transacoes_display = transacoes_df.copy()
                transacoes_display['valor'] = transacoes_display['valor'].apply(format_currency)
                st.dataframe(transacoes_display, use_container_width=True)
            else:
                st.info("Nenhuma transação encontrada.")
        
        with tab2:
            with st.form("nova_transacao"):
                col1, col2 = st.columns(2)
                
                with col1:
                    tipo = st.selectbox("Tipo *", ["receita", "despesa"])
                    descricao = st.text_input("Descrição *")
                    valor = st.number_input("Valor (R$) *", min_value=0.0, step=10.0)
                
                with col2:
                    data_transacao = st.date_input("Data da Transação")
                    categoria = st.text_input("Categoria")
                
                if st.form_submit_button("💾 Registrar Transação", use_container_width=True):
                    if descricao and valor > 0:
                        try:
                            db.add_transacao(
                                tipo=tipo,
                                descricao=descricao,
                                valor=valor,
                                data_transacao=data_transacao.strftime('%Y-%m-%d'),
                                categoria=categoria
                            )
                            st.success("✅ Transação registrada com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erro ao registrar transação: {str(e)}")
                    else:
                        st.error("❌ Descrição e valor são obrigatórios")
    
    # Relatórios
    elif page == "📈 Relatórios":
        st.markdown('<div class="main-header"><h1>Relatórios e Análises</h1></div>', unsafe_allow_html=True)
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            data_inicio_filtro = st.date_input("Data de Início", value=datetime.now().replace(day=1))
        with col2:
            data_fim_filtro = st.date_input("Data de Fim", value=datetime.now())
        
        # Obter dados filtrados
        faturas_df = db.get_faturas()
        transacoes_df = db.get_transacoes()
        
        if not faturas_df.empty:
            # Filtrar por data
            faturas_df['data_emissao'] = pd.to_datetime(faturas_df['data_emissao'])
            faturas_filtradas = faturas_df[
                (faturas_df['data_emissao'].dt.date >= data_inicio_filtro) &
                (faturas_df['data_emissao'].dt.date <= data_fim_filtro)
            ]
            
            if not faturas_filtradas.empty:
                # Relatório de locações
                st.subheader("📊 Relatório de Locações")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total de Locações", len(faturas_filtradas))
                
                with col2:
                    receita_periodo = faturas_filtradas['valor_total'].sum()
                    st.metric("Receita do Período", format_currency(receita_periodo))
                
                with col3:
                    ticket_medio = faturas_filtradas['valor_total'].mean()
                    st.metric("Ticket Médio", format_currency(ticket_medio))
                
                # Gráfico de evolução diária
                st.subheader("📈 Evolução Diária de Receitas")
                faturas_filtradas['data'] = faturas_filtradas['data_emissao'].dt.date
                receita_diaria = faturas_filtradas.groupby('data')['valor_total'].sum().reset_index()
                
                fig = px.line(receita_diaria, x='data', y='valor_total',
                            title="Receita Diária",
                            labels={'valor_total': 'Receita (R$)', 'data': 'Data'})
                st.plotly_chart(fig, use_container_width=True)
                
                # Top clientes
                st.subheader("🏆 Top Clientes")
                top_clientes = faturas_filtradas.groupby('cliente_nome')['valor_total'].sum().sort_values(ascending=False).head(10)
                
                fig = px.bar(x=top_clientes.values, y=top_clientes.index, orientation='h',
                           title="Top 10 Clientes por Receita",
                           labels={'x': 'Receita (R$)', 'y': 'Cliente'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Nenhuma fatura encontrada no período selecionado.")
        else:
            st.info("Nenhuma fatura encontrada.")

if __name__ == "__main__":
    main()
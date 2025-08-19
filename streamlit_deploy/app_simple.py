import streamlit as st
import pandas as pd
from datetime import datetime
import os
from database_manager import DatabaseManager

# Configuração básica da página
st.set_page_config(
    page_title="LocAuto - Sistema de Locação",
    page_icon="🚗",
    layout="wide"
)

# CSS mínimo
st.markdown("""
<style>
    .main-header {
        background: #2a5298;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar banco de dados
@st.cache_resource
def init_database():
    try:
        db_manager = DatabaseManager()
        return db_manager
    except Exception as e:
        st.error(f"Erro ao inicializar banco: {e}")
        return None

db = init_database()

def main():
    # Header
    st.markdown('<div class="main-header"><h1>🚗 LocAuto</h1></div>', unsafe_allow_html=True)
    
    # Menu simples
    page = st.sidebar.selectbox(
        "Menu",
        ["Dashboard", "Clientes", "Veículos"]
    )
    
    if page == "Dashboard":
        st.header("📊 Dashboard")
        
        if db:
            try:
                clientes_df = db.get_clientes()
                veiculos_df = db.get_veiculos()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total de Clientes", len(clientes_df))
                with col2:
                    st.metric("Total de Veículos", len(veiculos_df))
                    
            except Exception as e:
                st.error(f"Erro ao carregar dados: {e}")
        else:
            st.error("Banco de dados não disponível")
    
    elif page == "Clientes":
        st.header("👥 Clientes")
        
        if db:
            try:
                clientes_df = db.get_clientes()
                if not clientes_df.empty:
                    st.dataframe(clientes_df)
                else:
                    st.info("Nenhum cliente cadastrado")
            except Exception as e:
                st.error(f"Erro ao carregar clientes: {e}")
        else:
            st.error("Banco de dados não disponível")
    
    elif page == "Veículos":
        st.header("🚗 Veículos")
        
        if db:
            try:
                veiculos_df = db.get_veiculos()
                if not veiculos_df.empty:
                    st.dataframe(veiculos_df)
                else:
                    st.info("Nenhum veículo cadastrado")
            except Exception as e:
                st.error(f"Erro ao carregar veículos: {e}")
        else:
            st.error("Banco de dados não disponível")

if __name__ == "__main__":
    main()
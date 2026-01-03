import streamlit as st
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.library_manager import (
    load_default_data, 
    process_dataframe
)

from components.books.analysis import render_analysis_tab
from components.books.management import render_management_tab
from components.books.mural import render_mural_tab
from components.books.input import render_input_tab
from components.books.table import render_table_tab

st.set_page_config(page_title="Leitura Pro: Gestão Completa", page_icon="📚", layout="wide")

st.sidebar.title("🎲 Configuração")
data_source = st.sidebar.radio("Fonte de Dados:", ["Padrão (Sistema)", "Upload Manual (CSV)"])

df = None
if data_source == "Padrão (Sistema)":
    df = load_default_data()
    if df is None:
        st.error("❌ Arquivo não encontrado.")
else:
    uploaded_file = st.sidebar.file_uploader("Upload CSV", type="csv")
    if uploaded_file:
        raw_df = pd.read_csv(uploaded_file)
        df, missing = process_dataframe(raw_df)
        if df is None:
            st.error(f"Faltam colunas: {missing}")

if df is None:
    st.info("Selecione os dados na barra lateral.")
    st.stop()

color_map_tipo = {
    "Técnico": "#2E86C1",      # Azul Forte
    "Não Técnico": "#E67E22"   # Laranja Vibrante
}

st.title("📚 Histórico de Leitura Inteligente")

tabs = ["📋 Tabela", "🖼️ Mural", "📊 Análise", "🔄 Gestão", "➕ Nova Leitura"]
tab_tabela, tab_mural, tab_analise, tab_gestao, tab_nova = st.tabs(tabs)

with tab_tabela:
    render_table_tab(df)

with tab_mural:
    render_mural_tab(df)

with tab_analise:
    render_analysis_tab(df, color_map_tipo)

with tab_gestao:
    render_management_tab(df)

with tab_nova:
    render_input_tab(df)

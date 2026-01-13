import streamlit as st
import os
import sys

# Adicionar root ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.file_system import list_files_in_dir, get_default_path
from utils.ui import render_footer

st.set_page_config(page_title="Listador de Arquivos", page_icon="📄", layout="wide")
st.title("📄 Listador de Arquivos")
st.markdown("Gera uma lista simples de arquivos contidos em uma pasta.")

# Input
default_path = get_default_path()
caminho_input = st.text_input("Caminho da Pasta", value=default_path)

if caminho_input:
    caminho_input = caminho_input.strip().strip('"').strip("'")

if st.button("Listar Arquivos 📝", type="primary"):
    if not caminho_input:
        st.warning("Por favor, insira um caminho.")
    else:
        files, report, error = list_files_in_dir(caminho_input)
        
        if error:
            st.error(f"❌ {error}")
        else:
            st.success(f"✅ Sucesso! {len(files)} arquivo(s) encontrados.")
            st.text_area("Conteúdo da Lista", report, height=300)
            
            st.download_button(
                label="⬇️ Baixar Lista (.txt)",
                data=report,
                file_name="lista_arquivos.txt",
                mime="text/plain"
            )

render_footer()

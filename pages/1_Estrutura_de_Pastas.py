import streamlit as st
import os
import sys

# Adicionar root ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.file_system import get_tree_structure, get_default_path

st.set_page_config(page_title="Estrutura de Pastas", page_icon="📁", layout="wide")
st.title("📁 Visualizador de Estrutura")
st.markdown("Visualize a hierarquia de qualquer diretório do seu sistema.")

# Input com default inteligente
default_path = get_default_path()
caminho_input = st.text_input("Caminho da Pasta", value=default_path, help="Copie e cole o caminho da pasta aqui.")

if caminho_input:
    caminho_input = caminho_input.strip().strip('"').strip("'")

if st.button("Visualizar Estrutura 🔍", type="primary"):
    if not caminho_input:
        st.warning("Por favor, insira um caminho.")
    elif not os.path.exists(caminho_input):
        st.error(f"❌ O caminho não existe: `{caminho_input}`")
    elif not os.path.isdir(caminho_input):
        st.error(f"❌ Não é uma pasta válida: `{caminho_input}`")
    else:
        st.success(f"📂 Lendo: `{os.path.abspath(caminho_input)}`")
        
        with st.spinner("Gerando árvore..."):
            estrutura = get_tree_structure(caminho_input)
            texto_estrutura = "\n".join(estrutura)
            
        st.code(texto_estrutura, language="text")
        
        st.download_button(
            label="⬇️ Baixar txt",
            data=texto_estrutura,
            file_name="estrutura_pastas.txt",
            mime="text/plain"
        )

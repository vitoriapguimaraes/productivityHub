import streamlit as st

from utils.file_system import list_files_in_dir, get_default_path
from utils.ui import render_footer, render_folder_selector

st.set_page_config(page_title="Listador de Arquivos", page_icon="📄", layout="wide")
st.title("📄 Listador de Arquivos")
st.markdown("Gera uma lista simples de arquivos contidos em uma pasta.")

# Input
default_path = get_default_path()
caminho_input = render_folder_selector("Caminho da Pasta", default_path, "folder_path")

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
                mime="text/plain",
            )

render_footer()

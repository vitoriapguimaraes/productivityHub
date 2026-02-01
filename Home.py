import streamlit as st
from utils.ui import render_footer

# Configuração da página
st.set_page_config(page_title="Utilitários Consolidados", page_icon="🛠️", layout="wide")

st.title("🛠️ Utilitários Consolidados")
st.markdown(
    """
Este aplicativo consolida diversas ferramentas úteis para o seu dia a dia, organizadas por funcionalidade:"""
)
st.info(
    "A navegação entre as ferramentas é feita através das páginas na lista abaixo ou no menu lateral."
)

st.page_link(
    "pages/1_Estrutura_de_Pastas.py",
    label="Visualizador de Estrutura .................................. Exibe a hierarquia de arquivos e pastas.",
    use_container_width=True,
)
st.page_link(
    "pages/2_Listador_de_Arquivos.py",
    label="Listador de Arquivos ....................................... Gera lista de arquivos em texto.",
    use_container_width=True,
)
st.page_link(
    "pages/3_Editor_de_PDFs.py",
    label="Editor de PDFs ......................................... Combina múltiplos arquivos PDF.",
    use_container_width=True,
)
st.page_link(
    "pages/4_PDF_para_Imagem.py",
    label="PDF para Imagem ............................................ Converte páginas de PDF em imagem.",
    use_container_width=True,
)
st.page_link(
    "pages/5_Redimensionador_Imagens.py",
    label="Redimensionador de Imagens ................................... Ajusta resolução de imagens em lote.",
    use_container_width=True,
)
st.page_link(
    "pages/6_Transcritor_de_Audio.py",
    label="Transcritor de Áudio ....................................... Transcreve áudio com IA.",
    use_container_width=True,
)
st.page_link(
    "pages/7_Doc_para_MD.py",
    label="Conversor DOCX → MD ........................................ Converte Word para Markdown.",
    use_container_width=True,
)

render_footer()

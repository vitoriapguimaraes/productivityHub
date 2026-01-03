import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Utilitários Consolidados",
    page_icon="🛠️",
    layout="wide"
)

# Título principal
st.title("🛠️ Utilitários Consolidados")
st.markdown("Bem-vindo ao seu aplicativo de utilidades unificado. Use o menu lateral para navegar entre as ferramentas disponíveis.")

# Informações gerais
st.header("Visão Geral das Ferramentas")
st.markdown("""
Este aplicativo consolida diversas ferramentas úteis para o seu dia a dia, organizadas por funcionalidade:

1.  **Visualizador de Estrutura de Pastas**: Exibe a hierarquia de arquivos e pastas de um diretório.
2.  **Listador de Arquivos**: Gera uma lista de todos os arquivos em uma pasta e salva em um arquivo de texto.
3.  **Unificador de PDFs**: Combina múltiplos arquivos PDF em um único documento.
4.  **Transcritor de Áudio e Resumo**: Transcreve arquivos de áudio e gera um resumo consolidado usando IA (OpenAI).
5.  **Conversor de PDF para Imagem**: Converte cada página de um PDF em arquivos de imagem (PNG/JPEG).
6.  **Histórico de Leitura**: Gestão completa de livros, metas e insights com IA.
7.  **Redimensionador de Imagens**: Ferramenta em lote para ajustar resolução de imagens.
""")

st.info("A navegação entre as ferramentas é feita através das páginas no menu lateral.")

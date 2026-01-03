import streamlit as st
import os
import sys

# Adicionar root ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.pdf_tools import merge_pdf_bytes

st.set_page_config(page_title="Unificador de PDFs", page_icon="🔗", layout="wide")
st.title("🔗 Unificador de PDFs")
st.markdown("Faça o upload de múltiplos arquivos PDF para combiná-los em um único documento.")

uploaded_files = st.file_uploader(
    "Escolha os arquivos PDF para unificar (em ordem)", 
    type="pdf", 
    accept_multiple_files=True
)

if uploaded_files:
    st.info(f"Arquivos selecionados: {len(uploaded_files)}")
    
    # Exibir a ordem dos arquivos
    st.subheader("Ordem de Unificação")
    file_names = [f.name for f in uploaded_files]
    st.text("\n".join([f"{i+1}. {name}" for i, name in enumerate(file_names)]))
    
    if st.button("Unificar PDFs 🚀", type="primary"):
        with st.spinner("Processando unificação..."):
            try:
                # Passa a lista de arquivos diretamente para a função utilitária
                merged_pdf = merge_pdf_bytes(uploaded_files)
                
                st.success("🎉 PDFs unificados com sucesso!")
                
                st.download_button(
                    label="⬇️ Baixar PDF Unificado",
                    data=merged_pdf,
                    file_name="pdf_unificado.pdf",
                    mime="application/pdf"
                )
                
            except Exception as e:
                st.error(f"❌ Erro na unificação: {e}")
else:
    st.warning("Por favor, carregue um ou mais arquivos PDF.")

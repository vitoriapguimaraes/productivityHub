import streamlit as st
import os
import sys

# Adicionar root ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.pdf_tools import convert_pdf_to_images_zip

st.set_page_config(page_title="PDF para Imagem", page_icon="🖼️", layout="wide")
st.title("🖼️ Conversor de PDF para Imagem")
st.markdown("Converte cada página de um arquivo PDF em imagens de alta qualidade.")

uploaded_file = st.file_uploader("Escolha um arquivo PDF", type="pdf")

if uploaded_file:
    col1, col2 = st.columns(2)
    with col1:
        formato = st.selectbox("Formato da Imagem", ["PNG", "JPEG"])
    with col2:
        dpi = st.slider("Resolução (DPI)", 72, 300, 150, 10)
        
    if st.button("Converter para Imagens 🚀", type="primary"):
        with st.spinner(f"Convertendo PDF para {formato} ({dpi} DPI)..."):
            try:
                # Ler bytes do arquivo
                pdf_bytes = uploaded_file.read()
                
                # Chamar utilitário
                zip_data, total_pages = convert_pdf_to_images_zip(pdf_bytes, formato, dpi)
                
                st.success(f"🎉 Conversão concluída! {total_pages} páginas processadas.")
                
                st.download_button(
                    label="📥 Baixar Imagens (ZIP)",
                    data=zip_data,
                    file_name=f"{os.path.splitext(uploaded_file.name)[0]}_imagens.zip",
                    mime="application/zip"
                )
                
            except Exception as e:
                st.error(f"❌ Erro durante a conversão: {e}")
else:
    st.info("📄 Por favor, carregue um arquivo PDF para começar.")
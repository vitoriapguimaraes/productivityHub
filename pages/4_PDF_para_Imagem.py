import streamlit as st
import os
import sys

# Adicionar root ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.pdf_tools import convert_pdf_to_images
from utils.ui import render_footer

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
                output_data, total_pages, ext_type = convert_pdf_to_images(pdf_bytes, formato, dpi)
                
                st.success(f"🎉 Conversão concluída! {total_pages} páginas processadas.")
                
                if ext_type == 'zip':
                    mime_type = "application/zip"
                    file_name = f"{os.path.splitext(uploaded_file.name)[0]}_imagens.zip"
                    label = "📥 Baixar Imagens (ZIP)"
                else:
                    mime_type = f"image/{ext_type}" # image/png or image/jpeg
                    # Se for jpg no retorno do util, ext_type é 'jpg', mas mime costuma ser jpeg.
                    # Mas browsers aceitam image/jpg comumente. Vamos ajustar para ser seguro.
                    if ext_type == 'jpg':
                         mime_type = "image/jpeg"
                    
                    file_name = f"{os.path.splitext(uploaded_file.name)[0]}.{ext_type}"
                    label = f"📥 Baixar Imagem ({ext_type.upper()})"

                st.download_button(
                    label=label,
                    data=output_data,
                    file_name=file_name,
                    mime=mime_type
                )
                
            except Exception as e:
                st.error(f"❌ Erro durante a conversão: {e}")
else:
    st.info("📄 Por favor, carregue um arquivo PDF para começar.")

render_footer()
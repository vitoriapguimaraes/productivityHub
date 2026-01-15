"""
Instalar o Pandoc (uma vez só)

Windows
👉 https://pandoc.org/installing.html

Baixe o instalador .msi e siga o padrão

Verifique:

pandoc --version
"""

import streamlit as st
import subprocess
import os
import tempfile

st.set_page_config(page_title="Conversor DOCX → MD", page_icon="📝")

st.title("📝 Conversor de Documentos para Markdown")
st.markdown("Converta arquivos Word (.docx) para Markdown (.md) de forma rápida e automática.")

# Upload do arquivo
uploaded_file = st.file_uploader("Escolha um arquivo .docx", type="docx")

if uploaded_file is not None:
    # Salvar arquivo temporariamente
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name
    
    # Criar caminho de saída
    output_path = tmp_path.replace(".docx", ".md")
    
    # Tentar converter
    try:
        # Comando Pandoc
        result = subprocess.run(
            ["pandoc", tmp_path, "-o", output_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Ler arquivo convertido
            with open(output_path, "r", encoding="utf-8") as f:
                md_content = f.read()
            
            st.success("Conversão concluída com sucesso!")
            
            # Mostrar preview
            with st.expander("Preview do Markdown", expanded=True):
                st.markdown(md_content)
            
            # Botão de download
            st.download_button(
                label="⬇️ Baixar arquivo .md",
                data=md_content,
                file_name=os.path.basename(output_path),
                mime="text/markdown"
            )
            
        else:
            st.error("Erro ao converter o arquivo.")
            st.code(result.stderr)
            
    except FileNotFoundError:
        st.error("Pandoc não encontrado!")
        st.markdown("""
        ### ⚠️ Pandoc não está instalado
        
        Para usar esta ferramenta, você precisa instalar o **Pandoc**.
        
        **Instalação no Windows:**
        1. Baixe o instalador em: https://pandoc.org/installing.html
        2. Execute o instalador .msi
        3. Verifique a instalação com: `pandoc --version`
        """)
    
    finally:
        # Limpar arquivos temporários
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        if os.path.exists(output_path):
            os.remove(output_path)
import streamlit as st
import subprocess
import os
import tempfile
import zipfile
import io


def convert_single_docx(file_bytes, original_filename):
    """
    Converte um único arquivo DOCX para Markdown usando Pandoc.
    Retorna uma tupla (nome_arquivo_md, conteudo_md) ou lança uma exceção.
    """
    # Salvar arquivo temporariamente
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
        tmp_file.write(file_bytes)
        tmp_path = tmp_file.name

    # Criar caminho de saída
    output_path = tmp_path.replace(".docx", ".md")

    try:
        # Comando Pandoc
        result = subprocess.run(
            [
                "pandoc",
                tmp_path,
                "-f",
                "docx",
                "-t",
                "gfm",
                "--wrap=none",
                "-o",
                output_path,
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Erro no Pandoc: {result.stderr}")

        # Ler arquivo convertido
        with open(output_path, "r", encoding="utf-8") as f:
            md_content = f.read()

        # Nome do arquivo final
        original_name = os.path.splitext(original_filename)[0]
        md_filename = f"{original_name}.md"

        return md_filename, md_content

    finally:
        # Limpar arquivos temporários
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        if os.path.exists(output_path):
            os.remove(output_path)


def display_conversion_results(converted_files):
    """Exibe os resultados da conversão e botões de download."""
    if not converted_files:
        return

    st.success(
        f"Processamento concluído! {len(converted_files)} arquivo(s) convertido(s)."
    )

    # CASO 1: Apenas 1 arquivo -> Mostra preview e botão simples
    if len(converted_files) == 1:
        filename, content = converted_files[0]

        with st.expander(f"Preview: {filename}", expanded=True):
            st.markdown(content)

        st.download_button(
            label=f"⬇️ Baixar {filename}",
            data=content,
            file_name=filename,
            mime="text/markdown",
        )

    # CASO 2: Múltiplos arquivos -> Baixar ZIP
    else:
        # Criar ZIP em memória
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for fname, fcontent in converted_files:
                zf.writestr(fname, fcontent)

        zip_buffer.seek(0)

        st.download_button(
            label="⬇️ Baixar Todos (ZIP)",
            data=zip_buffer,
            file_name="arquivos_convertidos.zip",
            mime="application/zip",
        )

        # Lista de arquivos convertidos
        with st.expander("Ver lista de arquivos"):
            for fname, _ in converted_files:
                st.write(f"✅ {fname}")


def process_uploaded_files(uploaded_files):
    """Processa a lista de arquivos enviados e retorna a lista de convertidos."""
    converted_files = []

    # Barra de progresso se houver muitos arquivos
    progress_bar = None
    if len(uploaded_files) > 1:
        progress_bar = st.progress(0)

    for i, uploaded_file in enumerate(uploaded_files):
        try:
            filename, content = convert_single_docx(
                uploaded_file.getvalue(), uploaded_file.name
            )
            converted_files.append((filename, content))

        except FileNotFoundError:
            st.error("Pandoc não encontrado! Verifique a instalação.")
            break
        except Exception as e:
            st.error(f"Erro ao converter {uploaded_file.name}: {str(e)}")

        # Atualizar barra de progresso
        if progress_bar:
            progress_bar.progress((i + 1) / len(uploaded_files))

    return converted_files


def main():
    st.set_page_config(page_title="Conversor DOCX → MD", page_icon="📝")

    st.title("📝 Conversor de Documentos para Markdown")
    st.markdown(
        "Converta arquivos Word (.docx) para Markdown (.md) de forma rápida e automática."
    )

    # Inicializar chave do uploader no Session State
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0

    def reset_uploader():
        """Incrementa a chave para resetar o componente file_uploader"""
        st.session_state.uploader_key += 1

    # Upload dos arquivos
    uploaded_files = st.file_uploader(
        "Escolha seus arquivos .docx",
        type="docx",
        accept_multiple_files=True,
        key=f"uploader_{st.session_state.uploader_key}",
    )

    # Botão de limpar (só aparece se houver arquivos)
    if uploaded_files:
        st.button("🧹 Limpar arquivos carregados", on_click=reset_uploader)

        # Processar arquivos
        converted_files = process_uploaded_files(uploaded_files)

        # Exibir resultados
        display_conversion_results(converted_files)


if __name__ == "__main__":
    main()

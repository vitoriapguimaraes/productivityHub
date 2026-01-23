import streamlit as st
import tkinter as tk
from tkinter import filedialog


def select_folder_callback(key):
    root = tk.Tk()
    root.withdraw()
    root.wm_attributes("-topmost", 1)
    selected_folder = filedialog.askdirectory()
    root.destroy()

    if selected_folder:
        st.session_state[key] = selected_folder


def render_folder_selector(label, default_path, key):
    """
    Renderiza um seletor de pastas com input de texto e botão nativo.
    Retorna o caminho selecionado.
    """
    if key not in st.session_state:
        st.session_state[key] = default_path

    col1, col2 = st.columns([4, 1])

    with col1:
        path_input = st.text_input(label, key=key)

    with col2:
        st.write("")  # Spacer
        st.write("")
        st.button(
            "📂 Selecionar",
            key=f"{key}_btn",
            on_click=select_folder_callback,
            args=(key,),
        )

    if path_input:
        return path_input.strip().strip('"').strip("'")
    return path_input


def render_file_uploader(
    label, type, accept_multiple_files=False, key_prefix="uploader", help=None
):
    """
    Renderiza um file_uploader com botão de limpar integrado.
    Retorna o(s) arquivo(s) carregado(s).
    """
    # Chave para controlar o reset do uploader
    session_key = f"{key_prefix}_counter"

    if session_key not in st.session_state:
        st.session_state[session_key] = 0

    def reset_uploader():
        st.session_state[session_key] += 1

    # Componente uploader
    uploaded_files = st.file_uploader(
        label,
        type=type,
        accept_multiple_files=accept_multiple_files,
        key=f"{key_prefix}_{st.session_state[session_key]}",
        help=help,
    )

    # Botão de reset (se houver arquivos)
    if uploaded_files:
        st.button(
            "🧹 Limpar arquivos", key=f"{key_prefix}_clean_btn", on_click=reset_uploader
        )

    return uploaded_files


def render_footer():
    """
    Renderiza o footer minimalista na página principal e na sidebar.
    """
    footer_html = """
    <div style="text-align: center; color: #888; font-size: 14px; margin-top: 20px;">
        Desenvolvido por <a href="https://github.com/vitoriapguimaraes" target="_blank" style="color: #888; text-decoration: none;">github.com/vitoriapguimaraes</a>
    </div>
    """
    st.sidebar.markdown(footer_html, unsafe_allow_html=True)

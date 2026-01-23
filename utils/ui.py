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

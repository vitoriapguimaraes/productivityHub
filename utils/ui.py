import streamlit as st

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

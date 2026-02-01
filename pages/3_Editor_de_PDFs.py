import streamlit as st
import pandas as pd

from utils.pdf_tools import merge_pdf_bytes, extract_pdf_pages, split_pdf_to_zip
from utils.ui import render_footer, render_file_uploader

st.set_page_config(page_title="Ferramentas de PDF", page_icon="🔗", layout="wide")
st.title("🔗 Ferramentas de PDF")
st.markdown(
    "Utilize as abas abaixo para unificar múltiplos arquivos ou dividir/extrair páginas de um PDF."
)


def render_merge_tab():
    st.header("Unificar PDFs")
    st.markdown("Faça o upload de múltiplos arquivos PDF para combiná-los.")

    uploaded_files = render_file_uploader(
        "Escolha os arquivos PDF para unificar (em ordem)",
        type="pdf",
        accept_multiple_files=True,
        key_prefix="pdf_merger",
    )

    if not uploaded_files:
        st.info("Para começar, faça upload dos arquivos na área acima.")
        return

    # 1. criar DataFrame para interface de ordenação
    files_map = {f.name: f for f in uploaded_files}
    file_list = [
        {"Arquivo": f.name, "Ordem": i + 1} for i, f in enumerate(uploaded_files)
    ]
    df_files = pd.DataFrame(file_list)

    st.code(f"📁 {len(uploaded_files)} arquivos carregados")

    st.subheader("🔢 Definir Ordem")
    st.caption(
        """
    Para mudar a ordem, clique na célula de **Ordem** e digite o número da posição desejada. O PDF final seguirá essa numeração (crescente).
    """
    )

    edited_df = st.data_editor(
        df_files,
        column_config={
            "Arquivo": st.column_config.TextColumn("Nome do Arquivo", disabled=True),
            "Ordem": st.column_config.NumberColumn(
                "Ordem (1=Primeiro)", min_value=1, max_value=len(uploaded_files), step=1
            ),
        },
        hide_index=True,
        use_container_width=True,
        key="pdf_order_editor",
    )

    # Botão de Ação
    if st.button("Unificar PDFs nesta Ordem 🚀", type="primary"):
        # Validação de Unicidade
        if edited_df["Ordem"].duplicated().any():
            st.error(
                "❌ Erro: Existem números de ordem repetidos. Por favor, use uma sequência única (ex: 1, 2, 3...)."
            )
            return

        with st.spinner("Processando unificação..."):
            try:
                # 2. Reordenar baseada na edição do usuário
                edited_df.sort_values(by="Ordem", inplace=True)
                ordered_names = edited_df["Arquivo"].tolist()

                # 3. Recuperar objetos de arquivo
                ordered_files = [files_map[name] for name in ordered_names]

                # 4. Unificar
                merged_pdf = merge_pdf_bytes(ordered_files)

                st.success("🎉 PDFs unificados com sucesso!")

                st.download_button(
                    label="⬇️ Baixar PDF Unificado",
                    data=merged_pdf,
                    file_name="pdf_unificado.pdf",
                    mime="application/pdf",
                )

            except Exception as e:
                st.error(f"❌ Erro na unificação: {e}")


def handle_extract_pages(uploaded_file):
    st.info("Digite os números das páginas que deseja manter (ex: 1, 3-5, 8).")
    page_selection = st.text_input("Seleção de Páginas", placeholder="Ex: 1-3, 5")

    if st.button("Extrair Páginas", type="primary"):
        if not page_selection:
            st.warning("Por favor, digite as páginas que deseja extrair.")
            return

        with st.spinner("Extraindo..."):
            try:
                new_pdf = extract_pdf_pages(uploaded_file, page_selection)
                st.success("Páginas extraídas com sucesso!")
                st.download_button(
                    label="⬇️ Baixar PDF Extraído",
                    data=new_pdf,
                    file_name=f"extraido_{uploaded_file.name}",
                    mime="application/pdf",
                )
            except Exception as e:
                st.error(f"Erro: {e}")


def handle_split_pages(uploaded_file):
    st.info(
        "Isso criará um arquivo ZIP contendo cada página como um arquivo PDF separado."
    )
    if st.button("Dividir em Arquivos Individuais", type="primary"):
        with st.spinner("Dividindo..."):
            try:
                zip_bytes = split_pdf_to_zip(uploaded_file)
                st.success("PDF dividido com sucesso!")
                st.download_button(
                    label="⬇️ Baixar ZIP com Páginas",
                    data=zip_bytes,
                    file_name=f"paginas_{uploaded_file.name}.zip",
                    mime="application/zip",
                )
            except Exception as e:
                st.error(f"Erro: {e}")


def render_split_extract_tab():
    st.header("Dividir ou Extrair Páginas")
    st.markdown("Extraia páginas específicas de um PDF ou separe todas elas.")

    uploaded_single = render_file_uploader(
        "Escolha um arquivo PDF",
        type="pdf",
        accept_multiple_files=False,
        key_prefix="pdf_splitter",
    )

    if not uploaded_single:
        return

    st.write(f"📄 **Arquivo selecionado:** {uploaded_single.name}")

    mode = st.radio(
        "Selecione a ação:", ["Extrair Páginas Específicas", "Dividir Todas as Páginas"]
    )

    if mode == "Extrair Páginas Específicas":
        handle_extract_pages(uploaded_single)
    elif mode == "Dividir Todas as Páginas":
        handle_split_pages(uploaded_single)


# Main Execution
tab_unificar, tab_dividir = st.tabs(["Unificar PDFs", "Dividir / Extrair"])

with tab_unificar:
    render_merge_tab()

with tab_dividir:
    render_split_extract_tab()

render_footer()

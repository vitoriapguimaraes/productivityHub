import streamlit as st
import pandas as pd

from utils.pdf_tools import merge_pdf_bytes
from utils.ui import render_footer

st.set_page_config(page_title="Unificador de PDFs", page_icon="🔗", layout="wide")
st.title("🔗 Unificador de PDFs")
st.markdown(
    "Faça o upload de múltiplos arquivos PDF para combiná-los em um único documento."
)

uploaded_files = st.file_uploader(
    "Escolha os arquivos PDF para unificar (em ordem)",
    type="pdf",
    accept_multiple_files=True,
)

if uploaded_files:
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
        else:
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
else:
    st.warning("Por favor, carregue um ou mais arquivos PDF.")

render_footer()

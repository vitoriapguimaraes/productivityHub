import streamlit as st

import io
import zipfile

from utils.ui import render_footer
from utils.image_tools import process_image_resize


# --- HELPER FUNCTIONS ---
def render_config_section():
    """Renderiza a seção de configuração de redimensionamento."""
    st.divider()
    st.subheader("⚙️ Configuração de Redimensionamento")

    col_mode, col_val = st.columns(2)

    with col_mode:
        resize_mode = st.radio(
            "Modo de Redimensionamento:",
            ["Porcentagem (%)", "Largura Fixa (px)", "Altura Fixa (px)"],
            horizontal=True,
        )

    with col_val:
        if "Porcentagem" in resize_mode:
            val = st.slider(
                "Porcentagem do tamanho original", 1, 200, 50, 5, format="%d%%"
            )
        elif "Largura" in resize_mode:
            val = st.number_input(
                "Nova Largura (pixels)", min_value=50, value=800, step=50
            )
        else:
            val = st.number_input(
                "Nova Altura (pixels)", min_value=50, value=600, step=50
            )
    return resize_mode, val


def render_results_section(processed_images):
    """Renderiza a seção de resultados e downloads."""
    if not processed_images:
        return

    st.success(f"✅ {len(processed_images)} imagens processadas com sucesso!")

    # Opção de Download ZIP
    if len(processed_images) > 1:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for p_img in processed_images:
                zip_file.writestr(p_img["name"], p_img["data"])

        st.download_button(
            label="📦 Baixar Todas (ZIP)",
            data=zip_buffer.getvalue(),
            file_name="imagens_redimensionadas.zip",
            mime="application/zip",
            type="primary",
        )

    st.divider()
    st.subheader("👀 Pré-visualização")

    # Grid de Imagens
    cols = st.columns(3)
    for idx, p_img in enumerate(processed_images):
        with cols[idx % 3]:
            st.image(p_img["data"], caption=f"{p_img['name']} ({p_img['dims']})")
            st.download_button(
                label="⬇️ Baixar",
                data=p_img["data"],
                file_name=p_img["name"],
                mime=p_img["type"],
                key=f"btn_{idx}",
            )


# --- MAIN UI ---
st.set_page_config(
    page_title="Redimensionador de Imagens", page_icon="🖼️", layout="wide"
)

st.title("🖼️ Redimensionador de Imagens em Lote")
st.markdown("Reduza ou aumente a resolução das suas imagens de forma rápida e prática.")

# --- UPLOAD ---
uploaded_files = st.file_uploader(
    "Arraste suas imagens aqui (JPG, PNG, WEBP)",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=True,
)


if uploaded_files:
    # 1. Configuração
    resize_mode, val = render_config_section()

    # 2. Processamento
    if st.button("Processar Imagens 🚀", type="primary"):
        processed_images = []
        progress_bar = st.progress(0)

        for i, up_file in enumerate(uploaded_files):
            try:
                # Processar imagem usando utilitário
                byte_im, dims, fmt = process_image_resize(up_file, resize_mode, val)

                processed_images.append(
                    {
                        "name": f"{up_file.name}",
                        "data": byte_im,
                        "type": f"image/{fmt.lower()}",
                        "dims": dims,
                    }
                )

            except Exception as e:
                st.error(f"Erro ao processar {up_file.name}: {e}")

            progress_bar.progress((i + 1) / len(uploaded_files))

        progress_bar.empty()

        # 3. Resultados
        render_results_section(processed_images)

render_footer()

import streamlit as st
import pandas as pd
import os
import base64
import unicodedata

def normalize_text(text):
    """Remove acentos e caracteres especiais para comparação."""
    if not isinstance(text, str):
        return ""
    # Normaliza unicode (NFD) e remove caracteres não-ASCII (acentos)
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn').lower()

def render_mural_tab(df):
    st.subheader("🖼️ Mural (Visual)")
    st.markdown("Visualize suas capas em destaque.")
    
    PLACEHOLDER_IMG = "https://placehold.co/300x450/e0e0e0/333333?text=Sem+Capa"
    
    # --- 1. SETUP DE IMAGENS ---
    base_dir = os.getcwd()
    covers_dir = os.path.join(base_dir, "assets", "book_covers")
    
    files_map = {}
    if os.path.exists(covers_dir):
        files = os.listdir(covers_dir)
        # Mapeia: nome_normalizado -> nome_real_arquivo
        # Ex: "codigo limpo" -> "Código Limpo.jpg"
        for f in files:
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                name_norm = normalize_text(f.split('.')[0])
                files_map[name_norm] = f

    # --- 2. LÓGICA DE FILTRAGEM ---
    # Container de filtros no topo
    with st.container(border=True):
        c_search, c_stat = st.columns([3, 1])
        search_term = c_search.text_input("🔍 Buscar no Mural", key="mural_search")
        status_filter = c_stat.multiselect("Status", options=sorted(df['Status_Label'].unique()), key="mural_status")
    
    df_display = df.copy()
    
    # Filtro Texto
    if search_term:
        q = search_term.lower()
        df_display = df_display[
            df_display['Título'].astype(str).str.lower().str.contains(q) | 
            df_display['Autor'].astype(str).str.lower().str.contains(q)
        ]
        
    # Filtro Status
    if status_filter:
        df_display = df_display[df_display['Status_Label'].isin(status_filter)]

    # --- 3. PREPARAÇÃO DOS DADOS (MATCHING) ---
    def get_image_path(row):
        title = str(row['Título'])
        # Tenta várias normalizações
        # 1. Normalizado direto (ex: "Épico" -> "epico")
        t_norm = normalize_text(title).strip()
        
        # 2. Com underline (ex: "clean code" -> "clean_code")
        t_under = t_norm.replace(" ", "_")
        
        # Busca no mapa
        filename = None
        if t_norm in files_map:
            filename = files_map[t_norm]
        elif t_under in files_map:
            filename = files_map[t_under]
            
        if filename:
            return os.path.join(covers_dir, filename)
        return None

    # Aplica matching
    df_display['ImgPath'] = df_display.apply(get_image_path, axis=1)
    
    # --- 4. DEBUG & STATS ---
    total_imgs = df_display['ImgPath'].count() # count ignora None? Nao, path é string ou None
    total_imgs = df_display['ImgPath'].notna().sum()
    
    st.caption(f"📚 Livros listados: **{len(df_display)}** | 🖼️ Capas encontradas: **{total_imgs}**")
    
    if len(df_display) == 0:
        st.warning("Nenhum livro encontrado.")
        return

    # --- 5. RENDERIZAÇÃO EM CARDS ---
    # Função auxiliar para ler bits (cacheado seria melhor, mas leitura local é rapida)
    def get_img_bytes(path):
        if not path: return PLACEHOLDER_IMG
        try:
            with open(path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
            return f"data:image/jpeg;base64,{encoded}"
        except: return PLACEHOLDER_IMG

    # Iterar e criar Cards
    for _, row in df_display.sort_values("Nota", ascending=False).iterrows():
        with st.container(border=True):
            cols = st.columns([1, 4])
            
            # Coluna Imagem
            with cols[0]:
                img_src = get_img_bytes(row['ImgPath'])
                # Usando HTML para controle total do tamanho se st.image nao ficar bom, 
                # mas st.image com use_column_width deve bastar para preencher a col[0]
                st.image(img_src, width=150) 
            
            # Coluna Info
            with cols[1]:
                # Topo: Título e Nota
                c_head, c_badge = st.columns([3, 1])
                c_head.subheader(f"📖 {row['Título']}")
                
                if pd.notna(row.get('Nota')) and row['Nota'] > 0:
                    c_badge.markdown(f"### ⭐ {int(row['Nota'])}")
                
                st.markdown(f"**Autor:** {row['Autor']} | **Ano:** {int(row.get('Ano', 0) or 0)}")
                
                # Tags
                st.markdown(f"`{row['Categoria']}` • `{row['Tipo']}` • `{row.get('Status_Label')}`")
                
                # Motivação / Detalhes
                if pd.notna(row.get('Motivacao')):
                    st.info(f"💡 {row['Motivacao']}")
                
                # Footer com Prioridade/Ordem
                ft_txt = []
                if pd.notna(row.get('Prioridade')): ft_txt.append(f"Prioridade: {row['Prioridade']}")
                if pd.notna(row.get('#')): ft_txt.append(f"Ordem: #{int(row['#'])}")
                
                if ft_txt:
                    st.caption(" • ".join(ft_txt))

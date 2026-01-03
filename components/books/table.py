import streamlit as st

def render_table_tab(df):
    st.subheader("📋 Master Table & Filtros")
    
    with st.container():
        c_search, c_cat = st.columns([2, 1])
        search_term = c_search.text_input("🔍 Buscar por Título ou Autor", placeholder="Digite algo...")
        cats_filter = c_cat.multiselect("Categorias", options=sorted(df['Categoria'].dropna().unique()))
        
        c_f1, c_f2, c_f3 = st.columns(3)
        status_filter = c_f1.multiselect("Status", options=sorted(df['Status_Label'].unique()))
        prio_filter = c_f2.multiselect("Prioridade", options=sorted(df['Prioridade'].dropna().unique()))
        
        valid_years = df['Ano'][df['Ano'] > 0]
        if not valid_years.empty:
            min_y, max_y = int(valid_years.min()), int(valid_years.max())
            year_range = c_f3.slider("Ano de Publicação", min_y, max_y, (min_y, max_y))
        else:
            year_range = None
                
    # --- LÓGICA DE FILTRAGEM ---
    df_filtered = df.copy()
    
    # 1. Texto (Título ou Autor)
    if search_term:
        query = search_term.lower()
        df_filtered = df_filtered[
            df_filtered['Título'].astype(str).str.lower().str.contains(query) | 
            df_filtered['Autor'].astype(str).str.lower().str.contains(query)
        ]
        
    # 2. Categoria
    if cats_filter:
        df_filtered = df_filtered[df_filtered['Categoria'].isin(cats_filter)]
        
    # 3. Status
    if status_filter:
        df_filtered = df_filtered[df_filtered['Status_Label'].isin(status_filter)]
        
    # 4. Prioridade
    if prio_filter:
        df_filtered = df_filtered[df_filtered['Prioridade'].isin(prio_filter)]
        
    # 5. Ano
    if year_range:
        df_filtered = df_filtered[
            (df_filtered['Ano'] >= year_range[0]) & 
            (df_filtered['Ano'] <= year_range[1])
        ]
        
    # --- EXIBIÇÃO ---
    st.caption(f"Mostrando {len(df_filtered)} livros")
    
    # Colunas para mostrar (esconde IDs internos se necessário, mas mostra Status real)
    # Garante que '#' seja a primeira se existir
    all_cols = [c for c in df.columns if c not in ['Lido_em_DT', 'Score', 'Status']]
    if "#" in all_cols:
        all_cols.remove("#")
        cols_to_show = ["#"] + all_cols
    else:
        cols_to_show = all_cols
    
    # Lógica de Ordenação
    # Se filtrou apenas "A Ler", ordena pela coluna "#" (Ordem de Leitura)
    if status_filter == ["A Ler"] and "#" in df_filtered.columns:
        df_sorted = df_filtered[cols_to_show].sort_values("#", ascending=True)
    else:
        # Padrão: Ordena por Nota (Melhores primeiro) ou # se existir
        sort_col = "Nota" if "Nota" in df_filtered.columns else "Título"
        df_sorted = df_filtered[cols_to_show].sort_values(sort_col, ascending=False)
        
    st.dataframe(
        df_sorted, 
        use_container_width=True,
        column_config={
            "#": st.column_config.NumberColumn(
                "Ordem",
                format="%d"
            ),
            "Nota": st.column_config.NumberColumn(
                "Nota",
                help="Sua avaliação de 1 a 5",
                format="%d ⭐"  # Formata como inteiro com estrela
            )
        }
    )

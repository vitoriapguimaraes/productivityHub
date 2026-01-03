import streamlit as st
from utils.library_manager import get_book_details_ai, save_new_book, CATEGORIES_MAP

def render_input_tab(df):
    st.subheader("➕ Adicionar Livro à Lista")
    st.markdown("Preencha o título e disponibilidade, depois use a IA para completar!")
    
    with st.form("new_book_form"):
        # 1. Dados Básicos (Manual)
        c_tit, c_disp = st.columns([3, 1])
        title = c_tit.text_input("Título do Livro")
        
        # Opções de disponibilidade existentes + padrão
        avail_options = sorted(df['Disponivel'].dropna().unique().tolist())
        if "Estante" not in avail_options: avail_options.append("Estante")
        if "Kindle" not in avail_options: avail_options.append("Kindle")
        if "NA" not in avail_options: avail_options.append("NA")
        # Remove duplicatas e ordena
        avail_options = sorted(list(set(avail_options)))
        
        disponivel = c_disp.selectbox("Disponível em", avail_options, index=0)

        # 2. Botão IA
        suggest = st.form_submit_button("Completar com IA ✨")
        
        details = {}
        if suggest and title:
            with st.spinner("Consultando IA..."):
                details = get_book_details_ai(title)
        
        # 3. Dados Detalhados
        col_a, col_b = st.columns(2)
        with col_a:
            author = st.text_input("Autor", value=details.get("Autor", ""))
            year = st.text_input("Ano (pub.)", value=details.get("Ano (pub.)", ""))
            tipo = st.selectbox("Tipo", ["Técnico", "Não Técnico"], index=0 if details.get("Tipo")=="Técnico" else 1)
        with col_b:
            # Lista unificada de Categorias
            existing_cats = set(df['Categoria'].dropna().unique())
            system_cats = set(CATEGORIES_MAP.keys())
            all_cats = sorted(list(existing_cats.union(system_cats)))
            
            # Tenta selecionar o que veio da IA ou Default
            default_cat_idx = 0
            ai_cat = details.get("Categoria", "")
            if ai_cat and ai_cat in all_cats:
                default_cat_idx = all_cats.index(ai_cat)
            
            cat = st.selectbox("Categoria", all_cats, index=default_cat_idx)
            
            prio = st.selectbox("Prioridade", ["1 - Baixa", "2 - Média", "3 - Média-Alta", "4 - Alta"], index=3)
            status = st.selectbox("Status", ["A Ler", "Lendo", "Lido"], index=0)
            
        # Se for LIDO, pedir Nota e Data
        nota_input = None
        data_input = None
        if status == "Lido":
            c_nota, c_data = st.columns(2)
            with c_nota:
                nota_input = st.slider("Sua Nota (1-5)", 1, 5, 4)
            with c_data:
                data_input = st.text_input("Data de Leitura (AAAA/MM)", value="2025/01")
            
        motivacao = st.text_area("Motivação", value=details.get("Motivação", ""))
        
        submit = st.form_submit_button("Salvar Livro 💾")
        
        if submit:
            if not title or not author:
                st.error("Título e Autor são obrigatórios.")
            else:
                status_map_rev = {"Lido": 0, "A Ler": 1, "Lendo": 2}
                new_data = {
                    "Título": title,
                    "Autor": author,
                    "Ano": year,
                    "Tipo": tipo,
                    "Prioridade": prio,
                    "Status": status_map_rev[status],
                    "Categoria": cat,
                    "Motivacao": motivacao,
                    "Disponivel": disponivel,
                    "Nota": nota_input if status == "Lido" else None,
                    "Data_Leitura": data_input if status == "Lido" else None,
                    "Score": 0 # Será calculado automaticamente
                }
                success, msg = save_new_book(new_data)
                if success:
                    st.success(msg)
                    st.balloons()
                else:
                    st.warning(msg)

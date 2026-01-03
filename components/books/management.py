import streamlit as st
import pandas as pd
from utils.library_manager import update_book_status, delete_book

def render_management_tab(df):
    st.subheader("🔄 Gerenciar Leitura")
    st.caption("Atualize o status dos seus livros aqui.")
    
    col_filter, col_act = st.columns([1, 2])
    
    with col_filter:
        status_filter = st.radio("Filtrar por Status:", ["A Ler", "Lendo", "Lido"], index=1)
        books_filtered = df[df['Status_Label'] == status_filter]['Título'].unique()
        selected_book = st.selectbox("Selecione o Livro:", books_filtered)
    
    with col_act:
        if selected_book:
            # Recuperar info atual
            row = df[df['Título'] == selected_book].iloc[0]
            
            # --- PREVIEW RICO ---
            with st.container(border=True):
                st.markdown(f"**📖 {row['Título']}**")
                st.caption(f"Autor: {row['Autor']} • Ano: {int(row.get('Ano', 0) or 0)}")
                
                # Métricas principais para decisão
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Categoria", row['Categoria'])
                m2.metric("Prioridade", row.get('Prioridade', '-'))
                
                # Ordem (#)
                val_ordem = row.get('#')
                if pd.notna(val_ordem):
                    m3.metric("Ordem Planejada", f"#{int(val_ordem)}")
                else:
                    m3.metric("Ordem", "-")
                
                # Se tiver índice calculado (Score)
                score_val = row.get('Score', 0)
                m4.metric("Índice (Score)", f"{score_val:.1f}", help="Cálculo baseado em prioridade, ano e tipo.")
                
                if row.get('Motivacao') and str(row['Motivacao']) != "nan":
                    st.info(f"💡 **Motivação:** {row['Motivacao']}")
                
                # Se já foi lido, mostra nota
                val_nota = row.get('Nota')
                if pd.notna(val_nota) and val_nota > 0:
                    st.write(f"⭐ **Sua Nota:** {int(val_nota)}/5")
            
            with st.form("update_status_form"):
                new_status = None
                
                # LÓGICA DE TRANSIÇÃO
                if status_filter == "A Ler":
                    st.write("➡️ Mover para **Lendo**")
                    new_disp = st.text_input("Disponivel em (ex: Kindle, Estante)", value=row['Disponivel'])
                    action = "Iniciar Leitura 🚀"
                    new_status = "Lendo"
                    
                elif status_filter == "Lendo":
                    st.write("➡️ Mover para **Lido**")
                    rating = st.slider("Sua Nota", 1, 5, 4)
                    end_date = st.text_input("Data Término (AAAA/MM)", value="2025/01")
                    action = "Concluir Leitura 🎉"
                    new_status = "Lido"
                
                else: # Lido
                    st.write("✏️ Editar dados de Leitura")
                    current_rating = int(float(row.get('Nota', 0) or 0))
                    if current_rating < 1: current_rating = 1
                    rating = st.slider("Sua Nota", 1, 5, current_rating)
                    action = "Atualizar Nota 💾"
                    new_status = "Lido"
                    end_date = None # Manter anterior se não editado, mas aqui simplificado para update de nota
                
                submit_upd = st.form_submit_button(action)
                
                if submit_upd:
                    if new_status == "Lendo":
                        success, msg = update_book_status(selected_book, "Lendo", new_availability=new_disp)
                    elif new_status == "Lido":
                        # Caso especial: se já era lido, é update de nota
                        d_val = end_date if status_filter == "Lendo" else None
                        success, msg = update_book_status(selected_book, "Lido", rating=rating, date=d_val)
                    
                    if success:
                        st.success(msg)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(msg)
            
            # --- ZONA DE PERIGO (Excluir) ---
            st.markdown("---")
            with st.expander("🗑️ Zona de Perigo"):
                st.warning(f"Tem certeza que deseja apagar '{selected_book}'?")
                if st.button("Sim, apagar livro permanentemente", type="primary"):
                    ok, msg = delete_book(selected_book)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

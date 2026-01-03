import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys

# Adicionar o diretório raiz ao path para conseguir importar do utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.library_manager import (
    load_default_data, 
    process_dataframe, 
    save_new_book, 
    update_book_status,
    get_book_details_ai, 
    REQUIRED_COLUMNS
)

# Tentar importar sklearn
try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import LabelEncoder
    from utils.data_manager import get_ml_ready_data
    HAS_ML = True
except ImportError:
    HAS_ML = False

# Configuração da Página
st.set_page_config(page_title="Leitura Pro: Gestão Completa", page_icon="📚", layout="wide")

# --- SIDEBAR ---
st.sidebar.title("🎲 Configuração")
data_source = st.sidebar.radio("Fonte de Dados:", ["Padrão (Sistema)", "Upload Manual (CSV)"])

df = None
if data_source == "Padrão (Sistema)":
    df = load_default_data()
    if df is None:
        st.error("❌ Arquivo não encontrado.")
else:
    uploaded_file = st.sidebar.file_uploader("Upload CSV", type="csv")
    if uploaded_file:
        raw_df = pd.read_csv(uploaded_file)
        df, missing = process_dataframe(raw_df)
        if df is None:
            st.error(f"Faltam colunas: {missing}")

if df is None:
    st.info("Selecione os dados na barra lateral.")
    st.stop()

# Configuração de Cores
color_map_tipo = {
    "Técnico": "#2E86C1",      # Azul Forte
    "Não Técnico": "#E67E22"   # Laranja Vibrante
}

# --- TABS ---
st.title("📚 Histórico de Leitura Inteligente")

tabs = ["📊 Análise", "🔄 Gestão", "🖼️ Mural", "➕ Nova Leitura", "📋 Tabela"]
tab_analise, tab_gestao, tab_mural, tab_nova, tab_tabela = st.tabs(tabs)

with tab_analise:
    # --- VISÃO GERAL COMPACTA ---
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("📚 Lidos", len(df[df['Status_Label']=='Lido']))
    with c2: st.metric("⏳ A Ler", len(df[df['Status_Label']=='A Ler']))
    with c3: st.metric("📖 Lendo", len(df[df['Status_Label']=='Lendo']))
    with c4: st.metric("🏷️ Categorias", df['Categoria'].nunique())
    
    # --- ESTATÍSTICAS DETALHADAS (Compacto) ---
    kpi_opinion, kpi_idx = st.columns(2)

    with kpi_opinion:
        st.markdown("### ⭐ Opinião")
        kpi1, kpi2, kpi3 = st.columns(3)
        if 'Nota' in df.columns:
            op_data = df[df['Nota'].notna()]['Nota']
            if not op_data.empty:
                with kpi1: st.metric("Min", f"{op_data.min():.0f}")
                with kpi2: st.metric("Méd", f"{op_data.mean():.1f}")
                with kpi3: st.metric("Max", f"{op_data.max():.0f}")

    with kpi_idx:
        st.markdown("### 🔢 Índice")
        kpi4, kpi5, kpi6 = st.columns(3)
        if 'Score' in df.columns:
            idx_data = df[df['Score'].notna()]['Score']
            if not idx_data.empty:
                with kpi4: st.metric("Min", f"{idx_data.min():.1f}")
                with kpi5: st.metric("Méd", f"{idx_data.mean():.1f}")
                with kpi6: st.metric("Max", f"{idx_data.max():.1f}")
    
    # --- ANÁLISE TEMPORAL ---
    st.markdown("### 📅 Linha do Tempo de Leitura")
    
    # Controles da Timeline
    c_view, c_gran = st.columns(2)
    timeline_view = c_view.radio("Visualizar Evolução por:", ["Geral", "Tipo", "Categoria"], horizontal=True)
    timeline_gran = c_gran.radio("Agrupar por:", ["Mês (aaaa-mm)", "Ano (aaaa)"], horizontal=True)
    
    # Filtrar apenas livros com data de leitura
    df_timeline = df.dropna(subset=['Lido_em_DT']).copy()
    
    if df_timeline.empty:
        st.info("Nenhuma data de leitura ('Lido em') encontrada para gerar a linha do tempo.")
    else:
        df_timeline = df_timeline.sort_values('Lido_em_DT')
        
        # Define formato do agrupamento
        fmt = '%Y-%m' if "Mês" in timeline_gran else '%Y'
        df_timeline['Periodo'] = df_timeline['Lido_em_DT'].dt.strftime(fmt)
        
        if timeline_view == "Geral":
            timeline_data = df_timeline.groupby('Periodo').size().reset_index(name='Quantidade')
            # Força Line Chart
            fig_time = px.line(timeline_data, x='Periodo', y='Quantidade', markers=True, title=f"Evolução de Leitura por {timeline_gran.split(' ')[0]}")
        else:
            col_group = 'Tipo' if timeline_view == "Tipo" else 'Categoria'
            timeline_data = df_timeline.groupby(['Periodo', col_group]).size().reset_index(name='Quantidade')
            
            # Cores personalizadas
            color_seq = color_map_tipo if col_group == "Tipo" else None
            
            # Força Line Chart com cores
            fig_time = px.line(
                timeline_data, x='Periodo', y='Quantidade', color=col_group, 
                markers=True, title=f"Evolução por {timeline_gran.split(' ')[0]} e {col_group}",
                color_discrete_map=color_seq
            )
        
        st.plotly_chart(fig_time, use_container_width=True)

    st.markdown("---")

    # --- ANÁLISE DE CATEGORIAS E TIPOS ---
    st.markdown("### 🏆 Top Categorias e Tipos")
    
    tab_cat, tab_tipo = st.tabs(["Por Categoria", "Por Tipo"])
    
    with tab_cat:
        c_lidos, c_total = st.columns(2)
        with c_lidos:
            st.caption("Mais Lidos (Todos)")
            top_lidos = df[df['Status_Label']=='Lido']['Categoria'].value_counts().reset_index()
            top_lidos.columns = ['Categoria', 'Qtd']
            fig_lidos = px.bar(top_lidos, x='Qtd', y='Categoria', orientation='h', title="Categorias Lidas", color='Qtd', height=600)
            fig_lidos.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_lidos, use_container_width=True)
            
        with c_total:
            st.caption("Mais Presentes na Lista (Todos)")
            top_total = df['Categoria'].value_counts().reset_index()
            top_total.columns = ['Categoria', 'Qtd']
            fig_total = px.bar(top_total, x='Qtd', y='Categoria', orientation='h', title="Categorias na Lista", color_discrete_sequence=['#ff4b4b'], height=600)
            fig_total.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_total, use_container_width=True)

    with tab_tipo:
        t_lidos, t_total = st.columns(2)
        with t_lidos:
            st.caption("Tipos Mais Lidos")
            tipo_lidos = df[df['Status_Label']=='Lido']['Tipo'].value_counts().reset_index()
            tipo_lidos.columns = ['Tipo', 'Qtd']
            fig_tipo = px.pie(tipo_lidos, names='Tipo', values='Qtd', title="Proporção de Tipos Lidos", color='Tipo', color_discrete_map=color_map_tipo)
            st.plotly_chart(fig_tipo, use_container_width=True)
            
        with t_total:
            st.caption("Distribuição Total da Lista")
            tipo_total = df['Tipo'].value_counts().reset_index()
            tipo_total.columns = ['Tipo', 'Qtd']
            fig_tipo_tot = px.pie(tipo_total, names='Tipo', values='Qtd', title="Proporção Total dos Tipos", color='Tipo', color_discrete_map=color_map_tipo)
            st.plotly_chart(fig_tipo_tot, use_container_width=True)

with tab_gestao:
    st.subheader("🔄 Gerenciar Leitura")
    st.caption("Atualize o status dos seus livros aqui.")
    
    col_filter, col_act = st.columns([1, 2])
    
    with col_filter:
        status_filter = st.radio("Filtrar por Status:", ["A Ler", "Lendo", "Lido"], index=1)
        books_filtered = df[df['Status_Label'] == status_filter]['Título'].unique()
        selected_book = st.selectbox("Selecione o Livro:", books_filtered)
    
    with col_act:
        if selected_book:
            st.info(f"Livro: **{selected_book}**")
            
            # Recuperar info atual
            row = df[df['Título'] == selected_book].iloc[0]
            st.markdown(f"**Categoria:** {row['Categoria']} | **Tipo:** {row['Tipo']}")
            
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
                    else:
                        st.error(msg)

with tab_nova:
    st.subheader("➕ Adicionar Livro à Lista")
    st.markdown("Preencha o título e deixe a IA completar o restante!")
    
    with st.form("new_book_form"):
        title = st.text_input("Título do Livro")
        suggest = st.form_submit_button("Completar com IA ✨")
        
        details = {}
        if suggest and title:
            with st.spinner("Consultando IA..."):
                details = get_book_details_ai(title)
        
        col_a, col_b = st.columns(2)
        with col_a:
            author = st.text_input("Autor", value=details.get("Autor", ""))
            year = st.text_input("Ano (pub.)", value=details.get("Ano (pub.)", ""))
            tipo = st.selectbox("Tipo", ["Técnico", "Não Técnico"], index=0 if details.get("Tipo")=="Técnico" else 1)
        with col_b:
            cat = st.text_input("Categoria", value=details.get("Categoria", ""))
            prio = st.selectbox("Prioridade", ["1 - Baixa", "2 - Média", "3 - Média-Alta", "4 - Alta"], index=3)
            status = st.selectbox("Status", ["A Ler", "Lendo", "Lido"], index=0)
        
        col_available, col_dummy = st.columns(2)
        with col_available:
            # Opções de disponibilidade existentes + opção de criar nova
            avail_options = sorted(df['Disponivel'].dropna().unique().tolist())
            if "Estante" not in avail_options: avail_options.append("Estante")
            if "Kindle" not in avail_options: avail_options.append("Kindle")
            
            disponivel = st.selectbox("Disponível em", avail_options, index=0)
            
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

with tab_tabela:
    st.subheader("📋 Master Table & Filtros")
    
    # --- FILTROS ---
    with st.container():
        c_search, c_cat = st.columns([2, 1])
        search_term = c_search.text_input("🔍 Buscar por Título ou Autor", placeholder="Digite algo...")
        cats_filter = c_cat.multiselect("Categorias", options=sorted(df['Categoria'].dropna().unique()))
        
        with st.expander("🛠️ Filtros Avançados (Status, Prioridade, Ano)"):
            c_f1, c_f2, c_f3 = st.columns(3)
            status_filter = c_f1.multiselect("Status", options=sorted(df['Status_Label'].unique()))
            prio_filter = c_f2.multiselect("Prioridade", options=sorted(df['Prioridade'].dropna().unique()))
            
            # Filtro de Ano (Range se houver anos numéricos válidos)
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
    cols_to_show = [c for c in df.columns if c not in ['Lido_em_DT', 'Score', 'Status']]
    st.dataframe(
        df_filtered[cols_to_show].sort_values("Nota", ascending=False), 
        use_container_width=True,
        column_config={
            "Nota": st.column_config.NumberColumn(
                "Nota",
                help="Sua avaliação de 1 a 5",
                format="%d ⭐"  # Formata como inteiro com estrela
            )
        }
    )

with tab_mural:
    st.subheader("🖼️ Mural de Leituras")
    st.markdown("Adicione capas em `assets/book_covers` com o **mesmo nome do livro** (ex: `1984.jpg`).")
    
    # Grid de capas
    cols = st.columns(4) # 4 colunas
    
    # Caminho das capas
    covers_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "book_covers")
    
    # Filtrar apenas livros lidos ou em progresso para não poluir, ou todos? Todos.
    books_with_cover = []
    
    if os.path.exists(covers_dir):
        files = os.listdir(covers_dir)
        # Normalizar nomes de arquivos para match fácil
        files_map = {f.split('.')[0].lower().strip(): f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))}
        
        for idx, row in df.iterrows():
            title_clean = str(row['Título']).lower().strip()
            # Tenta achar arquivo que tenha o nome do titulo
            if title_clean in files_map:
                books_with_cover.append({
                    "title": row['Título'],
                    "path": os.path.join(covers_dir, files_map[title_clean]),
                    "nota": row.get('Nota', 0)
                })
    
    if not books_with_cover:
        st.info(f"Nenhuma capa encontrada em `{covers_dir}`. Adicione imagens com o nome exato do título do livro.")
    else:
        for idx, book in enumerate(books_with_cover):
            with cols[idx % 4]:
                st.image(book["path"], use_container_width=True)
                st.caption(f"**{book['title']}**")
                if book['nota'] and book['nota'] > 0:
                    st.caption(f"{int(book['nota'])} ⭐")

import streamlit as st
import plotly.express as px

def render_analysis_tab(df, color_map_tipo):
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

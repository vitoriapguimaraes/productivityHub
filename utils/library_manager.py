import pandas as pd
import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Caminho centralizado
# Caminho Dinâmico e Robusto com Log
def find_data_file():
    base_script = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_script, "assets", "data", "lista_livros_2025.csv")
    return path

DATA_PATH = find_data_file()

REQUIRED_COLUMNS = [
    "Título", "Autor", "Ano", "Tipo", "Prioridade", "Status", "Disponivel", "Categoria", "#"
]

def get_data_path():
    return DATA_PATH

def calcular_importancia_engine(row):
    """Engine de cálculo de importância baseada na fórmula do usuário."""
    try:
        # Recupera dados com defaults seguros
        tipo = str(row.get("Tipo", "") or "")
        prio = str(row.get("Prioridade", "") or "")
        disp = str(row.get("Disponivel", "") or "")
        cat  = str(row.get("Categoria", "") or "")
        
        # Status agora é só 'Status'
        if "Status" not in row: return 0
        
        score = 0
        # Regra Tipo: Técnico ganha +4, outros +2
        score += 4 if tipo.strip() == "Técnico" else 2
        
        # Regra Disponibilidade
        score += 2 if disp.strip() == "Estante" else 0
        
        # Regra Prioridade
        prio_map = {"1 - Baixa": 1, "2 - Média": 4, "3 - Média-Alta": 7, "4 - Alta": 10}
        score += prio_map.get(prio.strip(), 0)
        
        # Regra Ano
        try:
            ano = int(row.get("Ano", 0))
            if 0 < ano <= 2005: score += 4
            elif 2006 <= ano <= 2021: score += 7
            elif ano >= 2022: score += 9
        except: pass
            
# Regra Categoria
        score += CATEGORIES_MAP.get(cat.strip(), 0)
        return score
    except: return 0

CATEGORIES_MAP = {
    "Alta Performance & Foco": 8,
    "Liderança & Pensamento Estratégico": 7,
    "Arquitetura da Mente (Mindset)": 7,
    "Artesanato de Software (Clean Code)": 6,
    "Sistemas de IA & LLMs": 9,
    "Storytelling & Visualização": 5,
    "Biohacking & Existência": 5,
    "Literatura Brasileira Clássica": 6,
    "Épicos & Ficção Reflexiva": 7,
    "Justiça Social & Interseccionalidade": 4,
    "Negócios & Estratégia": 3,
    "Liberdade Econômica & Finanças": 5,
    "Cosmologia & Fronteiras da Ciência": 8,
    "Estatística & Incerteza": 7,
    "Engenharia de ML & MLOps": 8,
    "Arquitetura de Sistemas Digitais": 5,
    "Design & UX": 3,
    "Noir & Engenharia do Mistério": 5,
    "Comunicação & Influência": 6
}

def process_dataframe(df):
    """Limpa e processa o DataFrame."""
    # Nomes já devem estar normalizados pelo script, mas mantemos strip
    df.columns = [c.strip() for c in df.columns]
    
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    # Se faltar apenas a coluna '#', podemos adicionar como vazia
    if "#" in missing:
        df["#"] = pd.NA
        missing.remove("#")
        
    if missing:
         st.warning(f"Colunas no arquivo: {list(df.columns)}")
         return None, missing
    
    status_map = {0: 'Lido', 1: 'A Ler', 2: 'Lendo'}
    df['Status_Label'] = df['Status'].fillna(1).astype(int).map(status_map)
    
    if "Data_Leitura" in df.columns:
        df['Lido_em_DT'] = pd.to_datetime(df['Data_Leitura'], format='%Y/%m', errors='coerce')
    
    if "Nota" in df.columns:
        df["Nota"] = pd.to_numeric(df["Nota"], errors='coerce').astype('Int64')
        
    # Processar coluna de Ordem (#)
    if "#" in df.columns:
        df["#"] = pd.to_numeric(df["#"], errors='coerce').astype('Int64')

    # Recalcula Score sempre
    df['Score'] = df.apply(calcular_importancia_engine, axis=1).astype(int)
    
    return df, []

@st.cache_data
def load_default_data():
    if not os.path.exists(DATA_PATH):
        st.error(f"❌ ERRO CRÍTICO: Arquivo não encontrado.")
        st.code(f"Tentando ler em: {DATA_PATH}\nCWD: {os.getcwd()}")
        return None
    df = pd.read_csv(DATA_PATH)
    df, _ = process_dataframe(df)
    return df

def save_new_book(new_row_dict):
    """Adiciona um novo livro ao CSV local, evitando duplicatas."""
    df = pd.read_csv(DATA_PATH)
    
    # 1. Verificar Duplicata (Título)
    new_title = str(new_row_dict.get("Título", "")).strip().lower()
    if new_title:
        # Check case-insensitive
        existing = df[df['Título'].astype(str).str.strip().str.lower() == new_title]
        if not existing.empty:
            return False, f"O livro '{new_row_dict.get('Título')}' já existe na lista!"

    # Garantir que as colunas novas existem no dicionário
    for col in df.columns:
        if col not in new_row_dict:
            new_row_dict[col] = None
            
    # Processa e Salva
    new_df = pd.concat([df, pd.DataFrame([new_row_dict])], ignore_index=True)
    new_df.to_csv(DATA_PATH, index=False)
    st.cache_data.clear() # Limpa o cache para recarregar com o novo dado
    return True, f"'{new_row_dict.get('Título')}' adicionado com sucesso!"

def update_book_status(title, new_status, rating=None, date=None, new_availability=None):
    """Atualiza o status e metadados de um livro."""
    df = pd.read_csv(DATA_PATH)
    
    # Encontra o índice pelo título (pode ter duplicatas, pega o primeiro)
    idx = df[df['Título'] == title].index
    if len(idx) == 0:
        return False, "Livro não encontrado."
    
    idx = idx[0]
    
    # Mapeamento Reverso de Status
    status_map_rev = {"Lido": 0, "A Ler": 1, "Lendo": 2}
    
    # Atualiza Status
    df.at[idx, 'Status'] = status_map_rev.get(new_status, df.at[idx, 'Status'])
    
    # Se virou 'Lendo', pode mudar disponibilidade
    if new_status == "Lendo" and new_availability:
        df.at[idx, 'Disponivel'] = new_availability
        
    # Se virou 'Lido', salva nota e data
    if new_status == "Lido":
        if rating is not None:
             df.at[idx, 'Nota'] = rating
        if date is not None:
             df.at[idx, 'Data_Leitura'] = date
    
    # Salva
    df.to_csv(DATA_PATH, index=False)
    st.cache_data.clear()
    return True, "Livro atualizado com sucesso!"

def delete_book(title):
    """Remove um livro do CSV local."""
    df = pd.read_csv(DATA_PATH)
    
    # Filtra removendo o titulo exato
    new_df = df[df['Título'] != title]
    
    if len(new_df) == len(df):
        return False, "Livro não encontrado para exclusão."
        
    new_df.to_csv(DATA_PATH, index=False)
    st.cache_data.clear()
    return True, f"Livro '{title}' excluído da lista."

def get_ml_ready_data(df):
    """Prepara os dados especificamente para o modelo de Machine Learning."""
    rating_col = "Nota"
    if rating_col not in df.columns:
        return pd.DataFrame(), pd.DataFrame()
        
    train_data = df[df['Status_Label'] == 'Lido'].dropna(
        subset=[rating_col, 'Categoria', 'Tipo', 'Prioridade']
    )
    
    predict_data = df[df['Status_Label'] == 'A Ler'].copy()
    
    return train_data, predict_data

def get_book_details_ai(title):
    """Usa Groq para sugerir detalhes do livro."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    
    client = Groq(api_key=api_key)
    prompt = f"""
    Dado o título do livro '{title}', sugira as seguintes informações no formato JSON:
    - Autor
    - Ano (pub.)
    - Tipo (Técnico ou Não Técnico)
    - Categoria (escolha uma: Produtividade, Liderança, IA, Data science, História/Ficção, Programação, Desenvolvimento pessoal, etc.)
    - Motivação (uma breve frase sobre o livro)
    
    Responda APENAS o JSON.
    """
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile", # Modelo rápido e capaz
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        import json
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"Erro no Groq: {e}")
        return None

import os
import tempfile
from openai import OpenAI

def transcribe_audio_file(uploaded_file, api_key):
    """
    Transcreve áudio usando OpenAI Whisper.
    Salva arquivo temporário de forma segura (Windows-compatible).
    """
    if not api_key:
        raise ValueError("Chave da API da OpenAI não fornecida.")
        
    client = OpenAI(api_key=api_key)
    
    # Cria arquivo temporário com extensão preservada
    suffix = os.path.splitext(uploaded_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name
        
    try:
        with open(tmp_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcript.text.strip()
        
    except Exception as e:
        raise Exception(f"Erro na transcrição: {str(e)}")
        
    finally:
        # Garante limpeza
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def generate_summary(text, api_key):
    """Gera resumo consolidado com GPT-4o."""
    if not api_key:
        raise ValueError("Chave da API da OpenAI não fornecida.")
        
    client = OpenAI(api_key=api_key)
    
    prompt = f"""
    Analise o seguinte texto transcrito e crie um resumo estruturado:
    1. Principais Tópicos
    2. Ações/Tarefas (se houver)
    3. Ferramentas ou Referências Citadas
    4. Conclusão Geral
    
    Texto:
    {text[:50000]}  # Limite de segurança de tokens (aprox)
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"Erro no resumo: {str(e)}")

import os

def get_tree_structure(path, prefix="", is_last=True, output_list=None, current_depth=0, max_depth=5, max_items=50):
    """
    Gera a estrutura de árvore de um diretório como uma lista de strings.
    Substitui a antiga `mostrar_estrutura_streamlit`.
    """
    if output_list is None:
        output_list = []
        
    try:
        if current_depth == 0 and not os.path.exists(path):
            return ["❌ Caminho não encontrado."]

        name = os.path.basename(path)
        connector = "└── " if is_last else "├── "
        output_list.append(prefix + connector + name)
        
        if os.path.isdir(path):
            if current_depth >= max_depth:
                return output_list

            try:
                items = sorted(os.listdir(path))
                original_count = len(items)
                
                has_hidden = False
                if original_count > max_items:
                    items = items[:max_items]
                    has_hidden = True
                
                new_prefix = prefix + ("    " if is_last else "│   ")
                
                for i, item in enumerate(items):
                    full_path = os.path.join(path, item)
                    # If we have hidden items, the last visible item is NOT the last semantically
                    is_last_item = (i == len(items) - 1) and not has_hidden
                    
                    get_tree_structure(full_path, new_prefix, is_last_item, output_list, current_depth + 1, max_depth, max_items)
                
                if has_hidden:
                    remaining = original_count - max_items
                    output_list.append(new_prefix + f"... e mais {remaining} itens ocultos")

            except PermissionError:
                output_list.append(prefix + ("    " if is_last else "│   ") + "⛔ [Acesso Negado]")
                
    except PermissionError:
        output_list.append(prefix + "    ⛔ [Acesso Negado]")
    except Exception as e:
        output_list.append(f"    ⚠️ [Erro: {e}]")
        
    return output_list

def list_files_in_dir(path):
    """
    Lista todos os arquivos de uma pasta.
    Retorna (lista_de_arquivos, texto_formatado, erro).
    """
    if not os.path.exists(path):
        return None, None, f"O caminho '{path}' não existe."
    
    if not os.path.isdir(path):
        return None, None, f"'{path}' não é um diretório válido."
    
    try:
        files = []
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            if os.path.isfile(full_path):
                files.append(item)
        
        files.sort()
        
        # Texto formatado para relatório
        report = f"📂 Lista de arquivos: {path}\n"
        report += f"🔢 Total: {len(files)}\n"
        report += "=" * 60 + "\n\n"
        report += "\n".join(files)
        
        return files, report, None
        
    except PermissionError:
        return None, None, f"Sem permissão para acessar '{path}'."
    except Exception as e:
        return None, None, f"Erro desconhecido: {e}"

def get_default_path():
    """Retorna o diretório atual de trabalho de forma segura."""
    return os.getcwd()

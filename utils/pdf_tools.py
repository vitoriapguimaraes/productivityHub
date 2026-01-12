import io
import fitz # PyMuPDF
from PyPDF2 import PdfMerger
from PIL import Image
import zipfile
import os

def merge_pdf_bytes(pdf_files):
    """
    Recebe uma lista de objetos file-like (bytes) de PDFs.
    Retorna os bytes do PDF unificado ou levanta exceção.
    """
    merger = PdfMerger()
    output_buffer = io.BytesIO()
    
    try:
        for f in pdf_files:
            # Garante que estamos no inicio do arquivo
            f.seek(0)
            merger.append(f)
            
        merger.write(output_buffer)
        merger.close()
        output_buffer.seek(0)
        return output_buffer.getvalue()
    except Exception as e:
        raise Exception(f"Erro na unificação: {str(e)}")

def convert_pdf_to_images(pdf_bytes, img_format="PNG", dpi=150):
    """
    Converte bytes de um PDF em imagens.
    Se 1 página -> retorna (img_bytes, 1, ext)
    Se >1 páginas -> retorna (zip_bytes, total_pages, 'zip')
    """
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        total_pages = doc.page_count
        
        # Se for apenas 1 página, retorna a imagem direto
        if total_pages == 1:
            page = doc[0]
            matrix = fitz.Matrix(dpi/72, dpi/72)
            pix = page.get_pixmap(matrix=matrix)
            
            img_format_lower = img_format.lower()
            
            # Tratamento especial para JPEG (remover alpha se houver)
            if img_format.upper() == 'JPEG':
                img = Image.open(io.BytesIO(pix.tobytes(img_format_lower)))
                img = img.convert('RGB')
                output_buffer = io.BytesIO()
                img.save(output_buffer, 'JPEG', quality=95)
                ext = 'jpg'
            else:
                output_buffer = io.BytesIO(pix.tobytes(img_format_lower))
                ext = 'png'
                
            output_buffer.seek(0)
            doc.close()
            return output_buffer.getvalue(), 1, ext

        # Se for mais de 1 página, cria ZIP
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for i in range(total_pages):
                page = doc[i]
                matrix = fitz.Matrix(dpi/72, dpi/72)
                pix = page.get_pixmap(matrix=matrix)
                
                # Converter para PIL
                img_data = pix.tobytes(img_format.lower())
                img = Image.open(io.BytesIO(img_data))
                
                # Salvar em buffer
                img_buffer = io.BytesIO()
                ext = img_format.lower()
                
                if img_format.upper() == 'JPEG':
                    img = img.convert('RGB')
                    img.save(img_buffer, 'JPEG', quality=95)
                    ext = 'jpg'
                else:
                    img.save(img_buffer, 'PNG')
                    ext = 'png'
                
                img_buffer.seek(0)
                file_name = f"pagina_{i+1:03d}.{ext}"
                zipf.writestr(file_name, img_buffer.read())
                
        doc.close()
        zip_buffer.seek(0)
        return zip_buffer.getvalue(), total_pages, 'zip'
        
    except Exception as e:
        raise Exception(f"Erro na conversão: {str(e)}")

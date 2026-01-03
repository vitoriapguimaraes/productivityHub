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

def convert_pdf_to_images_zip(pdf_bytes, img_format="PNG", dpi=150):
    """
    Converte bytes de um PDF em um arquivo ZIP com imagens.
    Retorna (zip_bytes, total_pages) ou levanta exceção.
    """
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        total_pages = doc.page_count
        
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
        return zip_buffer.getvalue(), total_pages
        
    except Exception as e:
        raise Exception(f"Erro na conversão: {str(e)}")

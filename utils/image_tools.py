from PIL import Image
import io


def calculate_new_dimensions(width, height, mode, value):
    """Calcula as novas dimensões baseadas no modo e valor escolhidos."""
    if "Porcentagem" in mode:
        new_w = int(width * (value / 100))
        new_h = int(height * (value / 100))
    elif "Largura" in mode:
        ratio = value / float(width)
        new_w = value
        new_h = int(height * ratio)
    else:  # Altura e outros casos
        ratio = value / float(height)
        new_h = value
        new_w = int(width * ratio)
    return new_w, new_h


def process_image_resize(image_file, mode, value):
    """
    Processa o redimensionamento de uma imagem.
    Retorna: (bytes_da_imagem, string_dimensoes, formato)
    """
    img = Image.open(image_file)
    w, h = img.size

    new_w, new_h = calculate_new_dimensions(w, h, mode, value)

    # Resize com alta qualidade (LANCZOS)
    img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # Salvar em buffer
    buf = io.BytesIO()

    # Tenta obter formato do arquivo, fallback para JPEG se incerto
    try:
        if hasattr(image_file, "type"):
            fmt = image_file.type.split("/")[-1].upper()
        else:
            fmt = img.format if img.format else "JPEG"
    except Exception:
        fmt = "JPEG"

    if fmt == "JPG":
        fmt = "JPEG"

    # Conversão segura para JPEG (remove canal alpha)
    if fmt == "JPEG" and img_resized.mode in ("RGBA", "P"):
        img_resized = img_resized.convert("RGB")

    img_resized.save(buf, format=fmt, quality=90)
    return buf.getvalue(), f"{new_w}x{new_h}", fmt

import os
import uuid
from pathlib import Path
from PIL import Image
from io import BytesIO
from fastapi import UploadFile, HTTPException, status

# Configurações
UPLOAD_DIR = Path("uploads/products")
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_IMAGE_WIDTH = 1200
MAX_IMAGE_HEIGHT = 1200


def create_upload_directory():
    """Criar diretório de upload se não existir."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def validate_image_file(file: UploadFile) -> None:
    """
    Validar arquivo de imagem.
    
    Args:
        file: Arquivo enviado
        
    Raises:
        HTTPException: Se o arquivo não é válido
    """
    # Validar extensão
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato de arquivo não permitido. Aceitos: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Validar tamanho (verificar no content-length)
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Arquivo muito grande. Máximo: 5 MB"
        )


async def save_and_optimize_image(file: UploadFile) -> str:
    """
    Salvar e otimizar imagem.
    
    Args:
        file: Arquivo de imagem
        
    Returns:
        str: Caminho relativo da imagem salva
        
    Raises:
        HTTPException: Se houver erro ao processar a imagem
    """
    try:
        # Validar arquivo
        validate_image_file(file)
        
        # Criar diretório se não existir
        create_upload_directory()
        
        # Ler arquivo
        contents = await file.read()
        
        # Validar tamanho novamente
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Arquivo muito grande. Máximo: 5 MB"
            )
        
        # Abrir imagem com Pillow
        image = Image.open(BytesIO(contents))
        
        # Converter RGBA para RGB se necessário (para JPEG)
        if image.mode in ("RGBA", "LA", "P"):
            rgb_image = Image.new("RGB", image.size, (255, 255, 255))
            rgb_image.paste(image, mask=image.split()[-1] if image.mode == "RGBA" else None)
            image = rgb_image
        
        # Redimensionar se necessário
        image.thumbnail((MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT), Image.Resampling.LANCZOS)
        
        # Gerar nome único para o arquivo
        file_extension = file.filename.split(".")[-1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Salvar imagem otimizada
        if file_extension in ("jpg", "jpeg"):
            image.save(file_path, "JPEG", quality=85, optimize=True)
        elif file_extension == "png":
            image.save(file_path, "PNG", optimize=True)
        elif file_extension == "webp":
            image.save(file_path, "WEBP", quality=85)
        
        # Retornar caminho relativo
        return f"uploads/products/{unique_filename}"
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar imagem: {str(e)}"
        )


def delete_image(image_path: str) -> None:
    """
    Deletar imagem do servidor.
    
    Args:
        image_path: Caminho da imagem
    """
    try:
        if image_path and image_path.startswith("uploads/"):
            file_path = Path(image_path)
            if file_path.exists():
                file_path.unlink()
    except Exception as e:
        print(f"Erro ao deletar imagem: {e}")

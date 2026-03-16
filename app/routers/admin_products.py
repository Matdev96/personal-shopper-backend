from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.core.admin_security import get_current_admin
from pathlib import Path
import shutil
import uuid

router = APIRouter(prefix="/admin/products", tags=["Admin - Products"])

# Diretório para uploads
UPLOAD_DIR = Path("uploads/products")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category_id: int = Form(...),
    image_url: str = Form(None),  # ✅ NOVO: URL da imagem
    image: UploadFile = File(None),  # Upload de arquivo
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Criar um novo produto com upload de imagem ou URL.
    Apenas administradores podem acessar.
    
    Args:
        name: Nome do produto
        description: Descrição do produto
        price: Preço do produto
        category_id: ID da categoria
        image_url: URL da imagem (opcional)
        image: Arquivo de imagem (opcional)
        current_admin: Admin autenticado
        db: Sessão do banco de dados
    
    Returns:
        ProductResponse: Dados do produto criado
    """
    print(f"DEBUG: Criando produto para admin: {current_admin.email}")

    # Verificar se a categoria existe
    from app.models.category import Category
    category = db.query(Category).filter(Category.id == category_id).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada",
        )
    
    # ✅ NOVO: Validar se tem imagem (URL ou arquivo)
    final_image_url = None
    
    if image_url:
        # Se tem URL, usar a URL diretamente
        final_image_url = image_url
        print(f"DEBUG: Usando URL da imagem: {image_url}")
    elif image:
        # Se tem arquivo, fazer upload
        file_extension = image.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Salvar arquivo
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        final_image_url = f"/uploads/products/{unique_filename}"
        print(f"DEBUG: Arquivo salvo em: {final_image_url}")
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Forneça uma URL ou um arquivo de imagem",
        )
    
    # Criar novo produto
    new_product = Product(
        name=name,
        description=description,
        price=price,
        category_id=category_id,
        image_url=final_image_url,
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return new_product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    name: str = Form(None),
    description: str = Form(None),
    price: float = Form(None),
    category_id: int = Form(None),
    image_url: str = Form(None),  # ✅ NOVO: URL da imagem
    image: UploadFile = File(None),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Atualizar um produto existente.
    Apenas administradores podem acessar.
    
    Args:
        product_id: ID do produto
        name: Novo nome (opcional)
        description: Nova descrição (opcional)
        price: Novo preço (opcional)
        category_id: Nova categoria (opcional)
        image_url: Nova URL da imagem (opcional)
        image: Novo arquivo de imagem (opcional)
        current_admin: Admin autenticado
        db: Sessão do banco de dados
    
    Returns:
        ProductResponse: Dados do produto atualizado
    
    Raises:
        HTTPException: Se produto não encontrado
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado",
        )
    
    # Atualizar campos
    if name:
        product.name = name
    if description:
        product.description = description
    if price:
        product.price = price
    if category_id:
        product.category_id = category_id
    
    # ✅ NOVO: Processar nova imagem (URL ou arquivo)
    if image_url:
        product.image_url = image_url
        print(f"DEBUG: Atualizando com URL: {image_url}")
    elif image:
        file_extension = image.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        product.image_url = f"/uploads/products/{unique_filename}"
        print(f"DEBUG: Atualizando com arquivo: {product.image_url}")
    
    db.commit()
    db.refresh(product)
    
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Deletar um produto.
    Apenas administradores podem acessar.
    
    Args:
        product_id: ID do produto
        current_admin: Admin autenticado
        db: Sessão do banco de dados
    
    Raises:
        HTTPException: Se produto não encontrado
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado",
        )
    
    db.delete(product)
    db.commit()
    
    return None
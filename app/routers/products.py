from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.models.product import Product
from app.models.category import Category
from app.dependencies import get_db, get_current_admin_user
from app.models.user import User
from fastapi import File, UploadFile
from app.utils.image_handler import save_and_optimize_image, delete_image

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Criar um novo produto.
    Requer autenticação e permissão de admin.
    
    Args:
        product_data: Dados do produto
        current_user: Usuário autenticado (deve ser admin)
        db: Sessão do banco de dados
        
    Returns:
        ProductResponse: Dados do produto criado
        
    Raises:
        HTTPException: Se a categoria não existe ou dados inválidos
    """
    # Verificar se a categoria existe
    category = db.query(Category).filter(Category.id == product_data.category_id).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoria com ID {product_data.category_id} não encontrada",
        )
    
    # Verificar se a categoria está ativa
    if not category.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível adicionar produtos a uma categoria inativa",
        )
    
    # Verificar se já existe um produto com o mesmo nome na mesma categoria
    existing_product = db.query(Product).filter(
        Product.name == product_data.name,
        Product.category_id == product_data.category_id,
    ).first()
    
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Já existe um produto com o nome '{product_data.name}' nesta categoria",
        )
    
    # Criar novo produto
    new_product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        size=product_data.size,
        color=product_data.color,
        category_id=product_data.category_id,
        image_url=product_data.image_url,
        stock=product_data.stock,
        is_active=True,
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return new_product


@router.get("", response_model=List[ProductResponse])
def list_products(
    skip: int = 0,
    limit: int = 10,
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
):
    """
    Listar produtos com filtros e paginação.
    
    Args:
        skip: Número de registros a pular (padrão: 0)
        limit: Número máximo de registros a retornar (padrão: 10)
        category_id: Filtrar por ID da categoria
        min_price: Preço mínimo
        max_price: Preço máximo
        in_stock: Filtrar por disponibilidade (True = em estoque, False = fora de estoque)
        search: Buscar por nome do produto
        sort_by: Campo para ordenação (created_at, price, name)
        sort_order: Ordem de classificação (asc, desc)
        db: Sessão do banco de dados
        
    Returns:
        List[ProductResponse]: Lista de produtos filtrados e paginados
    """
        # Validar parâmetros
    if skip < 0:
        skip = 0
    if limit < 1 or limit > 100:
        limit = 10
    if sort_order not in ["asc", "desc"]:
        sort_order = "desc"
    if sort_by not in ["created_at", "price", "name"]:
        sort_by = "created_at"
    
    # Construir query base - filtrar apenas produtos ativos
    query = db.query(Product).filter(Product.is_active == True)
    
    # Aplicar filtros
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    if in_stock is not None:
        if in_stock:
            query = query.filter(Product.stock > 0)
        else:
            query = query.filter(Product.stock == 0)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Product.name.ilike(search_term)) | 
            (Product.description.ilike(search_term))
        )
    
    # Aplicar ordenação
    if sort_by == "price":
        sort_column = Product.price
    elif sort_by == "name":
        sort_column = Product.name
    else:
        sort_column = Product.created_at
    
    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    
    # Aplicar paginação
    products = query.offset(skip).limit(limit).all()
    
    return products


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    """
    Obter um produto por ID.
    Endpoint público (não requer autenticação).
    
    Args:
        product_id: ID do produto
        db: Sessão do banco de dados
        
    Returns:
        ProductResponse: Dados do produto
        
    Raises:
        HTTPException: Se o produto não existe
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado",
        )
    
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Atualizar um produto.
    Requer autenticação e permissão de admin.
    
    Args:
        product_id: ID do produto
        product_data: Dados a serem atualizados
        current_user: Usuário autenticado (deve ser admin)
        db: Sessão do banco de dados
        
    Returns:
        ProductResponse: Dados atualizados do produto
        
    Raises:
        HTTPException: Se o produto não existe ou categoria não existe
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado",
        )
    
    # Verificar se a nova categoria existe (se foi fornecida)
    if product_data.category_id is not None:
        category = db.query(Category).filter(Category.id == product_data.category_id).first()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria não encontrada",
            )
        
        product.category_id = product_data.category_id
    
    # Atualizar campos (se foram fornecidos)
    if product_data.name is not None:
        product.name = product_data.name
    
    if product_data.description is not None:
        product.description = product_data.description
    
    if product_data.price is not None:
        product.price = product_data.price
    
    if product_data.size is not None:
        product.size = product_data.size
    
    if product_data.color is not None:
        product.color = product_data.color
    
    if product_data.image_url is not None:
        product.image_url = product_data.image_url
    
    if product_data.stock is not None:
        product.stock = product_data.stock
    
    if product_data.is_active is not None:
        product.is_active = product_data.is_active
    
    db.commit()
    db.refresh(product)
    
    return product

@router.post("/upload", status_code=status.HTTP_200_OK)
async def upload_product_image(
    product_id: int = Query(..., description="ID do produto"),
    file: UploadFile = File(..., description="Arquivo de imagem"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Fazer upload de imagem para um produto.
    Requer autenticação e permissão de admin.
    
    Args:
        product_id: ID do produto
        file: Arquivo de imagem (JPG, PNG, WebP)
        current_user: Usuário autenticado (deve ser admin)
        db: Sessão do banco de dados
        
    Returns:
        dict: Dados do produto atualizado com a nova imagem
        
    Raises:
        HTTPException: Se o produto não existe ou arquivo inválido
    """
    # Verificar se o produto existe
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado",
        )
    
    # Deletar imagem antiga se existir
    if product.image_url:
        delete_image(product.image_url)
    
    # Salvar e otimizar nova imagem
    image_path = await save_and_optimize_image(file)
    
    # Atualizar produto com novo caminho de imagem
    product.image_url = image_path
    db.commit()
    db.refresh(product)
    
    return {
        "message": "Imagem enviada com sucesso",
        "product": ProductResponse.model_validate(product),
    }

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Deletar um produto.
    Requer autenticação e permissão de admin.
    
    Args:
        product_id: ID do produto
        current_user: Usuário autenticado (deve ser admin)
        db: Sessão do banco de dados
        
    Raises:
        HTTPException: Se o produto não existe
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado",
        )
    
    db.delete(product)
    db.commit()
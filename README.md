# Personal Shopper — TCC

Aplicacao e-commerce fullstack desenvolvida como Trabalho de Conclusao de Curso (TCC) do curso de Analise e Desenvolvimento de Sistemas (ADS).

[![Python](https://img.shields.io/badge/Python-3.13+-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-blue)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue)](https://postgresql.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## Sobre

O **Personal Shopper** e uma plataforma de e-commerce com backend em FastAPI e frontend em React. O sistema permite que usuarios naveguem por produtos, gerenciem um carrinho de compras e realizem pedidos, enquanto administradores gerenciam o catalogo, estoque e usuarios.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Framework | FastAPI 0.115 (Python 3.13+) |
| Banco de dados | PostgreSQL 15+ |
| ORM | SQLAlchemy 2.0 |
| Autenticacao | JWT (HS256) + Bcrypt |
| Migrations | Alembic |
| Rate limiting | slowapi |
| Imagens | Pillow |
| Testes | pytest + pytest-asyncio (184 testes) |
| Frontend | React 19 + Vite 5 + Tailwind CSS v4 |
| Estado | Zustand 5 |

---

## Funcionalidades

**Autenticacao e Usuarios**
- Registro e login com JWT
- Controle de acesso por nivel (admin / usuario)
- Gerenciamento de perfil

**Catalogo de Produtos**
- Listagem com paginacao, filtros e busca
- Filtros por categoria, preco e estoque
- Upload de imagens (arquivo ou URL) com otimizacao via Pillow
- CRUD restrito a administradores

**Carrinho e Pedidos**
- Carrinho persistente por usuario
- Snapshot de preco no momento da compra
- Controle de estoque: deducao ao confirmar, restauracao ao cancelar
- Historico de pedidos com filtros

**Painel Admin**
- Dashboard com estatisticas (usuarios, produtos, pedidos, receita)
- Gerenciamento de produtos e usuarios

---

## Estrutura do Projeto

```
personal-shopper-backend/
  app/
    main.py          # Inicializacao FastAPI, CORS, routers
    database.py      # Engine SQLAlchemy, sessao, get_db
    dependencies.py  # get_current_user, get_current_admin_user
    core/
      config.py      # Settings via pydantic-settings
      security.py    # JWT e bcrypt
      limiter.py     # Rate limiting
    models/          # Modelos SQLAlchemy (tabelas)
    schemas/         # Modelos Pydantic (request/response)
    routers/         # Endpoints agrupados por recurso
    utils/
      image_handler.py
  migrations/        # Migrations Alembic
  tests/             # 184 testes com pytest
  uploads/products/  # Imagens enviadas
```

---

## Endpoints da API

Base URL: `/api/v1`

| Metodo | Rota | Auth | Descricao |
|---|---|---|---|
| POST | `/auth/register` | — | Cadastro (3 req/min) |
| POST | `/auth/login` | — | Login, retorna JWT (5 req/min) |
| GET/PUT | `/auth/me` | Usuario | Perfil do usuario logado |
| GET | `/products` | — | Listar produtos com filtros e paginacao |
| GET | `/products/{id}` | — | Detalhe do produto |
| POST/PUT/DELETE | `/products` | Admin | CRUD de produtos |
| GET/DELETE | `/categories` | —/Admin | CRUD de categorias |
| GET/POST/PUT/DELETE | `/cart` | Usuario | Gerenciar carrinho |
| GET/POST | `/orders` | Usuario | Listar e criar pedidos |
| PUT | `/orders/{id}/cancel` | Usuario | Cancelar pedido pendente |
| GET | `/admin/users` | Admin | Listar usuarios |
| GET | `/admin/users/{id}/orders` | Admin | Pedidos de um usuario |
| POST/PUT/DELETE | `/admin/products` | Admin | Gerenciar produtos |

Documentacao interativa disponivel em `/docs` (Swagger) e `/redoc`.

---

## Como Executar

### Pre-requisitos
- Python 3.13+
- PostgreSQL 15+

### Instalacao

```bash
# Clonar o repositorio
git clone https://github.com/Matdev96/personal-shopper-backend.git
cd personal-shopper-backend

# Criar e ativar ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variaveis de ambiente
cp .env.example .env
# Editar .env com as credenciais do banco

# Executar migrations
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload
```

### Testes

```bash
pytest tests/ -v
```

---

## Frontend

O frontend esta disponivel em: [personal-shopper-frontend](https://github.com/Matdev96/personal-shopper-frontend)

---

## Licenca

MIT

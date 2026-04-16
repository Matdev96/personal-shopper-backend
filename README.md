# Personal Shopper — Backend (TCC)

API REST do e-commerce Personal Shopper, desenvolvida como Trabalho de Conclusão de Curso (TCC) do curso de Análise e Desenvolvimento de Sistemas (ADS).

[![Python](https://img.shields.io/badge/Python-3.13+-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue)](https://postgresql.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## Sobre

Backend da plataforma Personal Shopper — e-commerce onde clientes navegam por produtos, gerenciam carrinho, realizam pedidos e acompanham solicitações de busca personalizadas. Administradores gerenciam o catálogo, estoque, solicitações e pagamentos.

O repositório do frontend está em: [personal-shopper-frontend](https://github.com/Matdev96/personal-shopper-frontend)

---

## Stack

| Camada | Tecnologia |
|---|---|
| Framework | FastAPI 0.115 (Python 3.13+) |
| Banco de dados | PostgreSQL 15+ |
| ORM | SQLAlchemy 2.0 |
| Autenticação | JWT (HS256) + Bcrypt |
| Migrations | Scripts SQL manuais em `migrations/` |
| Rate limiting | slowapi |
| Imagens | Pillow |
| Testes | pytest + pytest-asyncio (184 testes) |

---

## Funcionalidades

**Autenticação e Usuários**
- Registro e login com JWT
- Controle de acesso por nível (admin / usuário)
- Perfil do usuário com endereço de entrega (CEP, logradouro, número, complemento, bairro, cidade, estado)
- Preferência de entrega: endereço salvo ou retirada na loja

**Catálogo de Produtos**
- Listagem com paginação, filtros e busca por texto
- Filtros por categoria, preço e estoque
- Upload de imagens (arquivo ou URL) com otimização via Pillow
- CRUD restrito a administradores
- Resposta inclui objeto `category` aninhado

**Carrinho e Pedidos**
- Carrinho persistente por usuário (criado automaticamente)
- Snapshot de preço no momento da compra
- Controle de estoque: dedução ao confirmar, restauração ao cancelar
- Histórico de pedidos com filtros
- Suporte a endereço de entrega ou "Retirar na Loja"

**Solicitações de Busca (`ProductRequest`)**
- Cliente cria solicitação com produto, referência, loja, orçamento e tamanho
- Ciclo completo de 14 status (pendente → em_busca → ... → entregue)
- Admin cota preço, cliente confirma
- Limite de 10 solicitações abertas por usuário

**Pagamentos**
- Pagamento em duas etapas: sinal 50% + final 50%
- Cliente registra comprovante, admin confirma ou rejeita
- Integração automática com status da solicitação

**Painel Admin**
- CRUD de produtos com upload de imagem
- Gerenciamento de usuários
- Gestão completa de solicitações e pagamentos

---

## Estrutura do Projeto

```
personal-shopper-backend/
  app/
    main.py          # Inicialização FastAPI, CORS, routers
    database.py      # Engine SQLAlchemy, sessão, get_db
    dependencies.py  # get_current_user, get_current_admin_user
    core/
      config.py      # Settings via pydantic-settings (.env)
      security.py    # JWT e bcrypt
      limiter.py     # Rate limiting (slowapi)
    models/          # Modelos SQLAlchemy (9 tabelas)
    schemas/         # Modelos Pydantic (request/response)
    routers/         # Endpoints agrupados por recurso
    utils/
      image_handler.py  # Upload e otimização de imagens
  migrations/        # Scripts SQL para alterações no banco
  tests/             # 184 testes com pytest
  uploads/products/  # Imagens enviadas
```

---

## Endpoints da API

Base URL: `/api/v1`

### Autenticação e Perfil

| Método | Rota | Auth | Descrição |
|---|---|---|---|
| POST | `/auth/register` | — | Cadastro (3 req/min) |
| POST | `/auth/login` | — | Login, retorna JWT (5 req/min) |
| GET | `/auth/me` | Usuário | Dados do usuário logado |
| PUT | `/auth/me` | Usuário | Atualizar perfil e endereço de entrega |

### Catálogo, Carrinho e Pedidos

| Método | Rota | Auth | Descrição |
|---|---|---|---|
| GET | `/products` | — | Listar produtos com filtros e paginação |
| GET | `/products/{id}` | — | Detalhe do produto |
| GET/POST/PUT/DELETE | `/categories` | —/Admin | CRUD de categorias |
| GET/POST/PUT/DELETE | `/cart` e `/cart/items` | Usuário | Gerenciar carrinho |
| GET/POST | `/orders` | Usuário | Listar e criar pedidos |
| PUT | `/orders/{id}/cancel` | Usuário | Cancelar pedido pendente |
| POST | `/stock/validate` | — | Validar estoque antes do checkout |

### Solicitações e Pagamentos

| Método | Rota | Auth | Descrição |
|---|---|---|---|
| POST | `/requests` | Usuário | Criar solicitação de busca |
| GET | `/requests` | Usuário | Listar próprias solicitações |
| GET | `/requests/{id}` | Usuário | Detalhe da solicitação |
| PUT | `/requests/{id}/confirm` | Usuário | Confirmar preço cotado |
| PUT | `/requests/{id}/cancel` | Usuário | Cancelar solicitação |
| POST | `/payments` | Usuário | Registrar sinal ou pagamento final |
| GET | `/payments/my` | Usuário | Listar próprios pagamentos |

### Admin

| Método | Rota | Descrição |
|---|---|---|
| GET/DELETE | `/admin/users` | Listar e remover usuários |
| POST/PUT/DELETE | `/admin/products` | Gerenciar produtos |
| GET | `/admin/requests` | Listar todas as solicitações com filtros |
| PUT | `/admin/requests/{id}/status` | Avançar status da solicitação |
| PUT | `/admin/requests/{id}/quote` | Registrar preço cotado |
| PUT | `/admin/requests/{id}/cancel` | Cancelar qualquer solicitação |
| PUT | `/admin/requests/{id}/payments/{pid}/review` | Confirmar ou rejeitar pagamento |

Documentação interativa disponível em `/docs` (Swagger) e `/redoc`.

---

## Banco de Dados

Tabelas: `users`, `categories`, `products`, `carts`, `cart_items`, `orders`, `order_items`, `product_requests`, `payments`

Migrations são aplicadas via scripts Python na raiz do projeto:

```bash
python run_address_migration.py   # Campos de endereço nos usuários
python run_stock_migration.py     # Campo stock nos produtos
# ... outros scripts de migração
```

---

## Como Executar

### Pré-requisitos
- Python 3.13+
- PostgreSQL 15+

### Instalação

```bash
# Clonar o repositório
git clone https://github.com/Matdev96/personal-shopper-backend.git
cd personal-shopper-backend

# Criar e ativar ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com as credenciais do banco

# Aplicar migrations
python run_stock_migration.py
python run_address_migration.py

# Iniciar servidor
uvicorn app.main:app --reload
```

### Testes

```bash
pytest tests/ -v
pytest tests/ --cov=app --cov-report=html
```

---

## Frontend

O frontend (React + Vite) está em: [personal-shopper-frontend](https://github.com/Matdev96/personal-shopper-frontend)

---

## Licença

MIT

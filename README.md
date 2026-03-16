# 🛍️ Personal Shopper - E-commerce Full Stack

Um projeto de e-commerce desenvolvido com **FastAPI** (Backend) e **React** (Frontend) para a disciplina de **Análise e Desenvolvimento de Software**.

![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow)
![Python](https://img.shields.io/badge/Python-3.13+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)
![React](https://img.shields.io/badge/React-18+-61DAFB)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791)

---

## 📋 Descrição do Projeto

O **Personal Shopper** é uma plataforma de e-commerce que permite aos usuários:

- ✅ **Registrar e fazer login** com autenticação JWT
- ✅ **Navegar produtos** por categorias
- ✅ **Adicionar produtos ao carrinho** e fazer checkout
- ✅ **Visualizar pedidos** realizados
- ✅ **Gerenciar produtos** (admin)
- ✅ **Gerenciar usuários** (admin)
- ✅ **Visualizar dashboard** com estatísticas (admin)

---

## 🎯 Funcionalidades Implementadas

### **1. Autenticação e Autorização** ✅
- Registro de usuários com validação de email
- Login com JWT (JSON Web Tokens)
- Verificação de permissões (admin e usuários comuns)
- Proteção de rotas com autenticação

### **2. Gerenciamento de Usuários** ✅
- Listar todos os usuários (admin)
- Obter detalhes de um usuário específico (admin)
- Deletar usuários (admin)
- Visualizar pedidos de um usuário (admin)

### **3. Gerenciamento de Produtos** ✅
- Listar produtos com paginação
- Criar produtos com upload de imagem (arquivo ou URL)
- Atualizar produtos (admin)
- Deletar produtos (admin)
- Filtrar produtos por categoria

### **4. Gerenciamento de Categorias** ✅
- Listar categorias
- Criar categorias (admin)
- Atualizar categorias (admin)
- Deletar categorias (admin)

### **5. Carrinho de Compras** ✅
- Adicionar produtos ao carrinho
- Remover produtos do carrinho
- Atualizar quantidade de produtos
- Visualizar carrinho
- Limpar carrinho

### **6. Pedidos** ✅
- Criar pedidos (checkout)
- Listar pedidos do usuário
- Visualizar detalhes do pedido
- Listar todos os pedidos (admin)
- Calcular receita total

### **7. Estoque** ✅
- Gerenciar estoque de produtos
- Verificar disponibilidade

### **8. Dashboard Admin** ✅
- Visualizar total de usuários
- Visualizar total de produtos
- Visualizar total de pedidos
- Visualizar receita total
- Ações rápidas (gerenciar usuários, produtos, voltar para loja)

---

## 🏗️ Arquitetura do Projeto

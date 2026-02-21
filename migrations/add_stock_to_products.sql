-- Adicionar coluna 'stock' à tabela 'products'
ALTER TABLE products ADD COLUMN IF NOT EXISTS stock INTEGER DEFAULT 0 NOT NULL;
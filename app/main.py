# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Criar a aplicação FastAPI
app = FastAPI(
    title="Personal Shopper API",
    description="API para gerenciar compras de personal shopper",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rota de teste
@app.get("/")
def read_root():
    """
    Endpoint raiz da API.
    """
    return {
        "message": "Bem-vindo à API de Personal Shopper!",
        "status": "online"
    }

# Rota de health check
@app.get("/health")
def health_check():
    """
    Verifica se a API está funcionando corretamente.
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
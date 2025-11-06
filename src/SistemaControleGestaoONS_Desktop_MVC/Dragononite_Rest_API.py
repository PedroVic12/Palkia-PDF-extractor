# -*- coding: utf-8 -*-
# DRAGONITE TOOL SERVER v2.0 (POO + FastAPI + SQLite3 Nativo + Gemini Tools)
# Autor: Pedro Victor Veras (Conceito) / Lumina Aurora (Implementação)
# Descrição: Backend POO/SOLID para PySide6/ONS, focado em alta performance.

import os
import sys
import sqlite3
import json
import smtplib
from email.mime.text import MIMEText
from fastapi import FastAPI, Depends, HTTPException, APIRouter, status, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from datetime import datetime
import time
import requests
# NOTA: Instalar 'google-genai' ou usar requests para API (mantendo compatibilidade)

# --- 1. CONFIGURAÇÃO DE AMBIENTE ---
DATABASE_FILE = 'database/dragonite.db'
os.makedirs(os.path.dirname(DATABASE_FILE), exist_ok=True)
BASE_URL = "/api" # Prefixo padrão para APIs
STATIC_DIR = "static" # Diretório para o Frontend (PySide6/Iframe)

# --- MODELOS Pydantic (SOLID - Lógica de Negócio) ---

class ClientBase(BaseModel):
    """Modelo base para dados de cliente."""
    nome: str
    email: EmailStr
    telefone: str | None = None

class ClientCreate(ClientBase):
    """Modelo para criação (todos campos obrigatórios)."""
    pass

class ClientDB(ClientBase):
    """Modelo para o retorno do banco de dados."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- 2. SERVIÇOS/DEPENDÊNCIAS (SOLID - Princípio da Inversão de Dependência) ---

class DatabaseManager:
    """Gerencia todas as operações com o banco de dados SQLite3 nativo."""
    def __init__(self):
        self._create_tables()

    def _get_conn(self):
        """Cria e retorna uma conexão com o banco."""
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_tables(self):
        """Cria a tabela de 'clients' se ela não existir."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                telefone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        print("✅ Tabela 'clients' (SQLite3 Nativo) inicializada.")

    def create_client(self, client: ClientCreate):
        """Cria um novo cliente (C do CRUD)."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO clients (nome, email, telefone) VALUES (?, ?, ?)",
                (client.nome, client.email, client.telefone)
            )
            conn.commit()
            conn.close()
            return client.model_dump(exclude_unset=True) # Retorna os dados criados
        except sqlite3.IntegrityError:
            conn.close()
            raise HTTPException(status_code=409, detail="Email já cadastrado.")

    def get_clients(self):
        """Retorna todos os clientes (R do CRUD)."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients ORDER BY nome")
        clients = [ClientDB(**dict(row)) for row in cursor.fetchall()]
        conn.close()
        return clients

class EmailService:
    """Gerencia o disparo de emails (Tool 1)."""

    def send_email(self, to_email: str, subject: str, body: str):
        """Simula o envio de email."""
        
        # --- Simulação para evitar falhas de setup SMTP real ---
        print(f"\n--- 🚀 SIMULAÇÃO DE DISPARO DE EMAIL (SMTP Não Configurado) ---")
        print(f"Para: {to_email}")
        print(f"Assunto: {subject}")
        print(f"Corpo: {body[:50]}...")
        print(f"-------------------------------------------------------------")
        
        # NOTE: A lógica real de SMTP usaria smtplib
        # return {"status": "Email enviado com sucesso."}
        return {"status": "Simulação de email concluída."}

class ChatbotService:
    """Gerencia o Chatbot e o uso de Ferramentas (Gemini Tools)."""

    def __init__(self, db: DatabaseManager, email: EmailService):
        self.db = db
        self.email = email
        self.tools = {
            "get_clients": self.db.get_clients,
            "send_email": self.email.send_email
        }
        # NOTE: Aqui é onde a integração real com a API do Gemini ocorreria
        
    def run_chat_tool_call(self, prompt: str):
        """Simulação de execução de ferramenta via prompt."""
        if "listar clientes" in prompt.lower():
            clients = self.db.get_clients()
            return {"tool_result": clients, "response_text": f"Encontrei {len(clients)} clientes no banco de dados."}
        
        if "enviar email" in prompt.lower():
            # Mock de extração de argumentos pela IA
            result = self.email.send_email("alvo@email.com", "Alerta IA", "O agendamento ótimo está pronto!")
            return {"tool_result": result, "response_text": "Email de alerta simulado enviado com sucesso."}

        return {"response_text": "Desculpe, não entendi o comando. Tente 'listar clientes' ou 'enviar email'."}

# Instância única dos serviços (Injeção de Dependência)
db_manager = DatabaseManager()
email_service = EmailService()
chatbot_service = ChatbotService(db_manager, email_service)


# --- 3. ROTAS API (APIRouter / BLUEPRINTS) ---

# Roteador para o CRUD (MVC - Cliente Controller)
client_router = APIRouter(prefix="/clients", tags=["Clients (CRUD)"])

@client_router.get("/", response_model=list[ClientDB])
async def get_clients_route():
    """Endpoint para GET (Leitura) - Alimenta o Dashboard PySide6."""
    return db_manager.get_clients()

@client_router.post("/", status_code=status.HTTP_201_CREATED, response_model=ClientDB)
async def create_client_route(client: ClientCreate):
    """Endpoint para POST (Criação)."""
    # NOTE: db_manager.create_client já lança 409 se o email for duplicado
    created_client_data = db_manager.create_client(client)
    return ClientDB(**created_client_data)

# Roteador para o Chatbot (MVC - Chat Controller)
chat_router = APIRouter(prefix="/chat", tags=["Chatbot (Gemini Tools)"])

@chat_router.post("/")
async def chat_route(request: Request):
    """Endpoint para o Chatbot executar comandos de ferramenta."""
    try:
        data = await request.json()
        prompt = data.get('prompt')
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt é obrigatório.")
        
        return chatbot_service.run_chat_tool_call(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno do Chatbot: {e}")

# --- 4. CLASSE PRINCIPAL DO SERVIDOR (FastAPI / POO) ---

class DragoniteToolServer:
    def __init__(self):
        self.app = FastAPI(
            title="Dragonite Tool Server",
            description="Backend de Automação, CRUD e Gemini Tools para PySide6/ONS.",
            version="2.0.0",
            root_path=BASE_URL # Aplica o prefixo a todas as rotas
        )
        self.configure_middleware()
        self.setup_routes()

    def configure_middleware(self):
        """Configura CORS."""
        origins = ["*"] # Permite acesso de qualquer Frontend (PySide6, Astro, Next.js)
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def setup_routes(self):
        """Registra os roteadores (Blueprints) e rotas estáticas."""
        self.app.include_router(client_router)
        self.app.include_router(chat_router)

        # Rota para servir o Frontend Estático (PySide6 com QWebEngineView ou HTML/JS)
        @self.app.get("/", include_in_schema=False)
        async def serve_index():
            # NOTA: Em um ambiente real, o PySide6 faria a requisição para /api/clients
            # e a GUI seria construída localmente. Servir HTML aqui é para mock/web.
            return HTMLResponse(content="""
                <html>
                <head>
                    <title>Dragonite Server</title>
                </head>
                <body>
                    <h1>Dragonite Tool Server está Online!</h1>
                    <p>Endpoints CRUD: /api/clients (GET, POST)</p>
                    <p>Endpoint Chatbot: /api/chat (POST)</p>
                    <p>Pronto para ser consumido pelo seu App PySide6.</p>
                </body>
                </html>
            """)

# --- PONTO DE ENTRADA ---
if __name__ == '__main__':
    server = DragoniteToolServer()
    # Use uvicorn para rodar o FastAPI
    import uvicorn
    print(f"🚀 Dragonite Tool Server (FastAPI) rodando em http://127.0.0.1:8000/api")
    uvicorn.run(server.app, host="0.0.0.0", port=8000)
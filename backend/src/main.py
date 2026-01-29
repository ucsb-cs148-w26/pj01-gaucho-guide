from fastapi import FastAPI
from backend.src.api import chat, rag

app = FastAPI()

app.include_router(chat.router)
app.include_router(rag.router)

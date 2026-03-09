import os

from dotenv import load_dotenv
from fastapi import FastAPI
from src.api import chat, rag, transcript, auth

app = FastAPI()


from fastapi.middleware.cors import CORSMiddleware

load_dotenv(dotenv_path=".env", override=False)

frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173").strip()
extra_frontend_urls = [
    url.strip()
    for url in os.getenv("FRONTEND_URLS", "").split(",")
    if url.strip()
]

allow_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "https://ppm-qualities-tells-services.trycloudflare.com",
    frontend_url,
    *extra_frontend_urls,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(dict.fromkeys(allow_origins)),
    allow_origin_regex=r"https://gauchoguider(-.*)?\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(rag.router)
app.include_router(transcript.router)
app.include_router(auth.router)

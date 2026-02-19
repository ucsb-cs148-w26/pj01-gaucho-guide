from fastapi import FastAPI
from backend.src.api import chat, rag, transcript
from src.api import chat, rag, auth

app = FastAPI()


from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "https://ppm-qualities-tells-services.trycloudflare.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(rag.router)
app.include_router(transcript.router)
app.include_router(auth.router)

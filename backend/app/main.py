import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# === IMPORTS DES ROUTERS ===
from app.auth import router as auth_router
from app.routers.chat import router as chat_router
from app.routers.pdf_upload import router as pdf_router   # PDF EN PREMIER !
from app.routers.chat_rag import router as chat_rag_router
from app.routers.profile import router as profile_router
from app.routers.recommend import router as recommend_router
from app.routers.certifications import router as certifications_router


# === STARTUP EVENT ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load models and cache at startup for faster queries."""
    print("[startup] Loading models and certification cache...")

    try:
        # Pre-load certification embeddings cache
        from app.services.graph_reasoning import load_certification_cache
        load_certification_cache()
        print("[startup] Certification cache loaded successfully")
    except Exception as e:
        print(f"[startup] Warning: Could not load cache: {e}")

    try:
        # Pre-load skills cache
        from app.services.skill_extractor import load_canonical_skills
        load_canonical_skills()
        print("[startup] Skills cache loaded successfully")
    except Exception as e:
        print(f"[startup] Warning: Could not load skills cache: {e}")

    print("[startup] Ready to serve requests!")
    yield
    print("[shutdown] Cleaning up...")


app = FastAPI(lifespan=lifespan)

# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================================================
# IMPORTANT : ORDRE DES ROUTERS
# ======================================================
# 1️⃣ Load PDF router first → pdf_memory becomes available globally
app.include_router(pdf_router)

# 2️⃣ Then load all other routers
app.include_router(auth_router, prefix="/auth")
app.include_router(chat_router, prefix="/chat")
app.include_router(chat_rag_router, prefix="/chat-rag")   # ← RAG lit pdf_memory ici
app.include_router(profile_router, prefix="/profile")
app.include_router(recommend_router, prefix="/recommend")
app.include_router(certifications_router, prefix="/certifications")


@app.get("/")
def home():
    return {"status": "Backend running"}

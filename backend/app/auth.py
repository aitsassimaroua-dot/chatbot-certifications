from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from app.utils.db_mysql import get_db_connection

router = APIRouter(tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(BaseModel):
    email: str
    password: str

# ---------------- REGISTER ----------------
@router.post("/register")
def register(user: User):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE email=%s", (user.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    hashed = pwd_context.hash(user.password)

    cursor.execute(
        "INSERT INTO users (email, password_hash) VALUES (%s, %s)",
        (user.email, hashed)
    )
    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "Compte créé avec succès"}

# ---------------- LOGIN ----------------
@router.post("/login")
def login(user: User):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, password_hash FROM users WHERE email=%s",
        (user.email,)
    )
    result = cursor.fetchone()

    if not result:
        raise HTTPException(status_code=400, detail="Email incorrect")

    user_id, hashed = result

    if not pwd_context.verify(user.password, hashed):
        raise HTTPException(status_code=400, detail="Mot de passe incorrect")

    cursor.close()
    conn.close()

    return {"message": "Connexion réussie", "user_id": user_id}

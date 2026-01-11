from fastapi import APIRouter
from pydantic import BaseModel
from app.database import save_profile

router = APIRouter(prefix="/profile", tags=["profile"])

class Profile(BaseModel):
    id: str
    niveau: str
    objectif: str
    budget: int
    temps_par_semaine: int
    competences: list[str]

@router.post("/")
def save_user_profile(profile: Profile):
    save_profile(profile.dict())
    return {"message": "Profil enregistré avec succès", "profile": profile}

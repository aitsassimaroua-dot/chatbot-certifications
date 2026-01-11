# app/schemas.py
from pydantic import BaseModel

class ProfileIn(BaseModel):
    niveau: str
    objectif: str
    budget: float
    temps_par_semaine: int
    competences: list[str]

class Recommendation(BaseModel):
    id: str
    titre: str
    provider: str
    difficulte: str
    prix: float
    competences: list[str] = []
    justification: str

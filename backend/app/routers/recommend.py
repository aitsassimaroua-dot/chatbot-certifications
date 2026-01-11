from fastapi import APIRouter
from app.services.recommender import get_recommendations_from_db

router = APIRouter(prefix="/recommend", tags=["recommend"])

@router.get("/{user_id}")
def recommend_for_user(user_id: str):
    """
    Lit le profil dans Neo4j et renvoie les certifications recommandées.
    """
    recommandations = get_recommendations_from_db(user_id)
    return {"recommandations": recommandations}

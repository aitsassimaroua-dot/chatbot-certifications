from app.database import execute_query
from app.services.graph_reasoning import get_smart_recommendations


def get_recommendations_from_db(user_id: str) -> list[dict]:
    """
    Get personalized recommendations based on user profile stored in Neo4j.

    Uses the graph reasoning engine for intelligent skill matching.
    """
    # 1. Load user profile from Neo4j
    profile_query = """
    MATCH (p:Profile {id: $id})
    RETURN p
    """
    result = execute_query(profile_query, {"id": user_id})

    if not result:
        return []

    profile_node = result[0]["p"]

    # 2. Build user profile dict
    user_profile = {
        "niveau": profile_node.get("niveau"),
        "objectif": profile_node.get("objectif"),
        "budget": profile_node.get("budget"),
        "competences": profile_node.get("competences", [])
    }

    # 3. Use graph reasoning for smart recommendations
    # Build a query from the profile
    query_text = f"""
    Je cherche des certifications pour {user_profile.get('objectif', 'progresser')}.
    Mon niveau actuel est {user_profile.get('niveau', 'débutant')}.
    Mes compétences: {', '.join(user_profile.get('competences', []))}.
    """

    result = get_smart_recommendations(
        user_text=query_text,
        user_profile=user_profile,
        top_k=6,
        use_llm_extraction=False  # Skills already in profile
    )

    # 4. Format recommendations
    recommendations = []
    for cert in result.get("recommendations", []):
        recommendations.append({
            "id": cert.get("id"),
            "titre": cert.get("titre"),
            "domaine": cert.get("domaine"),
            "niveau": cert.get("niveau"),
            "objectif": cert.get("objectif"),
            "competences": cert.get("competences", []),
            "difficulte": cert.get("difficulte"),
            "duree": cert.get("duree"),
            "prix": cert.get("prix"),
            "url": cert.get("url"),
            "relevance_score": cert.get("combined_score", cert.get("relevance_score", 0)),
            "matched_skills": cert.get("matched_skills", [])
        })

    return recommendations


def get_recommendations_for_text(text: str, top_k: int = 5) -> dict:
    """
    Get recommendations based on free-form text (CV, description, etc.).

    Returns full result with skill analysis and reasoning.
    """
    return get_smart_recommendations(
        user_text=text,
        user_profile=None,
        top_k=top_k,
        use_llm_extraction=True
    )

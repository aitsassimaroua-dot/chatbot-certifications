# app/routers/certifications.py
from fastapi import APIRouter
from app.database import execute_query
from app.services.rag_service import refresh_cache, search_relevant_certifications
from app.services.skill_extractor import refresh_skills_cache

router = APIRouter(tags=["Certification"])


@router.get("/all")
def get_all_certifications():
    """Get all certifications from Neo4j with count."""
    query = """
    MATCH (c:Certification)
    RETURN
        c.id AS id,
        c.titre AS titre,
        c.domaine AS domaine,
        c.niveau AS niveau,
        c.prix AS prix,
        c.duree AS duree
    ORDER BY c.domaine, c.titre
    """
    results = execute_query(query)

    certifications = [dict(r) for r in results]
    return {
        "total": len(certifications),
        "certifications": certifications
    }


@router.post("/refresh-cache")
def refresh_certification_cache():
    """Refresh all certification caches after Neo4j data changes."""
    # Refresh RAG service cache
    certs, _ = refresh_cache()
    # Refresh skill extractor cache
    refresh_skills_cache()

    return {
        "status": "success",
        "message": f"Cache refreshed with {len(certs)} certifications"
    }


@router.get("/debug-recommendations")
def debug_recommendations():
    """
    Debug endpoint to test recommendation flow and verify all fields are returned.
    Test with: GET /certifications/debug-recommendations
    """
    # Test query
    test_query = "Je cherche une certification AWS pour le cloud"

    result = search_relevant_certifications(
        question=test_query,
        user_id="debug-user",
        top_k=5
    )

    recommendations = result.get("recommendations", [])

    # Extract key fields from each recommendation for debugging
    debug_data = []
    for i, rec in enumerate(recommendations):
        debug_data.append({
            "index": i + 1,
            "titre": rec.get("titre"),
            "niveau": rec.get("niveau"),
            "prix": rec.get("prix"),
            "duree": rec.get("duree"),
            "domaine": rec.get("domaine"),
            "competences": rec.get("competences"),
            "matched_skills": rec.get("matched_skills"),
            "relevance_score": rec.get("relevance_score"),
            "combined_score": rec.get("combined_score"),
            "all_keys": list(rec.keys())
        })

    return {
        "test_query": test_query,
        "total_recommendations": len(recommendations),
        "debug_data": debug_data,
        "full_first_recommendation": recommendations[0] if recommendations else None
    }


@router.get("/{certif_id}")
def get_certification(certif_id: str):
    query = """
    MATCH (c:Certification {id: $id})
    RETURN c
    """
    result = execute_query(query, {"id": certif_id})

    if not result:
        return {"detail": "Certification not found"}

    c = result[0]["c"]

    return {
        "id": c.get("id", ""),
        "titre": c.get("titre", ""),
        "domaine": c.get("domaine", ""),
        "niveau": c.get("niveau", ""),
        "prix": c.get("prix", 0),
        "duree": c.get("duree", ""),
        "objectif": c.get("objectif", ""),
        "competences": c.get("competences", []),
        "langues": c.get("langues", []),
        "url": c.get("url", ""),
        "temps_par_semaine": c.get("temps_par_semaine", "")
    }

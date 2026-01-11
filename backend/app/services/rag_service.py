# ================================
# RAG SERVICE – CERTIPROFILE PRO
# Enhanced with skill-based reasoning
# ================================

import re
from sentence_transformers import SentenceTransformer, util
from app.database import execute_query
from app.services.graph_reasoning import get_smart_recommendations
from app.services.skill_extractor import extract_skill_vector

# ================================
# Charger le modèle sémantique
# ================================
model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# ================================
# Cache pour embeddings (lazy loading)
# ================================
_certifications_cache = None
_embeddings_cache = None


def load_certifications_from_neo4j():
    """Load certifications from Neo4j with caching."""
    global _certifications_cache, _embeddings_cache

    if _certifications_cache is not None:
        return _certifications_cache, _embeddings_cache

    query = """
    MATCH (c:Certification)
    RETURN
        c.id AS id,
        c.titre AS titre,
        c.domaine AS domaine,
        c.niveau AS niveau,
        c.objectif AS objectif,
        c.competences AS competences,
        c.duree AS duree,
        c.prix AS prix,
        c.url AS url,
        c.langues AS langues,
        c.temps_par_semaine AS temps_par_semaine
    """
    rows = execute_query(query)

    certifications = []
    for r in rows:
        text = f"{r['titre']} - {r['objectif']} - {', '.join(r['competences'] or [])}"
        certifications.append({
            "id": r["id"],
            "text": text,
            "titre": r["titre"],
            "domaine": r["domaine"],
            "niveau": r["niveau"],
            "objectif": r["objectif"],
            "competences": r["competences"] or [],
            "duree": r["duree"],
            "prix": r["prix"],
            "url": r["url"],
            "langues": r["langues"],
            "temps_par_semaine": r["temps_par_semaine"]
        })

    embeddings = None
    if certifications:
        embeddings = model.encode(
            [c["text"] for c in certifications],
            convert_to_tensor=True
        )

    _certifications_cache = certifications
    _embeddings_cache = embeddings

    return certifications, embeddings


def refresh_cache():
    """Force refresh of certification cache."""
    global _certifications_cache, _embeddings_cache
    _certifications_cache = None
    _embeddings_cache = None
    return load_certifications_from_neo4j()


# ================================
# Budget extraction
# ================================
def extract_budget(text: str) -> float | None:
    """Extract budget from user query."""
    match = re.search(r'(\d+(?:\.\d+)?)\s*(€|eur|euros?|dh|mad)', text.lower())
    if match:
        return float(match.group(1))
    return None


# ================================
# Smart RAG with skill matching
# ================================
def search_relevant_certifications(
    question: str,
    user_id: str = None,
    top_k: int = 10,
    user_profile: dict = None
) -> dict:
    """
    Enhanced RAG search using skill-based graph reasoning.

    Returns:
        {
            "source": "graph_reasoning",
            "skill_analysis": {...},
            "recommendations": [...],
            "reasoning": {...},
            "context_text": "..."  # For backward compatibility
        }
    """

    # Build user profile from query and stored profile
    profile = user_profile or {}

    # Extract budget from query if present
    query_budget = extract_budget(question)
    if query_budget:
        profile["budget"] = query_budget

    # Get smart recommendations using graph reasoning
    result = get_smart_recommendations(
        user_text=question,
        user_profile=profile,
        top_k=top_k,
        use_llm_extraction=True
    )

    # Build context text for backward compatibility
    context_parts = []
    for cert in result["recommendations"]:
        context_parts.append(format_certification(cert))

    result["source"] = "graph_reasoning"
    result["context_text"] = "\n\n".join(context_parts)

    return result


def format_certification(cert: dict) -> str:
    """Format certification for display/LLM context."""
    matched = cert.get("matched_skills", [])
    score = cert.get("combined_score", cert.get("relevance_score", 0))

    return f"""📜 {cert.get('titre', 'N/A')}
   Domaine: {cert.get('domaine', 'N/A')}
   Niveau: {cert.get('niveau', 'N/A')}
   Objectif: {cert.get('objectif', 'N/A')}
   Compétences: {', '.join(cert.get('competences', []))}
   Durée: {cert.get('duree', 'N/A')}
   Prix: {cert.get('prix', 'N/A')} €
   Score de pertinence: {score:.1f}%
   Compétences correspondantes: {', '.join(matched) if matched else 'Aucune correspondance directe'}"""


# ================================
# Legacy function for backward compatibility
# ================================
def search_neo4j_legacy(question: str) -> list[dict]:
    """Legacy Neo4j search (kept for backward compatibility)."""
    q = question.lower()

    domain = None
    if "cloud" in q:
        domain = "Cloud"
    elif "data" in q:
        domain = "Data"
    elif "ai" in q or "machine learning" in q:
        domain = "AI"

    level = None
    if "débutant" in q:
        level = "Débutant"
    elif "intermédiaire" in q:
        level = "Intermédiaire"
    elif "avancé" in q:
        level = "Avancé"

    budget = extract_budget(question)

    query = """
    MATCH (c:Certification)
    WHERE ($domain IS NULL OR c.domaine = $domain)
      AND ($level IS NULL OR c.niveau = $level)
      AND ($budget IS NULL OR c.prix <= $budget)
    RETURN
        c.titre AS titre,
        c.niveau AS niveau,
        c.objectif AS objectif,
        c.competences AS competences,
        c.prix AS prix,
        c.duree AS duree,
        c.url AS url
    LIMIT 20
    """

    return execute_query(query, {
        "domain": domain,
        "level": level,
        "budget": budget
    })

# ================================
# GRAPH REASONING SERVICE
# Weighted skill matching & ranking using Neo4j
# ================================

from app.database import execute_query
from app.services.skill_extractor import extract_skill_vector
from sentence_transformers import SentenceTransformer, CrossEncoder, util
import time

# Embedding model for semantic similarity
model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# Reranker model for better precision (lightweight)
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", max_length=512)


# ================================
# Helper: Normalize competences format
# ================================
def normalize_competences(competences):
    """
    Ensure competences is always a proper list of strings.
    Handles: string, comma-separated string, list, or None.
    """
    if competences is None:
        return []

    if isinstance(competences, str):
        # Comma-separated string
        if "," in competences:
            return [s.strip() for s in competences.split(",") if s.strip()]
        # Single competence
        return [competences.strip()] if competences.strip() else []

    if isinstance(competences, (list, tuple)):
        result = []
        for item in competences:
            if isinstance(item, str) and item.strip():
                result.append(item.strip())
            elif item is not None:
                result.append(str(item).strip())
        return result

    return []


# ================================
# Certification Embeddings Cache
# Pre-compute embeddings at startup for faster queries
# ================================
_cert_cache = {
    "certifications": [],
    "texts": [],
    "embeddings": None,
    "loaded": False
}


def load_certification_cache():
    """
    Pre-load and embed all certifications at startup.
    This significantly speeds up semantic re-ranking.
    """
    global _cert_cache

    if _cert_cache["loaded"]:
        return _cert_cache

    print("[graph_reasoning] Loading certification cache...")
    start = time.time()

    query = """
    MATCH (c:Certification)
    WHERE c.competences IS NOT NULL
    RETURN
        c.id AS id,
        c.titre AS titre,
        c.domaine AS domaine,
        c.objectif AS objectif,
        c.competences AS competences
    """

    results = execute_query(query)

    certifications = []
    texts = []

    for r in results:
        cert = dict(r)
        certifications.append(cert)

        # Build searchable text for embedding
        competences = cert.get("competences", [])
        if isinstance(competences, str):
            competences = competences.split(", ")

        text = f"{cert.get('titre', '')} - {cert.get('objectif', '')} - {', '.join(competences)}"
        texts.append(text)

    if texts:
        embeddings = model.encode(texts, convert_to_tensor=True, show_progress_bar=False)
    else:
        embeddings = None

    _cert_cache["certifications"] = certifications
    _cert_cache["texts"] = texts
    _cert_cache["embeddings"] = embeddings
    _cert_cache["loaded"] = True

    elapsed = time.time() - start
    print(f"[graph_reasoning] Cache loaded: {len(certifications)} certifications in {elapsed:.2f}s")

    return _cert_cache


def get_cached_embedding(cert_id: str):
    """Get cached embedding for a certification by ID."""
    cache = load_certification_cache()

    for i, cert in enumerate(cache["certifications"]):
        if cert.get("id") == cert_id:
            return cache["embeddings"][i] if cache["embeddings"] is not None else None

    return None


def refresh_certification_cache():
    """Force refresh of certification cache (call after Neo4j data changes)."""
    global _cert_cache
    _cert_cache["loaded"] = False
    return load_certification_cache()


# ================================
# Weighted Skill Matching Query
# ================================
def query_certifications_by_skills(
    skill_vector: dict[str, float],
    domains: list[str] = None,
    level: str = None,
    budget: float = None,
    limit: int = 100
) -> list[dict]:
    """
    Query Neo4j for certifications matching the skill vector.
    Uses Cypher to compute skill overlap scores.
    Handles competences stored as comma-separated strings.

    Args:
        skill_vector: {skill_name: weight} - weighted skills from user
        domains: Optional domain filter (cloud, data, ai, etc.)
        level: Optional level filter (débutant, intermédiaire, avancé)
        budget: Optional max budget filter
        limit: Max results to return

    Returns:
        List of certifications with relevance scores
    """

    if not skill_vector:
        # Fallback to basic query if no skills extracted
        return query_certifications_basic(domains, level, budget, limit)

    skill_names = list(skill_vector.keys())
    skill_weights = skill_vector

    # Cypher query - handles competences as either array or comma-separated string
    # Uses text matching for skill overlap
    query = """
    WITH $skills AS user_skills, $weights AS weights

    MATCH (c:Certification)
    WHERE c.competences IS NOT NULL

    // Apply optional filters
    AND ($domains IS NULL OR size($domains) = 0 OR
         ANY(d IN $domains WHERE toLower(c.domaine) CONTAINS toLower(d)))
    AND ($level IS NULL OR toLower(c.niveau) = toLower($level))
    AND ($budget IS NULL OR c.prix <= $budget)

    // Handle both array and string formats for competences
    WITH c, user_skills, weights,
         CASE
             WHEN c.competences IS :: LIST<ANY> THEN [s IN c.competences | trim(toString(s))]
             ELSE [s IN split(toString(c.competences), ', ') | trim(s)]
         END AS cert_skills

    // Find matching skills (case-insensitive substring match)
    WITH c, user_skills, weights, cert_skills,
         [user_skill IN user_skills
          WHERE ANY(cert_skill IN cert_skills
                    WHERE toLower(cert_skill) CONTAINS toLower(user_skill)
                       OR toLower(user_skill) CONTAINS toLower(cert_skill))] AS matching_skills

    // Compute weighted score
    WITH c, cert_skills, matching_skills,
         size(matching_skills) AS match_count,
         size(cert_skills) AS total_cert_skills,
         REDUCE(score = 0.0, skill IN matching_skills |
                score + COALESCE(weights[skill], 0.5)) AS weighted_score

    // Compute normalized relevance score (0-100, capped)
    WITH c, cert_skills, matching_skills, match_count, total_cert_skills, weighted_score,
         CASE
             WHEN size(matching_skills) = 0 THEN 0.0
             ELSE toFloat(match_count) / toFloat(total_cert_skills) * 100
         END AS raw_score

    // Cap score at 100%
    WITH c, cert_skills, matching_skills, match_count, total_cert_skills,
         CASE WHEN raw_score > 100.0 THEN 100.0 ELSE raw_score END AS relevance_score

    WHERE match_count > 0 OR $allow_no_match = true

    RETURN
        c.id AS id,
        c.titre AS titre,
        c.domaine AS domaine,
        c.niveau AS niveau,
        c.objectif AS objectif,
        cert_skills AS competences,
        c.duree AS duree,
        c.prix AS prix,
        c.url AS url,
        c.langues AS langues,
        c.temps_par_semaine AS temps_par_semaine,
        matching_skills AS matched_skills,
        match_count AS skill_matches,
        total_cert_skills AS total_skills,
        round(relevance_score * 100) / 100 AS relevance_score

    ORDER BY relevance_score DESC, match_count DESC, c.prix ASC
    LIMIT $limit
    """

    results = execute_query(query, {
        "skills": skill_names,
        "weights": skill_weights,
        "domains": domains if domains else [],
        "level": level,
        "budget": budget,
        "limit": limit,
        "allow_no_match": len(skill_names) < 2  # Allow no-match results if few skills
    })

    return [dict(r) for r in results]


def query_certifications_basic(
    domains: list[str] = None,
    level: str = None,
    budget: float = None,
    limit: int = 100
) -> list[dict]:
    """Fallback query when no skills are provided. Uses TEACHES relationships."""

    query = """
    MATCH (c:Certification)
    WHERE ($domains IS NULL OR size($domains) = 0 OR
           ANY(d IN $domains WHERE toLower(c.domaine) CONTAINS toLower(d)))
      AND ($level IS NULL OR toLower(c.niveau) = toLower($level))
      AND ($budget IS NULL OR c.prix <= $budget)

    // Get skills from TEACHES relationships
    OPTIONAL MATCH (c)-[:TEACHES]->(s:Skill)

    WITH c, collect(DISTINCT s.name) AS skills

    RETURN
        c.id AS id,
        c.titre AS titre,
        c.domaine AS domaine,
        c.niveau AS niveau,
        c.objectif AS objectif,
        CASE WHEN size(skills) > 0 THEN skills ELSE c.competences END AS competences,
        c.duree AS duree,
        c.prix AS prix,
        c.url AS url,
        c.langues AS langues,
        c.temps_par_semaine AS temps_par_semaine,
        [] AS matched_skills,
        0 AS skill_matches,
        size(skills) AS total_skills,
        0.0 AS relevance_score

    ORDER BY c.prix ASC
    LIMIT $limit
    """

    results = execute_query(query, {
        "domains": domains if domains else [],
        "level": level,
        "budget": budget,
        "limit": limit
    })

    return [dict(r) for r in results]


# ================================
# Semantic Re-ranking with Reranker
# ================================
def rerank_with_semantics(
    certifications: list[dict],
    query_text: str,
    alpha: float = 0.7,  # Increased to give more weight to skill/level scores
    use_reranker: bool = True
) -> list[dict]:
    """
    Re-rank certifications using semantic similarity and cross-encoder reranker.
    Combines skill-based score (including level boost) with semantic score.

    Args:
        certifications: List from Neo4j query (already boosted by level)
        query_text: Original user query
        alpha: Weight for skill/level score (1-alpha for semantic). Default 0.7.
        use_reranker: Whether to use CrossEncoder for final reranking

    Returns:
        Re-ranked certifications with combined scores
    """

    if not certifications or not query_text:
        return certifications

    # Ensure cache is loaded for fast embedding lookup
    load_certification_cache()

    # Encode user query
    query_embed = model.encode(query_text, convert_to_tensor=True)

    # Build certification texts for embedding
    cert_texts = []
    for c in certifications:
        competences = c.get('competences', [])
        if isinstance(competences, str):
            competences = competences.split(", ")
        text = f"{c.get('titre', '')} - {c.get('objectif', '')} - {', '.join(competences)}"
        cert_texts.append(text)

    # Encode certifications (use cache if available, else compute)
    cert_embeddings = model.encode(cert_texts, convert_to_tensor=True, show_progress_bar=False)

    # Compute semantic similarity (bi-encoder)
    similarities = util.cos_sim(query_embed, cert_embeddings)[0]

    # Combine scores (Phase 1: bi-encoder)
    for i, cert in enumerate(certifications):
        skill_score = cert.get("relevance_score", 0)
        semantic_score = similarities[i].item() * 100  # Scale to 0-100

        # Combined score
        combined = (alpha * skill_score) + ((1 - alpha) * semantic_score)
        cert["semantic_score"] = round(semantic_score, 2)
        cert["combined_score"] = round(combined, 2)

    # Sort by combined score (pre-reranking)
    certifications.sort(key=lambda x: x.get("combined_score", 0), reverse=True)

    # Phase 2: Cross-encoder reranking (more precise but slower)
    if use_reranker and len(certifications) >= 2:
        # Only rerank top candidates for efficiency
        top_k = min(15, len(certifications))
        top_certs = certifications[:top_k]
        rest_certs = certifications[top_k:]

        # Prepare pairs for cross-encoder
        pairs = [(query_text, cert_texts[i]) for i in range(top_k)]

        try:
            # Cross-encoder scores
            rerank_scores = reranker.predict(pairs)

            # Normalize rerank scores to 0-100 range
            min_score = float(min(rerank_scores))
            max_score = float(max(rerank_scores))
            score_range = max_score - min_score if max_score != min_score else 1.0

            for i, cert in enumerate(top_certs):
                normalized = float(((rerank_scores[i] - min_score) / score_range) * 100)
                cert["rerank_score"] = round(normalized, 2)

                # Final score: blend combined with rerank
                # 70% combined (skill+semantic), 30% reranker
                final = float(0.7 * cert["combined_score"] + 0.3 * normalized)
                cert["final_score"] = round(final, 2)

            # Sort by final score
            top_certs.sort(key=lambda x: x.get("final_score", 0), reverse=True)

            # Use final_score as combined_score for consistency
            for cert in top_certs:
                cert["combined_score"] = float(cert["final_score"])

            certifications = top_certs + rest_certs

        except Exception as e:
            print(f"[graph_reasoning] Reranker failed: {e}")
            # Fallback to combined score ordering

    return certifications


# ================================
# Main Recommendation Function
# ================================
def get_smart_recommendations(
    user_text: str,
    user_profile: dict = None,
    top_k: int = 10,
    use_llm_extraction: bool = True
) -> dict:
    """
    Get intelligent certification recommendations.

    Args:
        user_text: User query or CV text
        user_profile: Optional user profile with level, budget, domains, etc.
        top_k: Number of recommendations to return
        use_llm_extraction: Whether to use LLM for skill extraction

    Returns:
        {
            "skill_analysis": {...},      # Extracted skill vector
            "recommendations": [...],      # Ranked certifications
            "reasoning": {...}             # Explanation for LLM
        }
    """

    # 1. Extract skill vector from user input
    skill_analysis = extract_skill_vector(user_text, use_llm=use_llm_extraction)

    # 2. Get held certifications and experience years
    held_certs = skill_analysis.get("held_certifications", [])
    experience_years = skill_analysis.get("experience_years", 0)

    # 3. Determine appropriate level
    # PRIORITY: user_profile["niveau"] > skill_analysis["level_hint"] > experience-based
    level = None
    budget = None
    domains = skill_analysis.get("domains", [])

    # Check user_profile for explicit preferences FIRST (highest priority)
    if user_profile:
        if user_profile.get("niveau"):
            level = user_profile.get("niveau")
            print(f"[graph_reasoning] Niveau from user preference: {level}")
        if user_profile.get("budget"):
            budget = user_profile.get("budget")
        if user_profile.get("domains"):
            domains = user_profile.get("domains") + domains
            domains = list(set(domains))  # Remove duplicates
        # Add profile skills
        profile_skills = user_profile.get("competences", [])
        for skill in profile_skills:
            if skill not in skill_analysis["skill_vector"]:
                skill_analysis["skill_vector"][skill] = 0.5

    # If no explicit level preference, use experience-based detection
    if not level:
        if experience_years >= 5:
            level = "avancé"
        elif experience_years >= 2:
            level = "intermédiaire"
        else:
            # 0-1 years = débutant (students, juniors, career changers)
            level = "débutant"

        # Check for explicit level hints in skill_analysis
        hint = skill_analysis.get("level_hint")
        if hint:
            hint_lower = hint.lower()
            if "avancé" in hint_lower:
                level = "avancé"
            elif "intermédiaire" in hint_lower:
                level = "intermédiaire"
            elif "débutant" in hint_lower:
                level = "débutant"

    # Update skill_analysis with final level
    skill_analysis["level_hint"] = level

    # Log for debugging
    print(f"[graph_reasoning] Années d'expérience: {experience_years} -> niveau final: {level}")
    if held_certs:
        print(f"[graph_reasoning] Certifications déjà obtenues: {held_certs}")

    # 4. Query Neo4j with weighted skill matching
    # Get extra results to account for filtering
    certifications = query_certifications_by_skills(
        skill_vector=skill_analysis["skill_vector"],
        domains=domains if domains else None,
        level=None,  # Don't filter by level in query, we'll prioritize instead
        budget=budget,
        limit=top_k * 3  # Get more for filtering and re-ranking
    )

    # 5. Filter out certifications already held
    if held_certs:
        before_count = len(certifications)
        certifications = [c for c in certifications if c.get("id") not in held_certs]
        filtered_count = before_count - len(certifications)
        if filtered_count > 0:
            print(f"[graph_reasoning] Filtré {filtered_count} certification(s) déjà obtenue(s)")

    # 6. Boost/penalize certifications based on LEVEL matching
    # Use VERY aggressive scoring to ensure correct level appears first
    if level:
        target_level = level.lower()
        print(f"[graph_reasoning] Applying level boosting for: {target_level}")

        for cert in certifications:
            cert_level = (cert.get("niveau") or "").lower()
            base_score = cert.get("relevance_score", 0)

            # Exact level match = MAJOR boost
            if target_level in cert_level or cert_level in target_level:
                cert["relevance_score"] = base_score + 60  # Increased from 40
                cert["level_match"] = "exact"

            # For beginner profiles (débutant) - be VERY strict
            elif target_level == "débutant":
                if "intermédiaire" in cert_level:
                    cert["relevance_score"] = base_score - 50  # Increased penalty
                    cert["level_match"] = "too_high"
                elif "avancé" in cert_level:
                    cert["relevance_score"] = base_score - 80  # Very strong penalty
                    cert["level_match"] = "way_too_high"

            # For intermediate profiles (intermédiaire)
            elif target_level == "intermédiaire":
                if "débutant" in cert_level:
                    cert["relevance_score"] = base_score - 15
                    cert["level_match"] = "too_low"
                elif "avancé" in cert_level:
                    cert["relevance_score"] = base_score - 25
                    cert["level_match"] = "too_high"

            # For senior profiles (avancé)
            elif target_level == "avancé":
                if "intermédiaire" in cert_level:
                    cert["relevance_score"] = base_score + 15  # Acceptable
                    cert["level_match"] = "acceptable"
                elif "débutant" in cert_level:
                    cert["relevance_score"] = base_score - 50
                    cert["level_match"] = "way_too_low"

    # 7. Boost/penalize certifications based on DOMAIN matching
    if domains:
        print(f"[graph_reasoning] Applying domain boosting for: {domains}")
        for cert in certifications:
            cert_domain = (cert.get("domaine") or "").lower()
            cert_title = (cert.get("titre") or "").lower()

            domain_matched = False
            for target_domain in domains:
                target_d = target_domain.lower()
                # Check domain field and title for domain keywords
                if target_d in cert_domain or target_d in cert_title:
                    domain_matched = True
                    break
                # Special checks for Cloud
                if target_d == "cloud" and any(kw in cert_title for kw in ["aws", "azure", "gcp", "google cloud"]):
                    domain_matched = True
                    break
                # Special checks for AI
                if target_d == "ai" and any(kw in cert_title for kw in ["machine learning", "deep learning", "nlp", "tensorflow", "pytorch"]):
                    domain_matched = True
                    break

            if domain_matched:
                cert["relevance_score"] = cert.get("relevance_score", 0) + 40
                cert["domain_match"] = True
            else:
                cert["relevance_score"] = cert.get("relevance_score", 0) - 30
                cert["domain_match"] = False

    # Sort by relevance_score BEFORE semantic reranking
    certifications.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

    # Log top 3 after level/domain boosting
    print(f"[graph_reasoning] Top 3 after boosting:")
    for i, cert in enumerate(certifications[:3]):
        print(f"  {i+1}. {cert.get('titre')} | {cert.get('niveau')} | score: {cert.get('relevance_score')}")

    # 8. Re-rank with semantic similarity (but preserve level/domain ordering)
    if certifications:
        certifications = rerank_with_semantics(certifications, user_text)

    # 9. Take top_k results
    recommendations = certifications[:top_k]

    # 10. Normalize competences format for frontend
    for rec in recommendations:
        rec["competences"] = normalize_competences(rec.get("competences"))

    # 11. Build reasoning context for LLM
    reasoning = build_reasoning_context(skill_analysis, recommendations)

    return {
        "skill_analysis": skill_analysis,
        "recommendations": recommendations,
        "reasoning": reasoning
    }


def build_reasoning_context(skill_analysis: dict, recommendations: list[dict]) -> dict:
    """
    Build structured context for LLM to use as evidence.
    """

    user_skills = list(skill_analysis.get("skill_vector", {}).keys())
    domains = skill_analysis.get("domains", [])
    level = skill_analysis.get("level_hint")

    context = {
        "user_profile_summary": {
            "detected_skills": user_skills[:10],  # Top 10
            "domains_of_interest": domains,
            "experience_level": level or "non spécifié"
        },
        "recommendation_evidence": []
    }

    for cert in recommendations:
        evidence = {
            "certification": cert.get("titre", ""),
            "relevance_score": cert.get("combined_score", cert.get("relevance_score", 0)),
            "matched_skills": cert.get("matched_skills", []),
            "match_reason": _generate_match_reason(cert, user_skills)
        }
        context["recommendation_evidence"].append(evidence)

    return context


def _generate_match_reason(cert: dict, user_skills: list[str]) -> str:
    """Generate human-readable match reason."""

    matched = cert.get("matched_skills", [])
    score = cert.get("combined_score", cert.get("relevance_score", 0))

    if not matched:
        return "Recommandation basée sur le domaine et le niveau demandé"

    if len(matched) >= 3:
        return f"Forte correspondance: {len(matched)} compétences en commun ({', '.join(matched[:3])}...)"
    elif len(matched) > 0:
        return f"Correspondance partielle: {', '.join(matched)}"

    return "Recommandation générale"

from groq import Groq
import os
import json

# ================================
# Groq Client (singleton)
# ================================
_client = None

def get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client


# ================================
# Structured Evidence Prompts
# ================================

PROMPT_TEMPLATES = {
    "social": """Tu es CertiBot, un assistant amical spécialisé en certifications Cloud, Data et IA.

Message de l'utilisateur: "{question}"

CONSIGNES:
- Réponds de manière naturelle, chaleureuse et courte (1-2 phrases max)
- Si c'est un remerciement ("merci", "parfait", etc.) → réponds poliment et propose ton aide
- Si c'est une salutation ("bonjour", "salut") → salue et demande comment tu peux aider
- Si c'est un au revoir ("bye", "au revoir") → souhaite une bonne journée
- Reste toujours positif et professionnel
- Tu peux utiliser des emojis avec modération

Exemples:
- "merci" → "Avec plaisir ! N'hésite pas si tu as d'autres questions sur les certifications."
- "bonjour" → "Bonjour ! Comment puis-je t'aider aujourd'hui avec les certifications ?"
- "parfait" → "Super ! Je suis là si tu as besoin d'autres recommandations."

Réponds maintenant:""",

    "pdf_with_graph": """Tu es un conseiller expert en certifications Cloud, Data et IA.

PROFIL CV ANALYSÉ:
- Compétences: {detected_skills}
- Domaines: {domains}
- Niveau recommandé: {level}
- Expérience: {experience_years} ans
- Certifications déjà obtenues: {held_certifications}

CERTIFICATIONS RECOMMANDÉES (classées par pertinence, choisis parmi les 3 premières):
{recommendations}

Question: {question}

RÈGLES OBLIGATOIRES:
1. Choisis 2-3 certifications UNIQUEMENT parmi les 5 premières de la liste ci-dessus
2. Les certifications sont déjà triées par pertinence (la #1 est la meilleure)
3. Le niveau demandé est "{level}" - privilégie ce niveau
4. NE recommande JAMAIS une certification déjà obtenue
5. Copie les informations EXACTEMENT comme dans la liste (nom, niveau, prix, durée)
6. Niveaux autorisés: Débutant, Intermédiaire, Avancé (JAMAIS "Expert")

Format obligatoire:
• [Nom exact de la certification] | Niveau: [X] | Prix: [X]€ | Durée: [X]

Réponds en français, max 100 mots.""",

    "graph_reasoning": """Tu es un conseiller expert en certifications Cloud, Data et IA.

PROFIL UTILISATEUR:
- Compétences détectées: {detected_skills}
- Domaines: {domains}
- Niveau demandé: {level}
- Expérience: {experience_years} ans
- Certifications déjà obtenues: {held_certifications}

CERTIFICATIONS RECOMMANDÉES (triées par pertinence - #1 = meilleure):
{recommendations}

Question: {question}

RÈGLES OBLIGATOIRES:
1. Recommande 2-3 certifications parmi les 5 PREMIÈRES de la liste ci-dessus UNIQUEMENT
2. La liste est triée par score - préfère les certifications #1, #2, #3
3. Le niveau souhaité est "{level}" - choisis des certifications de ce niveau en priorité
4. NE recommande JAMAIS une certification déjà obtenue par l'utilisateur
5. Copie EXACTEMENT le nom, niveau, prix et durée tels qu'écrits dans la liste
6. NIVEAUX AUTORISÉS: "Débutant", "Intermédiaire", "Avancé" (PAS "Expert")

Format obligatoire pour chaque certification:
• [Nom exact] | Niveau: [Débutant/Intermédiaire/Avancé] | Prix: [X]€ | Durée: [X]

Réponds naturellement en français, max 100 mots."""
}


def format_recommendations(recommendations: list) -> str:
    """Format recommendations for prompt - includes top 10 to match panel."""
    if not recommendations:
        return "Aucune certification trouvée."

    parts = []
    for i, cert in enumerate(recommendations[:10], 1):
        score = cert.get("combined_score", cert.get("relevance_score", 0))
        matched = cert.get("matched_skills", [])

        part = f"{i}. {cert.get('titre', 'N/A')} | Niveau: {cert.get('niveau', 'N/A')} | Prix: {cert.get('prix', 'N/A')}€ | Durée: {cert.get('duree', 'N/A')} | Score: {score:.0f}%"
        if matched:
            part += f" | Compétences matchées: {', '.join(matched[:3])}"
        parts.append(part)

    return "\n".join(parts)


def format_evidence(reasoning: dict) -> str:
    """Format reasoning evidence for prompt."""
    if not reasoning:
        return "Pas de preuves structurées disponibles."

    evidence_parts = []
    for item in reasoning.get("recommendation_evidence", [])[:5]:
        evidence_parts.append(
            f"- {item.get('certification', '')}: {item.get('match_reason', '')}"
        )

    return "\n".join(evidence_parts) if evidence_parts else "Correspondance basée sur le domaine"


# ================================
# Main LLM Function with Evidence
# ================================
def ask_with_evidence(
    question: str,
    evidence: dict | None,
    history: str = "",
    mode: str = "graph_reasoning"
) -> str:
    """
    Ask LLM with structured evidence from graph reasoning.

    Args:
        question: User question
        evidence: Structured evidence from RAG/graph reasoning
        history: Conversation history
        mode: "social", "pdf_with_graph", or "graph_reasoning"

    Returns:
        LLM response
    """
    client = get_client()

    template = PROMPT_TEMPLATES.get(mode, PROMPT_TEMPLATES["graph_reasoning"])

    # Build template variables
    variables = {
        "question": question,
        "history": history or "Pas d'historique"
    }

    if mode == "social":
        prompt = template.format(**variables)

    elif mode == "pdf_with_graph" and evidence:
        pdf_skills = evidence.get("pdf_skills", {})
        held_certs = pdf_skills.get("held_certifications", [])
        variables.update({
            "detected_skills": ", ".join(list(pdf_skills.get("skill_vector", {}).keys())[:10]) or "Non détectées",
            "domains": ", ".join(pdf_skills.get("domains", [])) or "Non spécifiés",
            "level": pdf_skills.get("level_hint") or "Non spécifié",
            "experience_years": pdf_skills.get("experience_years", 0),
            "held_certifications": ", ".join(held_certs) if held_certs else "Aucune",
            "pdf_excerpt": evidence.get("pdf_content", "")[:1500],
            "recommendations": format_recommendations(evidence.get("recommendations", []))
        })
        prompt = template.format(**variables)

    elif mode == "graph_reasoning" and evidence:
        skill_analysis = evidence.get("skill_analysis", {})
        held_certs = skill_analysis.get("held_certifications", [])
        variables.update({
            "detected_skills": ", ".join(list(skill_analysis.get("skill_vector", {}).keys())[:10]) or "Non détectées",
            "domains": ", ".join(skill_analysis.get("domains", [])) or "Non spécifiés",
            "level": skill_analysis.get("level_hint") or "Non spécifié",
            "experience_years": skill_analysis.get("experience_years", 0),
            "held_certifications": ", ".join(held_certs) if held_certs else "Aucune",
            "recommendations": format_recommendations(evidence.get("recommendations", [])),
            "evidence": format_evidence(evidence.get("reasoning", {}))
        })
        prompt = template.format(**variables)

    else:
        # Fallback
        prompt = f"""Tu es un expert en certifications professionnelles.

Question: {question}

Réponds de manière utile. Si tu n'as pas d'information, dis-le."""

    # Call Groq
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Erreur lors de la génération de la réponse: {str(e)}"


# ================================
# Legacy LLMService for backward compatibility
# ================================
class LLMService:
    """Kept for backward compatibility."""

    def ask(self, prompt: str, user_id: str = None) -> str:
        """Simple prompt-based ask (legacy)."""
        client = get_client()

        try:
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Erreur: {str(e)}"


llm = LLMService()

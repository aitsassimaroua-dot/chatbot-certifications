from fastapi import APIRouter
from pydantic import BaseModel
from app.services.rag_service import search_relevant_certifications
from app.services.llm_service import ask_with_evidence
from app.services.skill_extractor import extract_skill_vector
from app.routers import pdf_upload
import re

router = APIRouter(tags=["chat-rag"])


class ChatRequest(BaseModel):
    question: str
    user_id: str | None = None


class ResetPreferencesRequest(BaseModel):
    user_id: str | None = None


# ===== Mémoire courte par utilisateur =====
conversation_memory = {}

# ===== Préférences utilisateur (niveau, domaine) =====
user_preferences = {}


def clear_conversation_memory(user_id: str = None):
    """
    Clear conversation memory and preferences for a user or all users.
    Called when PDF is cleared to remove old context.
    """
    global conversation_memory, user_preferences
    if user_id:
        if user_id in conversation_memory:
            del conversation_memory[user_id]
        if user_id in user_preferences:
            del user_preferences[user_id]
        # Also clear anonymous if user was anonymous
        if "anonymous" in conversation_memory:
            del conversation_memory["anonymous"]
        if "anonymous" in user_preferences:
            del user_preferences["anonymous"]
    else:
        # Clear all memory
        conversation_memory = {}
        user_preferences = {}


# ===== Détection de préférences utilisateur =====
def detect_user_preferences(text: str) -> dict:
    """
    Detect explicit user preferences from chat message.
    Returns dict with 'level', 'domain', 'budget' if detected.
    """
    text_lower = text.lower()
    prefs = {}

    # Detect level preferences
    level_patterns = [
        # Débutant patterns
        (r"\b(?:niveau|level)\s*[:\s]?\s*(?:débutant|debutant)s?\b", "débutant"),
        (r"\bje\s+(?:suis|débute|commence|veux\s+débuter)\b", "débutant"),
        (r"\b(?:pour\s+)?(?:débutant|débutants|beginner)s?\b", "débutant"),
        (r"\bcommencer|débuter|apprendre\s+les\s+bases\b", "débutant"),
        (r"\bpremière\s+(?:certification|formation)\b", "débutant"),
        (r"\baucune\s+expérience\b", "débutant"),
        (r"\bcertification[s]?\s+(?:débutant|pour\s+débuter)s?\b", "débutant"),

        # Intermédiaire patterns
        (r"\b(?:niveau|level)\s*[:\s]?\s*(?:intermédiaire|intermediaire)s?\b", "intermédiaire"),
        (r"\b(?:pour\s+)?(?:intermédiaire|intermediaire|intermediate)s?\b", "intermédiaire"),
        (r"\bcertification[s]?\s+(?:intermédiaire|intermediaire)s?\b", "intermédiaire"),

        # Avancé patterns
        (r"\b(?:niveau|level)\s*[:\s]?\s*(?:avancé|avance|expert)s?\b", "avancé"),
        (r"\b(?:pour\s+)?(?:avancé|avancés|avance|advanced|expert)s?\b", "avancé"),
        (r"\bcertification[s]?\s+(?:avancée?s?|pro(?:fessionnelle)?s?)\b", "avancé"),
    ]

    for pattern, level in level_patterns:
        if re.search(pattern, text_lower):
            prefs["level"] = level
            break

    # Detect domain preferences
    domain_patterns = [
        (r"\b(?:en\s+)?(?:aws|amazon\s+web|cloud\s+aws)\b", "cloud"),
        (r"\b(?:en\s+)?(?:azure|microsoft\s+azure|cloud\s+azure)\b", "cloud"),
        (r"\b(?:en\s+)?(?:gcp|google\s+cloud)\b", "cloud"),
        (r"\b(?:en\s+)?(?:cloud|nuage)\b", "cloud"),
        (r"\b(?:en\s+)?(?:data(?:\s+engineer(?:ing)?)?|données|big\s*data)\b", "data"),
        (r"\b(?:en\s+)?(?:ia|ai|intelligence\s+artificielle|machine\s+learning|ml|deep\s+learning)\b", "ai"),
    ]

    for pattern, domain in domain_patterns:
        if re.search(pattern, text_lower):
            prefs["domain"] = domain
            break

    # Detect budget
    budget_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:€|eur|euros?)', text_lower)
    if budget_match:
        prefs["budget"] = float(budget_match.group(1))

    return prefs


def update_user_preferences(uid: str, new_prefs: dict):
    """Update user preferences, merging with existing ones."""
    global user_preferences
    if uid not in user_preferences:
        user_preferences[uid] = {}

    # Update with new preferences (new ones override old)
    for key, value in new_prefs.items():
        if value is not None:
            user_preferences[uid][key] = value
            print(f"[chat_rag] Préférence mise à jour: {key}={value}")


def get_user_preferences(uid: str) -> dict:
    """Get current user preferences."""
    return user_preferences.get(uid, {})


SOCIAL_MESSAGES = [
    # Remerciements
    "merci", "merci beaucoup", "thank", "thanks", "thx",
    # Confirmations
    "ok", "okay", "d'accord", "compris", "entendu", "noté",
    # Appréciations
    "cool", "super", "parfait", "excellent", "génial", "top", "nickel", "impeccable",
    "bien", "très bien", "c'est bon", "c'est parfait", "formidable", "bravo",
    # Salutations
    "salut", "hello", "bonjour", "bonsoir", "hi", "hey", "coucou",
    # Au revoir
    "bye", "au revoir", "à bientôt", "a bientot", "ciao", "bonne journée", "bonne soirée",
    # Autres
    "oui", "non", "peut-être", "je vois", "ah ok", "ah d'accord"
]


def is_social_message(text: str) -> bool:
    """Check if message is a social/greeting message."""
    text_lower = text.lower().strip()

    # Remove punctuation for better matching
    text_clean = text_lower.replace("!", "").replace("?", "").replace(".", "").replace(",", "").strip()

    # Only trigger social mode for short messages (max 8 words)
    if len(text_clean.split()) > 8:
        return False

    # Exact match for short messages
    if text_clean in SOCIAL_MESSAGES:
        return True

    # Check if any social word is contained in the message
    return any(word in text_clean for word in SOCIAL_MESSAGES)


@router.post("/")
def chat_rag(req: ChatRequest):

    user_text = req.question.strip()
    uid = req.user_id or "anonymous"

    # Init user memory
    if uid not in conversation_memory:
        conversation_memory[uid] = []

    history = "\n".join(conversation_memory[uid][-6:])

    # ================= DETECT & UPDATE USER PREFERENCES =================
    # Parse explicit preferences from the current message
    detected_prefs = detect_user_preferences(user_text)
    if detected_prefs:
        update_user_preferences(uid, detected_prefs)
        print(f"[chat_rag] Préférences détectées: {detected_prefs}")

    # Get current preferences
    current_prefs = get_user_preferences(uid)
    print(f"[chat_rag] Préférences actuelles pour {uid}: {current_prefs}")

    # ================= SOCIAL =================
    if is_social_message(user_text):
        answer = ask_with_evidence(
            question=user_text,
            evidence=None,
            history=history,
            mode="social"
        )

        conversation_memory[uid].append(f"User: {user_text}")
        conversation_memory[uid].append(f"Bot: {answer}")

        return {
            "answer": answer,
            "context_used": "SOCIAL",
            "pdf_used": False
        }

    # ================= BUILD USER PROFILE =================
    # Combine preferences with any existing profile data
    user_profile = {
        "niveau": current_prefs.get("level"),
        "budget": current_prefs.get("budget"),
        "domains": [current_prefs.get("domain")] if current_prefs.get("domain") else None,
        "competences": []
    }

    # ================= PDF MODE =================
    if pdf_upload.pdf_memory and pdf_upload.pdf_memory.strip():
        # Extract skills from PDF for context
        pdf_skills = extract_skill_vector(pdf_upload.pdf_memory, use_llm=True)

        # Add PDF competences to profile
        user_profile["competences"] = list(pdf_skills.get("skill_vector", {}).keys())

        # If no explicit level preference, use PDF-detected level
        if not user_profile["niveau"]:
            user_profile["niveau"] = pdf_skills.get("level_hint")

        # Get recommendations based on PDF skills AND user preferences
        rag_result = search_relevant_certifications(
            question=user_text,
            user_id=uid,
            top_k=10,
            user_profile=user_profile
        )

        # Update pdf_skills with any preference overrides
        if current_prefs.get("level"):
            pdf_skills["level_hint"] = current_prefs.get("level")

        # Build evidence combining PDF and graph results
        evidence = {
            "pdf_content": pdf_upload.pdf_memory[:3000],  # Truncate for context
            "pdf_skills": pdf_skills,
            "recommendations": rag_result.get("recommendations", []),
            "reasoning": rag_result.get("reasoning", {})
        }

        answer = ask_with_evidence(
            question=user_text,
            evidence=evidence,
            history=history,
            mode="pdf_with_graph"
        )

        conversation_memory[uid].append(f"User: {user_text}")
        conversation_memory[uid].append(f"Bot: {answer}")

        return {
            "answer": answer,
            "pdf_used": True,
            "context_used": "PDF_WITH_GRAPH",
            "skill_analysis": rag_result.get("skill_analysis", {}),
            "recommendations": rag_result.get("recommendations", []),
            "user_preferences": current_prefs
        }

    # ================= GRAPH REASONING =================
    rag_result = search_relevant_certifications(
        question=user_text,
        user_id=uid,
        top_k=10,
        user_profile=user_profile if any(user_profile.values()) else None
    )

    recommendations = rag_result.get("recommendations", [])
    skill_analysis = rag_result.get("skill_analysis", {})

    # Apply preference overrides to skill_analysis for LLM
    if current_prefs.get("level"):
        skill_analysis["level_hint"] = current_prefs.get("level")

    # DEBUG: Log first recommendation to verify all fields are present
    if recommendations:
        first_rec = recommendations[0]
        print(f"[DEBUG chat_rag] First recommendation: {first_rec.get('titre')} - niveau: {first_rec.get('niveau')}")

    evidence = {
        "skill_analysis": skill_analysis,
        "recommendations": recommendations,
        "reasoning": rag_result.get("reasoning", {})
    }

    answer = ask_with_evidence(
        question=user_text,
        evidence=evidence,
        history=history,
        mode="graph_reasoning"
    )

    conversation_memory[uid].append(f"User: {user_text}")
    conversation_memory[uid].append(f"Bot: {answer}")

    return {
        "answer": answer,
        "pdf_used": False,
        "context_used": "GRAPH_REASONING",
        "skill_analysis": skill_analysis,
        "recommendations": recommendations,
        "user_preferences": current_prefs
    }


@router.post("/reset-preferences")
def reset_preferences(req: ResetPreferencesRequest = None):
    """
    Reset user preferences (level, domain, budget) without clearing PDF or conversation.
    Useful when user wants to start fresh with different criteria.
    """
    global user_preferences
    uid = req.user_id if req else "anonymous"

    if uid in user_preferences:
        del user_preferences[uid]

    # Also clear anonymous
    if "anonymous" in user_preferences:
        del user_preferences["anonymous"]

    print(f"[chat_rag] Préférences réinitialisées pour {uid}")

    return {
        "message": "Preferences reset successfully",
        "user_id": uid
    }


@router.get("/preferences/{user_id}")
def get_preferences(user_id: str = "anonymous"):
    """
    Get current user preferences.
    """
    prefs = get_user_preferences(user_id)
    return {
        "user_id": user_id,
        "preferences": prefs
    }

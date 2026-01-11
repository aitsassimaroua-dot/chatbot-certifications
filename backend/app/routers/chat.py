from fastapi import APIRouter
from pydantic import BaseModel

from app.services.rag_service import search_relevant_certifications
from app.services.llm_service import llm

# Import du texte PDF
from app.routers.pdf_upload import pdf_memory

router = APIRouter(prefix="/chat-rag", tags=["chat-rag"])

class ChatRequest(BaseModel):
    question: str
    user_id: str | None = None


@router.post("/")
def chat_rag(req: ChatRequest):

    # ========== 1) Si le PDF contient du texte → ON L'UTILISE OBLIGATOIREMENT ==========
    if pdf_memory.strip():
        prompt = f"""
Tu es un expert en certifications Cloud, Data et DevOps.
Tu DOIS répondre UNIQUEMENT en utilisant le texte du PDF ci-dessous.

------------- PDF -------------
{pdf_memory}
--------------------------------

RÈGLES IMPORTANTES :
- N'invente AUCUNE certification.
- Liste EXACTEMENT les certifications présentes dans le PDF.
- Si le PDF ne contient pas de certifications, dis-le clairement.

QUESTION :
{req.question}
"""

        answer = llm.ask(prompt)
        return {
            "answer": answer,
            "pdf_used": True,
            "context_used": "PDF_ONLY"
        }

    # ========== 2) Sinon → on utilise RAG (Neo4j) ==========
    relevant = search_relevant_certifications(
        question=req.question,
        user_id=req.user_id
    )

    context_text = "\n\n".join([c["text"] for c in relevant])

    prompt = f"""
Voici les certifications trouvées :

{context_text}

Réponds à la question suivante :
{req.question}
"""

    answer = llm.ask(prompt)

    return {
        "answer": answer,
        "pdf_used": False,
        "context_used": relevant
    }

from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from PyPDF2 import PdfReader

router = APIRouter(prefix="/pdf", tags=["pdf"])

pdf_memory = ""
pdf_skill_analysis = None  # Cache skill analysis from last uploaded PDF


class ClearRequest(BaseModel):
    user_id: str | None = None


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global pdf_memory, pdf_skill_analysis

    try:
        reader = PdfReader(file.file)
    except Exception as e:
        print(f"[pdf_upload] Error reading PDF: {e}")
        return {
            "message": "Error reading PDF",
            "error": str(e),
            "words": 0,
            "skill_analysis": None
        }

    text = ""

    print("\n===================== DÉBUT EXTRACTION PDF =====================\n")

    for i, page in enumerate(reader.pages):
        try:
            extracted = page.extract_text() or ""
            print(f"--- Page {i+1} ({len(extracted)} chars) ---")
            text += extracted
        except Exception as e:
            print(f"[pdf_upload] Error extracting page {i+1}: {e}")

    print("===================== FIN EXTRACTION PDF =====================\n")
    print(f"[pdf_upload] Longueur totale texte extrait: {len(text)} caractères")

    pdf_memory = text.strip()

    # Extract skills immediately on upload (with error handling)
    try:
        print("[pdf_upload] Extracting skills from PDF...")
        # Lazy import to avoid loading models at startup
        from app.services.skill_extractor import extract_skill_vector
        pdf_skill_analysis = extract_skill_vector(pdf_memory, use_llm=True)
        print(f"[pdf_upload] Extracted skills: {pdf_skill_analysis.get('extracted_skills', [])}")
        print(f"[pdf_upload] Detected domains: {pdf_skill_analysis.get('domains', [])}")
        print(f"[pdf_upload] Level hint: {pdf_skill_analysis.get('level_hint')}")
    except Exception as e:
        print(f"[pdf_upload] Error extracting skills: {e}")
        import traceback
        traceback.print_exc()
        pdf_skill_analysis = {
            "extracted_skills": [],
            "skill_vector": {},
            "domains": [],
            "level_hint": None
        }

    return {
        "message": "PDF uploaded successfully",
        "words": len(text.split()),
        "characters": len(text),
        "preview": text[:300],
        "skill_analysis": pdf_skill_analysis
    }


@router.get("/analyze")
async def get_pdf_analysis():
    """
    Get skill analysis from the currently uploaded PDF.
    Returns cached analysis or empty if no PDF uploaded.
    """
    global pdf_memory, pdf_skill_analysis

    if not pdf_memory or not pdf_memory.strip():
        print("[pdf_upload] /analyze called but no PDF in memory")
        return {
            "has_pdf": False,
            "skill_analysis": None,
            "pdf_length": 0
        }

    # If no cached analysis, extract now
    if pdf_skill_analysis is None:
        print("[pdf_upload] /analyze - extracting skills (no cache)")
        from app.services.skill_extractor import extract_skill_vector
        pdf_skill_analysis = extract_skill_vector(pdf_memory, use_llm=True)

    print(f"[pdf_upload] /analyze returning: {len(pdf_skill_analysis.get('extracted_skills', []))} skills")

    return {
        "has_pdf": True,
        "skill_analysis": pdf_skill_analysis,
        "pdf_length": len(pdf_memory)
    }


@router.post("/clear")
async def clear_pdf(req: ClearRequest = None):
    """
    Clear PDF memory, skill analysis cache, AND conversation memory.
    This ensures subsequent queries don't use old CV data.
    """
    global pdf_memory, pdf_skill_analysis

    # Clear PDF content
    pdf_memory = ""

    # Clear skill analysis cache
    pdf_skill_analysis = None

    # Clear conversation memory to remove old PDF context
    from app.routers.chat_rag import clear_conversation_memory
    user_id = req.user_id if req else None
    clear_conversation_memory(user_id)

    print("[pdf_upload] PDF, skill analysis, and conversation memory cleared")

    return {
        "message": "PDF and conversation memory cleared",
        "skill_analysis": None
    }

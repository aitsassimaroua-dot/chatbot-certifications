# ================================
# SKILL EXTRACTION SERVICE
# Converts user text/CV into a weighted skill vector
# ================================

import re
from sentence_transformers import SentenceTransformer, util
from app.database import execute_query
from groq import Groq
import os

# Shared embedding model
model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# Groq client for LLM-based extraction
_groq_client = None

def get_groq_client():
    global _groq_client
    if _groq_client is None:
        _groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _groq_client


# ================================
# Load canonical skills from Neo4j
# ================================
_skills_cache = None
_skills_embeddings = None

def load_canonical_skills():
    """
    Extract all unique skills from certifications in Neo4j.
    Handles competences stored as either arrays or comma-separated strings.
    These form the canonical skill vocabulary.
    """
    global _skills_cache, _skills_embeddings

    if _skills_cache is not None:
        return _skills_cache, _skills_embeddings

    # Query handles both array and string formats
    query = """
    MATCH (c:Certification)
    WHERE c.competences IS NOT NULL
    WITH c.competences AS comp
    // Handle both list and string formats
    WITH CASE
        WHEN comp IS :: LIST<ANY> THEN comp
        ELSE split(toString(comp), ', ')
    END AS skills_list
    UNWIND skills_list AS skill
    WITH trim(toString(skill)) AS clean_skill
    WHERE clean_skill <> ''
    RETURN DISTINCT clean_skill AS skill
    ORDER BY skill
    """
    results = execute_query(query)

    skills = [r["skill"] for r in results if r["skill"]]

    if skills:
        embeddings = model.encode(skills, convert_to_tensor=True)
    else:
        embeddings = None

    _skills_cache = skills
    _skills_embeddings = embeddings

    return skills, embeddings


def refresh_skills_cache():
    """Force refresh of skills cache (call after Neo4j data changes)."""
    global _skills_cache, _skills_embeddings
    _skills_cache = None
    _skills_embeddings = None
    return load_canonical_skills()


# ================================
# Extract skills from text using LLM
# ================================
def extract_skills_with_llm(text: str) -> list[str]:
    """
    Use LLM to extract skills/technologies/competencies from text.
    SCOPE: Cloud, Data, and AI domains only.
    Works with CVs, job descriptions, or user queries.
    """
    client = get_groq_client()

    prompt = f"""Extract ONLY the specific technical skills/technologies mentioned in this text.
Do NOT add generic terms like "Cloud", "Data", or "AI" unless they are part of a specific technology name.

TEXT: {text[:3000]}

RULES:
- Extract specific technologies: AWS, Azure, Python, SQL, Spark, etc.
- Do NOT extract generic words like "cloud", "data", "ai" alone
- If no specific skills found, respond with: NONE

RESPOND WITH ONLY A COMMA-SEPARATED LIST. NO EXPLANATIONS.
Example: AWS, Python, SQL, Spark

SKILLS:"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You extract skills from text. Respond ONLY with a comma-separated list of skills. No explanations, no sentences, just skills separated by commas."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=200
        )

        raw = response.choices[0].message.content.strip()

        # If response is too long or contains sentences, it's not a proper list
        if len(raw) > 500 or "Based on" in raw or "Here" in raw or "following" in raw:
            # Fallback: try to extract skills using regex
            import re
            # Look for known skill patterns
            known_skills = ["AWS", "Azure", "GCP", "Python", "SQL", "Spark", "Hadoop",
                          "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "Pandas",
                          "Docker", "Kubernetes", "Airflow", "Kafka", "BigQuery",
                          "Redshift", "Snowflake", "Power BI", "Tableau", "R",
                          "Machine Learning", "Deep Learning", "NLP", "MLOps"]
            found = [s for s in known_skills if s.lower() in raw.lower()]
            return found if found else []

        if raw.upper() == "NONE" or not raw:
            return []

        # Parse comma-separated skills, clean up
        skills = []
        # Generic terms to filter out (NOT specific technologies)
        generic_terms = {"cloud", "data", "ai", "ia", "ml", "none", "n/a", "certification", "certifications"}

        for s in raw.split(","):
            skill = s.strip().strip("-").strip("•").strip()
            if not skill:
                continue
            # Skip short lowercase terms (R and C valid only if uppercase)
            if len(skill) <= 2 and skill.lower() == skill:
                continue
            if len(skill) > 50:
                continue
            if " is " in skill.lower() or " are " in skill.lower():
                continue
            if skill.lower() in generic_terms:
                continue
            skills.append(skill)

        return skills[:20]  # Limit to 20 skills

    except Exception as e:
        print(f"[skill_extractor] LLM extraction failed: {e}")
        return []


# ================================
# Map extracted skills to canonical skills
# ================================
def map_to_canonical_skills(extracted_skills: list[str], threshold: float = 0.6) -> dict[str, float]:
    """
    Map extracted skills to canonical skills using semantic similarity.
    Returns a dict of {canonical_skill: confidence_score}.
    """
    canonical_skills, skill_embeddings = load_canonical_skills()

    if not canonical_skills or skill_embeddings is None:
        return {}

    if not extracted_skills:
        return {}

    skill_vector = {}

    for skill in extracted_skills:
        skill_embed = model.encode(skill, convert_to_tensor=True)
        similarities = util.cos_sim(skill_embed, skill_embeddings)[0]

        # Find best match
        best_idx = similarities.argmax().item()
        best_score = similarities[best_idx].item()

        if best_score >= threshold:
            canonical = canonical_skills[best_idx]
            # Keep highest score if skill maps to same canonical
            if canonical not in skill_vector or skill_vector[canonical] < best_score:
                skill_vector[canonical] = best_score

    return skill_vector


# ================================
# Extract keywords for fallback matching
# SCOPE: Cloud, Data, AI only
# ================================

# Tech skills for Cloud, Data, and AI domains only
TECH_SKILLS = [
    # Programming for Data/AI
    "python", "r", "scala", "java", "sql",
    # Cloud platforms
    "aws", "azure", "gcp", "google cloud", "cloud", "ec2", "s3", "lambda",
    "cloud computing", "iaas", "paas", "saas", "serverless",
    # Cloud services
    "vpc", "iam", "cloudformation", "arm templates", "cloud functions",
    # Data Engineering
    "sql", "nosql", "mongodb", "postgresql", "mysql", "bigquery", "snowflake",
    "databricks", "spark", "hadoop", "kafka", "airflow",
    "etl", "data warehouse", "data lake", "data pipeline", "data modeling",
    # Data Analytics & BI
    "analytics", "bi", "power bi", "tableau", "looker", "data studio",
    "data analysis", "data visualization", "reporting",
    # AI/ML
    "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
    "nlp", "computer vision", "neural network", "ai", "artificial intelligence",
    "scikit-learn", "pandas", "numpy", "jupyter",
    # ML Ops
    "mlops", "sagemaker", "azure ml", "vertex ai", "kubeflow",
    # Big Data
    "big data", "hdfs", "hive", "presto", "redshift", "synapse"
]

# Domain keywords - Cloud, Data, AI only
DOMAIN_KEYWORDS = {
    "cloud": [
        "cloud", "aws", "azure", "gcp", "google cloud", "amazon web services",
        "cloud computing", "iaas", "paas", "saas", "serverless", "ec2", "s3",
        "lambda", "cloud engineer", "cloud architect", "solutions architect"
    ],
    "data": [
        "data", "sql", "database", "analytics", "bi", "power bi", "tableau",
        "etl", "warehouse", "bigquery", "spark", "hadoop", "data engineer",
        "data analyst", "data science", "big data", "data pipeline", "databricks"
    ],
    "ai": [
        "ai", "machine learning", "ml", "deep learning", "nlp", "neural",
        "tensorflow", "pytorch", "computer vision", "artificial intelligence",
        "data scientist", "ml engineer", "ia", "intelligence artificielle"
    ]
}


def extract_keywords(text: str) -> list[str]:
    """
    Extract PRIMARY domain from text based on keyword frequency.
    Returns domains sorted by relevance (most matches first).
    Only returns secondary domains if they have significant presence.
    """
    import re
    text_lower = text.lower()

    # Short keywords that need word boundary matching
    short_keywords = {"ai", "ia", "ml", "bi", "r"}

    # Count keyword matches per domain
    domain_scores = {"cloud": 0, "data": 0, "ai": 0}

    # Strong indicators (in title/objective) get higher weight
    strong_context_patterns = {
        "cloud": [r"cloud\s+computing", r"cloud\s+engineer", r"aws", r"azure", r"carriere.*cloud", r"debuter.*cloud"],
        "data": [r"data\s+engineer", r"data\s+scientist", r"data\s+analyst", r"big\s+data", r"carriere.*data"],
        "ai": [r"machine\s+learning", r"deep\s+learning", r"intelligence\s+artificielle", r"carriere.*ia", r"carriere.*ai"],
    }

    # Check strong indicators first (worth 5 points each)
    for domain, patterns in strong_context_patterns.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                domain_scores[domain] += 5

    # Count regular keyword matches (worth 1 point each)
    for domain, keywords in DOMAIN_KEYWORDS.items():
        for kw in keywords:
            if kw in short_keywords:
                pattern = r'\b' + re.escape(kw) + r'\b'
                if re.search(pattern, text_lower):
                    domain_scores[domain] += 1
            else:
                # Count occurrences
                count = text_lower.count(kw)
                if count > 0:
                    domain_scores[domain] += count

    # Get primary domain (highest score)
    max_score = max(domain_scores.values())
    if max_score == 0:
        return []

    # Return primary domain, plus secondary if it has at least 50% of primary score
    threshold = max_score * 0.5
    result = []
    for domain, score in sorted(domain_scores.items(), key=lambda x: x[1], reverse=True):
        if score >= threshold and score > 0:
            result.append(domain)

    # If primary domain is clearly dominant (2x secondary), only return primary
    if len(result) > 1:
        scores = [domain_scores[d] for d in result]
        if scores[0] >= scores[1] * 2:
            result = [result[0]]

    print(f"[skill_extractor] Domain scores: {domain_scores} -> {result}")
    return result


def extract_skills_from_text(text: str) -> list[str]:
    """
    Extract tech skills from text using keyword matching.
    Uses word boundary matching to avoid false positives.
    """
    import re
    text_lower = text.lower()
    found_skills = []

    # Generic terms to skip in fallback extraction
    skip_terms = {"cloud", "data", "ai", "r", "c"}

    for skill in TECH_SKILLS:
        # Skip generic single-word terms that cause false positives
        if skill in skip_terms:
            continue
        # Use word boundary matching for short terms
        if len(skill) <= 3:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill)
        else:
            # Longer terms can use simple substring match
            if skill in text_lower:
                found_skills.append(skill)

    return found_skills


# ================================
# Detect certifications already held
# ================================
KNOWN_CERTIFICATIONS = [
    # AWS
    ("aws solutions architect associate", "aws-solutions-architect-associate"),
    ("aws solutions architect professional", "aws-solutions-architect-pro"),
    ("aws certified cloud practitioner", "aws-cloud-practitioner"),
    ("aws cloud practitioner", "aws-cloud-practitioner"),
    ("aws sysops", "aws-sysops-associate"),
    ("aws developer associate", "aws-developer-associate"),
    ("aws data analytics", "aws-data-analytics"),
    ("aws machine learning specialty", "aws-ml-specialty"),
    # Azure
    ("azure fundamentals", "azure-fundamentals"),
    ("azure administrator", "azure-administrator"),
    ("azure solutions architect", "azure-solutions-architect"),
    ("azure data scientist", "azure-data-scientist"),
    ("azure developer", "azure-developer"),
    ("az-900", "azure-fundamentals"),
    ("az-104", "azure-administrator"),
    ("az-305", "azure-solutions-architect"),
    ("dp-100", "azure-data-scientist"),
    ("az-204", "azure-developer"),
    ("pl-300", "power-bi-analyst"),
    # GCP
    ("google cloud associate", "gcp-cloud-engineer"),
    ("google cloud professional", "gcp-professional-cloud-architect"),
    ("gcp professional data engineer", "gcp-data-engineer"),
    ("gcp machine learning engineer", "gcp-ml-engineer"),
    ("google professional data engineer", "gcp-data-engineer"),
    # Databricks
    ("databricks certified", "databricks-data-engineer"),
    ("databricks associate", "databricks-data-engineer"),
    ("databricks data engineer", "databricks-data-engineer-pro"),
    # Kubernetes
    ("cka", "cka-kubernetes"),
    ("ckad", "ckad-kubernetes"),
    ("certified kubernetes administrator", "cka-kubernetes"),
    ("certified kubernetes application developer", "ckad-kubernetes"),
    # Others
    ("terraform associate", "terraform-associate"),
    ("power bi", "power-bi-analyst"),
    ("tableau certified", "tableau-data-analyst"),
    ("snowflake", "snowflake-data-engineer"),
    ("tensorflow developer", "tensorflow-developer"),
    ("finops", "finops-practitioner"),
]


def detect_held_certifications(text: str) -> list[str]:
    """
    Detect certifications already mentioned as obtained in the CV.
    Returns list of certification IDs to exclude from recommendations.
    """
    text_lower = text.lower()
    held_certs = []

    # Patterns indicating certification is already held
    held_patterns = [
        r"certifi[ée]",
        r"obtenu",
        r"diplôm[ée]",
        r"certified",
        r"certification[s]?\s*(?:actuelle|obtenue|:)",
        r"certifications?\s*:\s*\n",
        r"\(\d{4}\)",  # Year in parentheses like (2022)
    ]

    # Check each known certification
    for cert_name, cert_id in KNOWN_CERTIFICATIONS:
        if cert_name in text_lower:
            # Check if it appears in a context suggesting it's already held
            # Find the position of the certification mention
            pos = text_lower.find(cert_name)
            # Look at surrounding context (200 chars before and after)
            start = max(0, pos - 200)
            end = min(len(text_lower), pos + len(cert_name) + 200)
            context = text_lower[start:end]

            # Check if any "held" pattern is in the context
            for pattern in held_patterns:
                if re.search(pattern, context):
                    if cert_id not in held_certs:
                        held_certs.append(cert_id)
                    break

    return held_certs


def detect_experience_years(text: str) -> int:
    """
    Detect total years of PROFESSIONAL experience from CV text.
    Excludes education/formation periods.
    Returns estimated years of experience.
    """
    text_lower = text.lower()

    # ============================================================
    # PRIORITY 1: Check for EXPLICIT beginner/student indicators
    # If found, return 0 IMMEDIATELY (no date parsing)
    # ============================================================
    strong_beginner_indicators = [
        "étudiant en", "étudiante en", "student in",
        "recherche de stage", "recherche stage", "cherche stage",
        "première expérience", "premier emploi",
        "jeune diplômé", "nouveau diplômé", "fresh graduate",
        "sans expérience", "pas d'expérience", "no experience",
        "débutant en", "débuter en", "je débute",
        "en dernière année", "dernière année de",
        "en formation", "currently studying",
        "stage de fin d'études", "internship"
    ]

    for indicator in strong_beginner_indicators:
        if indicator in text_lower:
            print(f"[detect_experience] Strong beginner indicator found: '{indicator}' -> 0 ans")
            return 0

    # ============================================================
    # PRIORITY 2: Look for EXPLICIT "X ans d'expérience" patterns
    # ============================================================
    years_patterns = [
        r'(\d+)\s*(?:ans?|years?)\s*(?:d\'?expérience|d\'experience|experience|of experience)',
        r'(?:expérience|experience)\s*(?:de\s*)?(\d+)\s*(?:ans?|years?)',
        r'(\d+)\+?\s*(?:ans?|years?)\s+(?:en tant que|as a|comme)',
    ]

    explicit_years = 0
    for pattern in years_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            try:
                years = int(match)
                if 0 < years < 40:
                    explicit_years = max(explicit_years, years)
            except:
                pass

    if explicit_years > 0:
        print(f"[detect_experience] Explicit years pattern found: {explicit_years} ans")
        return explicit_years

    # ============================================================
    # PRIORITY 3: Check for weaker student indicators
    # ============================================================
    weak_student_indicators = [
        "stage", "stagiaire", "intern",
        "licence", "master", "bachelor", "bts", "dut",
        "alternance", "apprenti",
    ]

    is_likely_student = any(ind in text_lower for ind in weak_student_indicators)

    # If student indicators found and no explicit years mentioned, return 0
    if is_likely_student:
        # Check if there's a REAL job title (not internship)
        real_job_patterns = [
            r"\b(?:cdi|cdd)\b",
            r"\bcontrat\s+(?:permanent|indéterminé)",
            r"\bfull[\s-]?time\s+(?:position|role)",
            r"\bsenior\s+\w+",
            r"\b(?:5|6|7|8|9|\d{2})\s*ans?\s*d'expérience",
        ]
        has_real_job = any(re.search(p, text_lower) for p in real_job_patterns)

        if not has_real_job:
            print(f"[detect_experience] Student indicators found, no real job -> 0 ans")
            return 0

    # ============================================================
    # PRIORITY 4: Date range parsing (ONLY for non-students)
    # ============================================================
    # Only real job titles, NOT certification names
    job_titles = [
        r"\bingénieur\s+(?:data|cloud|logiciel)",
        r"\bdevelop(?:per|eur)\b",
        r"\bdata\s+(?:engineer|analyst|scientist)\b",
        r"\bcloud\s+engineer\b",
        r"\bconsultant\s+(?:senior|data|cloud)",
        r"\bchef\s+de\s+projet\b",
        r"\btech\s+lead\b",
        r"\bdevops\b",
        r"\bsre\b",
    ]

    date_pattern = r'(\d{4})\s*[-–]\s*((?:\d{4})|present|présent|aujourd\'?hui?|actuel)'
    total_years = 0

    for job_pattern in job_titles:
        match = re.search(job_pattern, text_lower)
        if match:
            pos = match.start()
            # Look for date ranges within 150 chars
            context_start = max(0, pos - 150)
            context_end = min(len(text_lower), pos + 150)
            context = text_lower[context_start:context_end]

            # Exclude education context
            if any(edu in context for edu in ["formation", "études", "diplôme", "université", "école"]):
                continue

            date_matches = re.findall(date_pattern, context)
            for start_year, end_year in date_matches:
                try:
                    start = int(start_year)
                    if end_year.isdigit():
                        end = int(end_year)
                    else:
                        end = 2026  # Current year
                    years = end - start
                    if 0 < years < 20:
                        total_years = max(total_years, years)
                except:
                    pass

    print(f"[detect_experience] Final years detected: {total_years}")
    return total_years


# ================================
# Main extraction function
# ================================
def extract_skill_vector(text: str, use_llm: bool = True) -> dict:
    """
    Convert user text/CV into a skill vector.

    Returns:
        {
            "extracted_skills": ["Python", "AWS", ...],  # Raw extracted
            "skill_vector": {"Python": 0.95, ...},       # Mapped to canonical with scores
            "domains": ["cloud", "data"],                # Detected domains
            "level_hint": "intermediate",                # Detected experience level
            "held_certifications": ["aws-sa-associate"], # Certs already obtained
            "experience_years": 5                        # Years of experience
        }
    """
    result = {
        "extracted_skills": [],
        "skill_vector": {},
        "domains": [],
        "level_hint": None,
        "held_certifications": [],
        "experience_years": 0
    }

    if not text or not text.strip():
        return result

    # Detect certifications already held
    result["held_certifications"] = detect_held_certifications(text)

    # Detect years of experience
    result["experience_years"] = detect_experience_years(text)

    # 1. Extract skills using LLM (with keyword fallback)
    extracted = []
    if use_llm:
        extracted = extract_skills_with_llm(text)

    # Fallback to keyword extraction if LLM fails or returns empty
    if not extracted:
        extracted = extract_skills_from_text(text)

    result["extracted_skills"] = extracted

    # 2. Map to canonical skills
    if extracted:
        result["skill_vector"] = map_to_canonical_skills(extracted)

    # 3. Detect domains from keywords
    result["domains"] = extract_keywords(text)

    # 4. Detect experience level - use the experience_years already calculated
    experience_years = result["experience_years"]
    text_lower = text.lower()

    # Check for beginner indicators FIRST (highest priority)
    beginner_keywords = [
        "étudiant", "student", "stagiaire", "stage", "intern",
        "débutant", "beginner", "entry level", "junior",
        "apprendre", "découvrir", "première expérience",
        "jeune diplômé", "nouveau dans", "reconversion",
        "cherche stage", "recherche stage", "en formation",
        "dernière année", "première certification", "débuter"
    ]
    is_beginner = any(kw in text_lower for kw in beginner_keywords)

    # Set level based on experience years
    if is_beginner:
        # Beginner indicators ALWAYS override to débutant
        result["level_hint"] = "débutant"
        print(f"[skill_extractor] Beginner keywords detected -> niveau: débutant")
    elif experience_years >= 5:
        result["level_hint"] = "avancé"
    elif experience_years >= 2:
        result["level_hint"] = "intermédiaire"
    else:
        # 0-1 years = débutant
        result["level_hint"] = "débutant"

    # Override only for EXPLICIT senior job titles (NOT certification names)
    # "architect" alone is NOT a senior indicator (it's often a certification name like "Solutions Architect")
    senior_patterns = [
        r"\bsenior\s+(?:engineer|developer|data|cloud)",
        r"\blead\s+(?:engineer|developer|data|architect)",
        r"\bprincipal\s+(?:engineer|architect)",
        r"\bchef\s+de\s+projet",
        r"\btech\s+lead\b",
        r"\b(?:10|15|20)\s*ans?\s*d'expérience",
        r"\bexpert\s+(?:en|cloud|data|aws|azure)",
    ]

    # Only override to avancé if NOT a beginner and has senior patterns
    if not is_beginner:
        import re
        for pattern in senior_patterns:
            if re.search(pattern, text_lower):
                result["level_hint"] = "avancé"
                print(f"[skill_extractor] Senior pattern '{pattern}' detected -> niveau: avancé")
                break

    print(f"[skill_extractor] Expérience: {experience_years} ans, Niveau final: {result['level_hint']}")

    return result

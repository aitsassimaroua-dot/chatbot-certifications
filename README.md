# CertiProfile - AI Certification Recommender

**Chatbot intelligent de recommandation de certifications Cloud, Data et IA**


---

Lien vers le GitHub de Chaymae :  
https://github.com/Chaimae24203

## Table des Matières

1. [Description du Projet](#description-du-projet)
2. [Architecture Technique](#architecture-technique)
3. [Stack Technique](#stack-technique)
4. [Algorithme de Recommandation](#algorithme-de-recommandation)
5. [Structure du Projet](#structure-du-projet)
6. [Installation](#installation)
7. [Utilisation](#utilisation)
8. [API Reference](#api-reference)
9. [Démonstration](#démonstration)

---

## Description du Projet

CertiProfile est un assistant conversationnel intelligent qui analyse les profils professionnels et recommande des certifications adaptées. Le système utilise une approche hybride combinant:

- **Analyse de graphe de connaissances** (Neo4j) pour modéliser les relations entre compétences et certifications
- **RAG (Retrieval-Augmented Generation)** pour des recommandations contextuelles
- **LLM (Large Language Model)** pour des réponses naturelles et personnalisées

### Fonctionnalités Principales

| Fonctionnalité | Description |
|----------------|-------------|
| **Analyse de CV** | Extraction automatique des compétences depuis un PDF |
| **Détection de niveau** | Débutant (0-1 ans), Intermédiaire (2-4 ans), Avancé (5+ ans) |
| **Détection de domaine** | Cloud, Data, AI automatiquement identifiés |
| **Scoring intelligent** | Combinaison compétences (70%) + sémantique (30%) |
| **Exclusion automatique** | Les certifications déjà obtenues sont filtrées |
| **Mémoire conversationnelle** | Les préférences sont mémorisées dans la session |

---

## Architecture Technique

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React 18)                          │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────────────┐    │
│  │   ChatBox     │  │  PdfUploader  │  │  RecommendationPanel  │    │
│  │   (Messages)  │  │  (CV Upload)  │  │  (Top 10 Results)     │    │
│  └───────────────┘  └───────────────┘  └───────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                │ HTTP/REST
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       BACKEND (FastAPI)                              │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                      API Routers                             │    │
│  │  POST /chat-rag/     POST /pdf/upload    POST /pdf/clear    │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                │                                     │
│  ┌─────────────────────────────┴─────────────────────────────┐      │
│  │                    Services Layer                          │      │
│  │                                                            │      │
│  │  ┌──────────────────┐  ┌──────────────────┐               │      │
│  │  │  Skill Extractor │  │  Graph Reasoning │               │      │
│  │  │  - LLM extraction│  │  - Neo4j queries │               │      │
│  │  │  - Level detect  │  │  - Skill matching│               │      │
│  │  │  - Domain detect │  │  - Level/Domain  │               │      │
│  │  │  - Held certs    │  │    boosting      │               │      │
│  │  └──────────────────┘  └──────────────────┘               │      │
│  │                                                            │      │
│  │  ┌──────────────────┐  ┌──────────────────┐               │      │
│  │  │   RAG Service    │  │   LLM Service    │               │      │
│  │  │  - Embeddings    │  │  - Groq API      │               │      │
│  │  │  - Reranking     │  │  - Prompt eng.   │               │      │
│  │  └──────────────────┘  └──────────────────┘               │      │
│  └────────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
    ┌──────────┐        ┌──────────┐        ┌──────────────┐
    │  Neo4j   │        │   Groq   │        │  Sentence    │
    │  Graph   │        │   LLM    │        │ Transformers │
    │    DB    │        │ Llama3.1 │        │  Embeddings  │
    │ 71 certs │        │   8B     │        │   + Cross    │
    │          │        │          │        │   Encoder    │
    └──────────┘        └──────────┘        └──────────────┘
```

### Flux de Traitement

```
┌─────────┐     ┌─────────────┐     ┌──────────────┐     ┌─────────┐
│ Question│────▶│   Skill     │────▶│    Graph     │────▶│   LLM   │
│  / CV   │     │  Extractor  │     │  Reasoning   │     │ Response│
└─────────┘     └─────────────┘     └──────────────┘     └─────────┘
                     │                    │
                     ▼                    ▼
              ┌─────────────┐      ┌──────────────┐
              │ • Skills    │      │ • Query Neo4j│
              │ • Level     │      │ • Boost level│
              │ • Domains   │      │ • Boost domain│
              │ • Held certs│      │ • Rerank     │
              └─────────────┘      └──────────────┘
```

---

## Stack Technique

| Couche | Technologie | Version | Rôle |
|--------|-------------|---------|------|
| **Frontend** | React | 18.x | Interface utilisateur |
| | Vite | 5.x | Build tool |
| **Backend** | FastAPI | 0.104+ | API REST async |
| | Python | 3.10+ | Runtime |
| | PyPDF2 | 3.x | Extraction PDF |
| **Database** | Neo4j | 5.x | Graphe de connaissances |
| **AI/ML** | Groq (Llama 3.1 8B) | - | Génération de texte |
| | SentenceTransformers | 2.x | Embeddings sémantiques |
| | CrossEncoder | - | Reranking précis |

### Modèles ML Utilisés

| Modèle | Tâche | Performance |
|--------|-------|-------------|
| `all-mpnet-base-v2` | Embeddings | 768 dimensions, haute qualité |
| `ms-marco-MiniLM-L-6-v2` | Reranking | Optimisé pour Q&A |
| `llama-3.1-8b-instant` | Génération | Rapide, contexte 8K |

---

## Algorithme de Recommandation

### Formule de Scoring

```
Score_Final = α × Score_Compétences + (1-α) × Score_Sémantique
            + Boost_Niveau + Boost_Domaine

Paramètres:
- α = 0.7 (priorité aux compétences)
- Boost_Niveau:
  • Match exact: +60 points
  • Débutant → Intermédiaire: -50 points
  • Débutant → Avancé: -80 points
- Boost_Domaine:
  • Match: +40 points
  • Mismatch: -30 points
```

### Détection du Niveau

| Indicateur | Niveau détecté |
|------------|----------------|
| "étudiant", "stage", "débuter" | Débutant |
| 2-4 ans d'expérience | Intermédiaire |
| "senior", "lead", 5+ ans | Avancé |

### Pipeline de Traitement

1. **Extraction** → Compétences, niveau, domaines depuis le texte
2. **Query Neo4j** → Récupération des certifications candidates
3. **Filtrage** → Exclusion des certifications déjà obtenues
4. **Boosting** → Application des bonus niveau/domaine
5. **Semantic Rerank** → Affinement par similarité sémantique
6. **Top-K** → Sélection des 10 meilleures recommandations

---

## Structure du Projet

```
chatbot-certifications/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app entry point
│   │   ├── database.py             # Neo4j connection
│   │   ├── routers/
│   │   │   ├── chat_rag.py         # Main chat endpoint
│   │   │   └── pdf_upload.py       # PDF handling
│   │   └── services/
│   │       ├── skill_extractor.py  # CV/text analysis
│   │       ├── graph_reasoning.py  # Neo4j + scoring
│   │       ├── rag_service.py      # RAG orchestration
│   │       └── llm_service.py      # Groq LLM interface
│   ├── requirements.txt
│   └── .env                        # Environment variables
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx                 # Main React component
│   │   └── components/
│   │       ├── ChatBox.jsx         # Chat interface
│   │       ├── PdfUploader.jsx     # CV upload
│   │       └── RecommendationPanel.jsx  # Results display
│   ├── package.json
│   └── vite.config.js
│
├── kg/                             # Knowledge Graph
│   └── certifications.json         # 71 certifications data
│
└── README.md
```

---

## Installation

### Prérequis

- Python 3.10+
- Node.js 18+
- Neo4j Desktop ou Docker
- Compte Groq (gratuit)

### 1. Cloner le projet

```bash
git clone <repository_url>
cd chatbot-certifications
```

### 2. Backend

```bash
cd backend

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configuration

Créer `backend/.env`:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=votre_mot_de_passe
GROQ_API_KEY=votre_cle_groq
```

### 4. Frontend

```bash
cd frontend
npm install
```

### 5. Neo4j

1. Démarrer Neo4j Desktop
2. Créer une base de données
3. Importer les certifications depuis `kg/certifications.json`

---

## Utilisation

### Démarrer les services

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Accéder à l'application

- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs

### Exemples d'utilisation

1. **Sans CV**: "Je veux débuter en Cloud AWS"
2. **Avec CV**: Uploader un PDF puis "Quelles certifications pour moi?"
3. **Changer de niveau**: "niveau avancé" ou "niveau débutant"
4. **Changer de domaine**: "en Data" ou "en AI"

---

## API Reference

### POST /chat-rag/

Chat principal avec recommandations.

**Request:**
```json
{
  "question": "Je veux une certification Cloud débutant",
  "user_id": "optional_user_id"
}
```

**Response:**
```json
{
  "answer": "Pour débuter en Cloud, je recommande...",
  "recommendations": [
    {
      "titre": "AWS Certified Cloud Practitioner",
      "niveau": "Débutant",
      "domaine": "Cloud",
      "prix": 100,
      "duree": "40h",
      "combined_score": 142.5
    }
  ],
  "skill_analysis": {
    "level_hint": "débutant",
    "domains": ["cloud"],
    "experience_years": 0
  }
}
```

### POST /pdf/upload

Upload d'un CV pour analyse.

### POST /pdf/clear

Effacer le CV et réinitialiser la session.

### POST /chat-rag/reset-preferences

Réinitialiser les préférences niveau/domaine.

---

## Démonstration

### Scénario 1: Étudiant Cloud

1. Uploader un CV d'étudiant en informatique
2. Le système détecte: niveau=Débutant, domaine=Cloud
3. Recommandations: AWS Cloud Practitioner, Azure Fundamentals...

### Scénario 2: Data Engineer Senior

1. Uploader un CV avec 5+ ans d'expérience Data
2. Le système détecte: niveau=Avancé, domaine=Data
3. Recommandations: Databricks Professional, AWS Data Analytics...

### Scénario 3: Changement de préférences

1. "Certification Cloud débutant" → Résultats débutant
2. "Maintenant niveau avancé" → Résultats avancé
3. Les préférences sont mémorisées dans la session

---

## Ports Utilisés

| Service | Port | URL |
|---------|------|-----|
| Backend | 8000 | http://localhost:8000 |
| Frontend | 5173 | http://localhost:5173 |
| Neo4j | 7687 | bolt://localhost:7687 |

---

## Auteurs

Projet de fin d'études - Master Cloud/Data/IA

---

## Licence

MIT License

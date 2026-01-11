from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

# ============ CONFIGURATION ============

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "rania1106")
DATABASE = os.getenv("NEO4J_DATABASE", "certifications-db")

# Driver global (singleton)
_driver = None


# ============ FONCTION OBLIGATOIRE POUR LE RAG ============

def get_neo4j_driver():
    """
    Retourne une instance unique (singleton) du driver Neo4j.
    Nécessaire pour rag_service.py.
    """
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    return _driver


# ============ EXECUTION DES QUERIES ============

def execute_query(cypher_query, parameters=None):
    """
    Exécute une requête Cypher et retourne les résultats sous forme de liste.
    """
    driver = get_neo4j_driver()   # <-- Utilise le driver unique
    with driver.session(database=DATABASE) as session:
        result = session.run(cypher_query, parameters or {})
        return list(result)


# ============ FERMETURE PROPRE ============

def close_driver():
    """Ferme proprement le driver Neo4j (optionnel)."""
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None


# ============ SAUVEGARDE PROFIL ============

def save_profile(profile_data):
    """
    Sauvegarde un profil utilisateur dans Neo4j.
    """
    query = """
    MERGE (p:Profile {id: $id})
    SET p += $data
    RETURN p
    """
    return execute_query(query, {
        "id": profile_data["id"],
        "data": profile_data
    })

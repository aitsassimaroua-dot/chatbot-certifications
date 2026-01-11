# ============================================================
# GRAPH SCHEMA MANAGEMENT SERVICE
# Extends Neo4j schema with Skills, Domains, and Profile relationships
# ============================================================

from app.database import execute_query
from typing import Optional


# ============================================================
# SCHEMA INITIALIZATION
# ============================================================

def create_constraints():
    """Create unique constraints for new node types."""
    queries = [
        "CREATE CONSTRAINT domain_name_unique IF NOT EXISTS FOR (d:Domain) REQUIRE d.name IS UNIQUE",
        "CREATE CONSTRAINT skill_name_unique IF NOT EXISTS FOR (s:Skill) REQUIRE s.name IS UNIQUE",
        "CREATE INDEX profile_id_index IF NOT EXISTS FOR (p:Profile) ON (p.id)",
    ]
    for q in queries:
        try:
            execute_query(q)
            print(f"[graph_schema] Executed: {q[:50]}...")
        except Exception as e:
            print(f"[graph_schema] Warning: {e}")


def create_domain_nodes():
    """Create the 3 main domain nodes: Cloud, Data, AI."""
    domains = [
        {
            "name": "Cloud",
            "description": "Cloud Computing - AWS, Azure, GCP",
            "icon": "☁️",
            "keywords": ["cloud", "aws", "azure", "gcp", "google cloud", "serverless"]
        },
        {
            "name": "Data",
            "description": "Data Engineering, Analytics & BI",
            "icon": "📈",
            "keywords": ["data", "sql", "analytics", "bi", "etl", "warehouse", "spark"]
        },
        {
            "name": "AI",
            "description": "Artificial Intelligence & Machine Learning",
            "icon": "🧠",
            "keywords": ["ai", "ia", "machine learning", "ml", "deep learning", "nlp"]
        }
    ]

    query = """
    MERGE (d:Domain {name: $name})
    SET d.description = $description,
        d.icon = $icon,
        d.keywords = $keywords
    RETURN d.name AS name
    """

    for domain in domains:
        result = execute_query(query, domain)
        print(f"[graph_schema] Created/updated domain: {domain['name']}")

    return len(domains)


def extract_skills_from_certifications():
    """Extract all unique skills from certification competences and create Skill nodes."""
    query = """
    MATCH (c:Certification)
    WHERE c.competences IS NOT NULL
    WITH c,
         CASE
             WHEN c.competences IS :: LIST<ANY> THEN c.competences
             ELSE split(toString(c.competences), ', ')
         END AS skills_list
    UNWIND skills_list AS skill_name
    WITH trim(toString(skill_name)) AS clean_skill
    WHERE clean_skill <> '' AND size(clean_skill) > 1
    MERGE (s:Skill {name: clean_skill})
    ON CREATE SET s.created_at = datetime()
    RETURN count(DISTINCT s) AS skills_created
    """
    result = execute_query(query)
    count = result[0]["skills_created"] if result else 0
    print(f"[graph_schema] Created/updated {count} skill nodes")
    return count


def link_certifications_to_skills():
    """Create TEACHES relationships between Certifications and Skills."""
    query = """
    MATCH (c:Certification)
    WHERE c.competences IS NOT NULL
    WITH c,
         CASE
             WHEN c.competences IS :: LIST<ANY> THEN c.competences
             ELSE split(toString(c.competences), ', ')
         END AS skills_list
    UNWIND skills_list AS skill_name
    WITH c, trim(toString(skill_name)) AS clean_skill
    WHERE clean_skill <> '' AND size(clean_skill) > 1
    MATCH (s:Skill {name: clean_skill})
    MERGE (c)-[r:TEACHES]->(s)
    ON CREATE SET r.created_at = datetime()
    RETURN count(r) AS relationships_created
    """
    result = execute_query(query)
    count = result[0]["relationships_created"] if result else 0
    print(f"[graph_schema] Created {count} TEACHES relationships")
    return count


def link_certifications_to_domains():
    """Create BELONGS_TO relationships between Certifications and Domains."""
    # Cloud domain
    cloud_query = """
    MATCH (c:Certification), (d:Domain {name: 'Cloud'})
    WHERE toLower(c.domaine) CONTAINS 'cloud'
       OR toLower(c.domaine) CONTAINS 'aws'
       OR toLower(c.domaine) CONTAINS 'azure'
       OR toLower(c.domaine) CONTAINS 'gcp'
    MERGE (c)-[r:BELONGS_TO]->(d)
    ON CREATE SET r.created_at = datetime()
    RETURN count(r) AS count
    """

    # Data domain
    data_query = """
    MATCH (c:Certification), (d:Domain {name: 'Data'})
    WHERE toLower(c.domaine) CONTAINS 'data'
       OR toLower(c.domaine) CONTAINS 'analytics'
       OR toLower(c.domaine) CONTAINS 'bi'
    MERGE (c)-[r:BELONGS_TO]->(d)
    ON CREATE SET r.created_at = datetime()
    RETURN count(r) AS count
    """

    # AI domain
    ai_query = """
    MATCH (c:Certification), (d:Domain {name: 'AI'})
    WHERE toLower(c.domaine) CONTAINS 'ai'
       OR toLower(c.domaine) CONTAINS 'ia'
       OR toLower(c.domaine) CONTAINS 'machine learning'
       OR toLower(c.domaine) CONTAINS 'ml'
       OR toLower(c.domaine) CONTAINS 'intelligence'
    MERGE (c)-[r:BELONGS_TO]->(d)
    ON CREATE SET r.created_at = datetime()
    RETURN count(r) AS count
    """

    total = 0
    for name, query in [("Cloud", cloud_query), ("Data", data_query), ("AI", ai_query)]:
        result = execute_query(query)
        count = result[0]["count"] if result else 0
        total += count
        print(f"[graph_schema] Linked {count} certifications to {name} domain")

    return total


def link_skills_to_domains():
    """Create RELATED_TO relationships between Skills and Domains."""
    # Cloud skills
    cloud_skills = """
    MATCH (s:Skill), (d:Domain {name: 'Cloud'})
    WHERE toLower(s.name) CONTAINS 'aws'
       OR toLower(s.name) CONTAINS 'azure'
       OR toLower(s.name) CONTAINS 'gcp'
       OR toLower(s.name) CONTAINS 'cloud'
       OR toLower(s.name) CONTAINS 'kubernetes'
       OR toLower(s.name) CONTAINS 'docker'
       OR toLower(s.name) CONTAINS 'terraform'
       OR toLower(s.name) CONTAINS 'ec2'
       OR toLower(s.name) CONTAINS 's3'
       OR toLower(s.name) CONTAINS 'lambda'
    MERGE (s)-[:RELATED_TO]->(d)
    RETURN count(*) AS count
    """

    # Data skills
    data_skills = """
    MATCH (s:Skill), (d:Domain {name: 'Data'})
    WHERE toLower(s.name) CONTAINS 'sql'
       OR toLower(s.name) CONTAINS 'spark'
       OR toLower(s.name) CONTAINS 'hadoop'
       OR toLower(s.name) CONTAINS 'etl'
       OR toLower(s.name) CONTAINS 'databricks'
       OR toLower(s.name) CONTAINS 'bigquery'
       OR toLower(s.name) CONTAINS 'kafka'
       OR toLower(s.name) CONTAINS 'airflow'
       OR toLower(s.name) CONTAINS 'tableau'
       OR toLower(s.name) CONTAINS 'power bi'
    MERGE (s)-[:RELATED_TO]->(d)
    RETURN count(*) AS count
    """

    # AI skills
    ai_skills = """
    MATCH (s:Skill), (d:Domain {name: 'AI'})
    WHERE toLower(s.name) CONTAINS 'machine learning'
       OR toLower(s.name) CONTAINS 'deep learning'
       OR toLower(s.name) CONTAINS 'tensorflow'
       OR toLower(s.name) CONTAINS 'pytorch'
       OR toLower(s.name) CONTAINS 'nlp'
       OR toLower(s.name) CONTAINS 'neural'
       OR toLower(s.name) CONTAINS 'scikit'
       OR toLower(s.name) CONTAINS 'keras'
    MERGE (s)-[:RELATED_TO]->(d)
    RETURN count(*) AS count
    """

    total = 0
    for name, query in [("Cloud", cloud_skills), ("Data", data_skills), ("AI", ai_skills)]:
        result = execute_query(query)
        count = result[0]["count"] if result else 0
        total += count
        print(f"[graph_schema] Linked {count} skills to {name} domain")

    return total


def initialize_schema():
    """Run all schema initialization steps."""
    print("\n" + "="*60)
    print("INITIALIZING EXTENDED GRAPH SCHEMA")
    print("="*60 + "\n")

    create_constraints()
    create_domain_nodes()
    extract_skills_from_certifications()
    link_certifications_to_skills()
    link_certifications_to_domains()
    link_skills_to_domains()

    print("\n" + "="*60)
    print("SCHEMA INITIALIZATION COMPLETE")
    print("="*60 + "\n")

    return get_schema_stats()


# ============================================================
# PROFILE MANAGEMENT
# ============================================================

def link_profile_to_skill(profile_id: str, skill_name: str, confidence: float = 1.0, source: str = "cv"):
    """Create HAS_SKILL relationship between Profile and Skill."""
    query = """
    MATCH (p:Profile {id: $profile_id})
    MERGE (s:Skill {name: $skill_name})
    MERGE (p)-[r:HAS_SKILL]->(s)
    SET r.confidence = $confidence,
        r.source = $source,
        r.updated_at = datetime()
    RETURN p.id AS profile, s.name AS skill
    """
    return execute_query(query, {
        "profile_id": profile_id,
        "skill_name": skill_name,
        "confidence": confidence,
        "source": source
    })


def link_profile_to_domain(profile_id: str, domain_name: str, weight: float = 1.0):
    """Create INTERESTED_IN relationship between Profile and Domain."""
    query = """
    MATCH (p:Profile {id: $profile_id}), (d:Domain {name: $domain_name})
    MERGE (p)-[r:INTERESTED_IN]->(d)
    SET r.weight = $weight,
        r.updated_at = datetime()
    RETURN p.id AS profile, d.name AS domain
    """
    return execute_query(query, {
        "profile_id": profile_id,
        "domain_name": domain_name,
        "weight": weight
    })


def link_profile_to_certification(profile_id: str, cert_id: str, priority: int = 1):
    """Create TARGETS relationship between Profile and Certification."""
    query = """
    MATCH (p:Profile {id: $profile_id}), (c:Certification {id: $cert_id})
    MERGE (p)-[r:TARGETS]->(c)
    SET r.priority = $priority,
        r.added_at = datetime()
    RETURN p.id AS profile, c.titre AS certification
    """
    return execute_query(query, {
        "profile_id": profile_id,
        "cert_id": cert_id,
        "priority": priority
    })


def update_profile_skills(profile_id: str, skills: list[dict]):
    """
    Update all skills for a profile.
    skills: [{"name": "Python", "confidence": 0.9}, ...]
    """
    # First remove old HAS_SKILL relationships
    clear_query = """
    MATCH (p:Profile {id: $profile_id})-[r:HAS_SKILL]->()
    DELETE r
    """
    execute_query(clear_query, {"profile_id": profile_id})

    # Add new skills
    for skill in skills:
        link_profile_to_skill(
            profile_id,
            skill["name"],
            skill.get("confidence", 1.0),
            skill.get("source", "cv")
        )

    return len(skills)


def update_profile_domains(profile_id: str, domains: list[str]):
    """
    Update domain interests for a profile.
    domains: ["Cloud", "Data", "AI"]
    """
    # First remove old INTERESTED_IN relationships
    clear_query = """
    MATCH (p:Profile {id: $profile_id})-[r:INTERESTED_IN]->()
    DELETE r
    """
    execute_query(clear_query, {"profile_id": profile_id})

    # Add new domain interests
    for domain in domains:
        # Normalize domain name
        domain_normalized = domain.capitalize()
        if domain_normalized not in ["Cloud", "Data", "Ai"]:
            if "cloud" in domain.lower():
                domain_normalized = "Cloud"
            elif "data" in domain.lower():
                domain_normalized = "Data"
            else:
                domain_normalized = "AI"

        link_profile_to_domain(profile_id, domain_normalized)

    return len(domains)


# ============================================================
# GRAPH-BASED RECOMMENDATIONS
# ============================================================

def get_recommendations_by_skills(profile_id: str, limit: int = 10):
    """
    Get certification recommendations based on profile skills.
    Uses graph traversal: Profile -[:HAS_SKILL]-> Skill <-[:TEACHES]- Certification
    """
    query = """
    MATCH (p:Profile {id: $profile_id})-[hs:HAS_SKILL]->(s:Skill)<-[:TEACHES]-(c:Certification)
    WITH c,
         collect(DISTINCT s.name) AS matched_skills,
         sum(hs.confidence) AS skill_score
    OPTIONAL MATCH (c)-[:BELONGS_TO]->(d:Domain)
    RETURN
        c.id AS id,
        c.titre AS titre,
        c.domaine AS domaine,
        c.niveau AS niveau,
        c.prix AS prix,
        c.duree AS duree,
        c.objectif AS objectif,
        collect(DISTINCT d.name) AS domains,
        matched_skills,
        size(matched_skills) AS match_count,
        skill_score
    ORDER BY skill_score DESC, match_count DESC
    LIMIT $limit
    """
    return execute_query(query, {"profile_id": profile_id, "limit": limit})


def get_recommendations_by_domain(profile_id: str, limit: int = 10):
    """
    Get certification recommendations based on domain interests.
    Uses graph traversal: Profile -[:INTERESTED_IN]-> Domain <-[:BELONGS_TO]- Certification
    """
    query = """
    MATCH (p:Profile {id: $profile_id})-[i:INTERESTED_IN]->(d:Domain)<-[:BELONGS_TO]-(c:Certification)
    WITH c, d, i.weight AS domain_weight
    OPTIONAL MATCH (c)-[:TEACHES]->(s:Skill)
    RETURN
        c.id AS id,
        c.titre AS titre,
        c.domaine AS domaine,
        c.niveau AS niveau,
        c.prix AS prix,
        d.name AS matched_domain,
        domain_weight,
        collect(DISTINCT s.name)[0..5] AS sample_skills
    ORDER BY domain_weight DESC, c.prix ASC
    LIMIT $limit
    """
    return execute_query(query, {"profile_id": profile_id, "limit": limit})


def get_combined_recommendations(profile_id: str, limit: int = 10):
    """
    Get recommendations combining skill matching and domain interest.
    """
    query = """
    // Get profile's skills and domains
    MATCH (p:Profile {id: $profile_id})
    OPTIONAL MATCH (p)-[hs:HAS_SKILL]->(user_skill:Skill)
    OPTIONAL MATCH (p)-[i:INTERESTED_IN]->(user_domain:Domain)

    WITH p,
         collect(DISTINCT {skill: user_skill.name, confidence: hs.confidence}) AS user_skills,
         collect(DISTINCT {domain: user_domain.name, weight: i.weight}) AS user_domains

    // Find matching certifications
    MATCH (c:Certification)
    OPTIONAL MATCH (c)-[:TEACHES]->(cert_skill:Skill)
    OPTIONAL MATCH (c)-[:BELONGS_TO]->(cert_domain:Domain)

    WITH c, user_skills, user_domains,
         collect(DISTINCT cert_skill.name) AS cert_skills,
         collect(DISTINCT cert_domain.name) AS cert_domains

    // Calculate skill match score
    WITH c, user_skills, user_domains, cert_skills, cert_domains,
         [us IN user_skills WHERE us.skill IN cert_skills | us] AS matched_skills

    // Calculate domain match score
    WITH c, cert_skills, cert_domains, matched_skills,
         size(matched_skills) AS skill_match_count,
         reduce(s = 0.0, ms IN matched_skills | s + coalesce(ms.confidence, 1.0)) AS skill_score,
         [ud IN user_domains WHERE ud.domain IN cert_domains | ud] AS matched_domains

    WITH c, cert_skills, cert_domains, matched_skills, matched_domains,
         skill_match_count, skill_score,
         reduce(d = 0.0, md IN matched_domains | d + coalesce(md.weight, 1.0)) AS domain_score

    // Combined score: 60% skills + 40% domain
    WITH c, cert_skills, cert_domains,
         [ms IN matched_skills | ms.skill] AS matched_skill_names,
         [md IN matched_domains | md.domain] AS matched_domain_names,
         skill_match_count,
         (0.6 * skill_score + 0.4 * domain_score) AS combined_score

    WHERE combined_score > 0

    RETURN
        c.id AS id,
        c.titre AS titre,
        c.domaine AS domaine,
        c.niveau AS niveau,
        c.prix AS prix,
        c.duree AS duree,
        c.objectif AS objectif,
        cert_skills[0..5] AS competences,
        matched_skill_names AS matched_skills,
        matched_domain_names AS matched_domains,
        skill_match_count,
        round(combined_score * 100) / 100 AS relevance_score
    ORDER BY combined_score DESC, c.prix ASC
    LIMIT $limit
    """
    return execute_query(query, {"profile_id": profile_id, "limit": limit})


# ============================================================
# VALIDATION & STATS
# ============================================================

def get_schema_stats():
    """Get statistics about the graph schema."""
    stats_query = """
    MATCH (n)
    WITH labels(n)[0] AS NodeType, count(n) AS Count
    RETURN NodeType, Count
    ORDER BY Count DESC
    """
    node_stats = execute_query(stats_query)

    rel_query = """
    MATCH ()-[r]->()
    WITH type(r) AS RelationType, count(r) AS Count
    RETURN RelationType, Count
    ORDER BY Count DESC
    """
    rel_stats = execute_query(rel_query)

    return {
        "nodes": {r["NodeType"]: r["Count"] for r in node_stats},
        "relationships": {r["RelationType"]: r["Count"] for r in rel_stats}
    }


def validate_schema():
    """Validate the extended schema is properly configured."""
    validation = {
        "domains_exist": False,
        "skills_exist": False,
        "teaches_relationships": False,
        "belongs_to_relationships": False
    }

    # Check domains
    result = execute_query("MATCH (d:Domain) RETURN count(d) AS count")
    validation["domains_exist"] = result[0]["count"] >= 3

    # Check skills
    result = execute_query("MATCH (s:Skill) RETURN count(s) AS count")
    validation["skills_exist"] = result[0]["count"] > 0

    # Check TEACHES relationships
    result = execute_query("MATCH ()-[r:TEACHES]->() RETURN count(r) AS count")
    validation["teaches_relationships"] = result[0]["count"] > 0

    # Check BELONGS_TO relationships
    result = execute_query("MATCH ()-[r:BELONGS_TO]->() RETURN count(r) AS count")
    validation["belongs_to_relationships"] = result[0]["count"] > 0

    return validation


# ============================================================
# CLI RUNNER
# ============================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "init":
        stats = initialize_schema()
        print("\nFinal Statistics:")
        print(f"  Nodes: {stats['nodes']}")
        print(f"  Relationships: {stats['relationships']}")
    else:
        print("Usage: python -m app.services.graph_schema init")
        print("\nCurrent schema stats:")
        stats = get_schema_stats()
        print(f"  Nodes: {stats['nodes']}")
        print(f"  Relationships: {stats['relationships']}")

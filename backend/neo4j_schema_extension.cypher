// ============================================================
// NEO4J SCHEMA EXTENSION FOR AI CERTIFICATION RECOMMENDER
// Database: certifications-db
// ============================================================
// Run these scripts in order in Neo4j Browser or cypher-shell
// ============================================================


// ============================================================
// PART 1: CREATE DOMAIN NODES
// ============================================================

// Create the 3 main domain nodes
CREATE CONSTRAINT domain_name_unique IF NOT EXISTS
FOR (d:Domain) REQUIRE d.name IS UNIQUE;

MERGE (d:Domain {name: 'Cloud'})
SET d.description = 'Cloud Computing - AWS, Azure, GCP',
    d.icon = '☁️',
    d.keywords = ['cloud', 'aws', 'azure', 'gcp', 'google cloud', 'amazon', 'serverless', 'iaas', 'paas', 'saas'];

MERGE (d:Domain {name: 'Data'})
SET d.description = 'Data Engineering, Analytics & BI',
    d.icon = '📈',
    d.keywords = ['data', 'sql', 'analytics', 'bi', 'etl', 'warehouse', 'spark', 'hadoop', 'databricks', 'bigquery'];

MERGE (d:Domain {name: 'AI'})
SET d.description = 'Artificial Intelligence & Machine Learning',
    d.icon = '🧠',
    d.keywords = ['ai', 'ia', 'machine learning', 'ml', 'deep learning', 'nlp', 'neural', 'tensorflow', 'pytorch'];


// ============================================================
// PART 2: CREATE SKILL NODES FROM CERTIFICATION COMPETENCES
// ============================================================

// Create unique constraint for skills
CREATE CONSTRAINT skill_name_unique IF NOT EXISTS
FOR (s:Skill) REQUIRE s.name IS UNIQUE;

// Extract skills from certifications (handles both array and string formats)
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
ON CREATE SET s.created_at = datetime();


// ============================================================
// PART 3: LINK CERTIFICATIONS TO SKILLS (TEACHES)
// ============================================================

// Create TEACHES relationships between Certification and Skill
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
ON CREATE SET r.created_at = datetime();


// ============================================================
// PART 4: LINK CERTIFICATIONS TO DOMAINS (BELONGS_TO)
// ============================================================

// Link certifications to Cloud domain
MATCH (c:Certification), (d:Domain {name: 'Cloud'})
WHERE toLower(c.domaine) CONTAINS 'cloud'
   OR toLower(c.domaine) CONTAINS 'aws'
   OR toLower(c.domaine) CONTAINS 'azure'
   OR toLower(c.domaine) CONTAINS 'gcp'
MERGE (c)-[r:BELONGS_TO]->(d)
ON CREATE SET r.created_at = datetime();

// Link certifications to Data domain
MATCH (c:Certification), (d:Domain {name: 'Data'})
WHERE toLower(c.domaine) CONTAINS 'data'
   OR toLower(c.domaine) CONTAINS 'analytics'
   OR toLower(c.domaine) CONTAINS 'bi'
MERGE (c)-[r:BELONGS_TO]->(d)
ON CREATE SET r.created_at = datetime();

// Link certifications to AI domain
MATCH (c:Certification), (d:Domain {name: 'AI'})
WHERE toLower(c.domaine) CONTAINS 'ai'
   OR toLower(c.domaine) CONTAINS 'ia'
   OR toLower(c.domaine) CONTAINS 'machine learning'
   OR toLower(c.domaine) CONTAINS 'ml'
   OR toLower(c.domaine) CONTAINS 'intelligence'
MERGE (c)-[r:BELONGS_TO]->(d)
ON CREATE SET r.created_at = datetime();


// ============================================================
// PART 5: PROFILE SCHEMA EXTENSIONS
// ============================================================

// Add indexes for Profile relationships
CREATE INDEX profile_id_index IF NOT EXISTS FOR (p:Profile) ON (p.id);

// Example: Link Profile to Skills (HAS_SKILL)
// This will be called from the application when analyzing user CV/profile
// MATCH (p:Profile {id: $profile_id}), (s:Skill {name: $skill_name})
// MERGE (p)-[r:HAS_SKILL]->(s)
// SET r.confidence = $confidence, r.source = $source;

// Example: Link Profile to Domains (INTERESTED_IN)
// MATCH (p:Profile {id: $profile_id}), (d:Domain {name: $domain_name})
// MERGE (p)-[r:INTERESTED_IN]->(d)
// SET r.weight = $weight;

// Example: Link Profile to Target Certifications (TARGETS)
// MATCH (p:Profile {id: $profile_id}), (c:Certification {id: $cert_id})
// MERGE (p)-[r:TARGETS]->(c)
// SET r.priority = $priority, r.added_at = datetime();


// ============================================================
// PART 6: CREATE SKILL CATEGORIES (OPTIONAL ENHANCEMENT)
// ============================================================

// Categorize skills by associating them with domains
// Cloud skills
MATCH (s:Skill), (d:Domain {name: 'Cloud'})
WHERE toLower(s.name) CONTAINS 'aws'
   OR toLower(s.name) CONTAINS 'azure'
   OR toLower(s.name) CONTAINS 'gcp'
   OR toLower(s.name) CONTAINS 'cloud'
   OR toLower(s.name) CONTAINS 'ec2'
   OR toLower(s.name) CONTAINS 's3'
   OR toLower(s.name) CONTAINS 'lambda'
   OR toLower(s.name) CONTAINS 'kubernetes'
   OR toLower(s.name) CONTAINS 'docker'
   OR toLower(s.name) CONTAINS 'terraform'
MERGE (s)-[:RELATED_TO]->(d);

// Data skills
MATCH (s:Skill), (d:Domain {name: 'Data'})
WHERE toLower(s.name) CONTAINS 'sql'
   OR toLower(s.name) CONTAINS 'spark'
   OR toLower(s.name) CONTAINS 'hadoop'
   OR toLower(s.name) CONTAINS 'etl'
   OR toLower(s.name) CONTAINS 'databricks'
   OR toLower(s.name) CONTAINS 'bigquery'
   OR toLower(s.name) CONTAINS 'warehouse'
   OR toLower(s.name) CONTAINS 'kafka'
   OR toLower(s.name) CONTAINS 'airflow'
   OR toLower(s.name) CONTAINS 'tableau'
   OR toLower(s.name) CONTAINS 'power bi'
MERGE (s)-[:RELATED_TO]->(d);

// AI/ML skills
MATCH (s:Skill), (d:Domain {name: 'AI'})
WHERE toLower(s.name) CONTAINS 'machine learning'
   OR toLower(s.name) CONTAINS 'deep learning'
   OR toLower(s.name) CONTAINS 'tensorflow'
   OR toLower(s.name) CONTAINS 'pytorch'
   OR toLower(s.name) CONTAINS 'nlp'
   OR toLower(s.name) CONTAINS 'neural'
   OR toLower(s.name) CONTAINS 'scikit'
   OR toLower(s.name) CONTAINS 'keras'
   OR toLower(s.name) CONTAINS 'computer vision'
   OR toLower(s.name) CONTAINS 'sagemaker'
MERGE (s)-[:RELATED_TO]->(d);


// ============================================================
// VALIDATION QUERIES
// ============================================================

// 1. Count all node types
// MATCH (n) RETURN labels(n)[0] AS NodeType, count(n) AS Count ORDER BY Count DESC;

// 2. Count all relationship types
// MATCH ()-[r]->() RETURN type(r) AS RelationType, count(r) AS Count ORDER BY Count DESC;

// 3. View sample of new graph structure
// MATCH (c:Certification)-[:TEACHES]->(s:Skill)
// MATCH (c)-[:BELONGS_TO]->(d:Domain)
// RETURN c.titre AS Certification, d.name AS Domain, collect(DISTINCT s.name)[0..5] AS Skills
// LIMIT 10;

// 4. Find certifications by domain with skill count
// MATCH (d:Domain)<-[:BELONGS_TO]-(c:Certification)-[:TEACHES]->(s:Skill)
// RETURN d.name AS Domain, c.titre AS Certification, count(s) AS SkillCount
// ORDER BY d.name, SkillCount DESC;

// 5. Visualize full graph structure (limit for performance)
// MATCH path = (d:Domain)<-[:BELONGS_TO]-(c:Certification)-[:TEACHES]->(s:Skill)
// RETURN path LIMIT 50;

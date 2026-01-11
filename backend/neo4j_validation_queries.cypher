// ============================================================
// VALIDATION QUERIES FOR EXTENDED GRAPH SCHEMA
// Run these in Neo4j Browser after schema initialization
// ============================================================


// ============================================================
// 1. COUNT ALL NODE TYPES
// ============================================================
MATCH (n)
RETURN labels(n)[0] AS NodeType, count(n) AS Count
ORDER BY Count DESC;


// ============================================================
// 2. COUNT ALL RELATIONSHIP TYPES
// ============================================================
MATCH ()-[r]->()
RETURN type(r) AS RelationType, count(r) AS Count
ORDER BY Count DESC;


// ============================================================
// 3. VIEW DOMAINS WITH CERTIFICATION COUNTS
// ============================================================
MATCH (d:Domain)
OPTIONAL MATCH (d)<-[:BELONGS_TO]-(c:Certification)
RETURN d.name AS Domain, d.description AS Description, d.icon AS Icon, count(c) AS Certifications
ORDER BY Certifications DESC;


// ============================================================
// 4. VIEW TOP SKILLS BY CERTIFICATION COUNT
// ============================================================
MATCH (s:Skill)<-[:TEACHES]-(c:Certification)
RETURN s.name AS Skill, count(c) AS TaughtInCertifications
ORDER BY TaughtInCertifications DESC
LIMIT 20;


// ============================================================
// 5. VIEW SAMPLE CERTIFICATIONS WITH SKILLS AND DOMAINS
// ============================================================
MATCH (c:Certification)-[:TEACHES]->(s:Skill)
OPTIONAL MATCH (c)-[:BELONGS_TO]->(d:Domain)
WITH c, d, collect(DISTINCT s.name)[0..5] AS Skills
RETURN
    c.titre AS Certification,
    c.niveau AS Level,
    c.prix AS Price,
    d.name AS Domain,
    Skills
LIMIT 15;


// ============================================================
// 6. VIEW SKILL-DOMAIN RELATIONSHIPS
// ============================================================
MATCH (s:Skill)-[:RELATED_TO]->(d:Domain)
RETURN d.name AS Domain, collect(s.name)[0..10] AS Skills, count(s) AS TotalSkills
ORDER BY TotalSkills DESC;


// ============================================================
// 7. FIND CERTIFICATIONS BY DOMAIN (GRAPH TRAVERSAL)
// ============================================================
MATCH (d:Domain {name: 'Cloud'})<-[:BELONGS_TO]-(c:Certification)
RETURN c.titre AS Certification, c.niveau AS Level, c.prix AS Price
ORDER BY c.prix ASC
LIMIT 10;


// ============================================================
// 8. FIND SKILLS TAUGHT BY MOST CERTIFICATIONS (POPULAR SKILLS)
// ============================================================
MATCH (s:Skill)<-[:TEACHES]-(c:Certification)
WITH s, count(c) AS certCount
WHERE certCount > 1
MATCH (s)-[:RELATED_TO]->(d:Domain)
RETURN s.name AS Skill, d.name AS Domain, certCount AS Certifications
ORDER BY certCount DESC
LIMIT 20;


// ============================================================
// 9. VISUALIZE GRAPH STRUCTURE (SAMPLE)
// Returns data for visualization in Neo4j Browser
// ============================================================
MATCH path = (d:Domain)<-[:BELONGS_TO]-(c:Certification)-[:TEACHES]->(s:Skill)
RETURN path
LIMIT 50;


// ============================================================
// 10. FULL SCHEMA VISUALIZATION
// Shows all node types and their relationships
// ============================================================
CALL db.schema.visualization();


// ============================================================
// 11. CHECK PROVIDER RELATIONSHIPS (EXISTING)
// ============================================================
MATCH (c:Certification)-[:PROVIDED_BY]->(p:Provider)
RETURN p.name AS Provider, count(c) AS Certifications
ORDER BY Certifications DESC;


// ============================================================
// 12. EXAMPLE: PROFILE-BASED RECOMMENDATION QUERY
// (After creating a profile with skills)
// ============================================================
// First create a test profile:
// MERGE (p:Profile {id: 'test-user-1'})
// SET p.name = 'Test User', p.email = 'test@example.com';

// Link profile to skills:
// MATCH (p:Profile {id: 'test-user-1'})
// MERGE (s1:Skill {name: 'Python'})
// MERGE (s2:Skill {name: 'AWS'})
// MERGE (p)-[:HAS_SKILL {confidence: 0.9}]->(s1)
// MERGE (p)-[:HAS_SKILL {confidence: 0.8}]->(s2);

// Get recommendations:
// MATCH (p:Profile {id: 'test-user-1'})-[hs:HAS_SKILL]->(s:Skill)<-[:TEACHES]-(c:Certification)
// RETURN c.titre AS Certification, collect(s.name) AS MatchedSkills, sum(hs.confidence) AS Score
// ORDER BY Score DESC
// LIMIT 5;


// ============================================================
// 13. CERTIFICATION SIMILARITY BY SHARED SKILLS
// ============================================================
MATCH (c1:Certification)-[:TEACHES]->(s:Skill)<-[:TEACHES]-(c2:Certification)
WHERE c1.id < c2.id
WITH c1, c2, count(s) AS sharedSkills, collect(s.name)[0..3] AS skills
WHERE sharedSkills >= 2
RETURN
    c1.titre AS Cert1,
    c2.titre AS Cert2,
    sharedSkills AS SharedSkillCount,
    skills AS SampleSharedSkills
ORDER BY sharedSkills DESC
LIMIT 10;

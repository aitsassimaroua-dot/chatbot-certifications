// ============================================================
// CertiProfile - Additional Certifications (25 new)
// Database: certifications-db
// Existing: 25 certifications | Target: 50 total
// Domains: Cloud, Data, AI only
// ============================================================

// ============================================================
// CLOUD COMPUTING CERTIFICATIONS (9 new)
// ============================================================

MERGE (c:Certification {id: "aws-solutions-architect-pro"})
SET c.titre = "AWS Solutions Architect Professional",
    c.domaine = "Cloud",
    c.niveau = "Avancé",
    c.objectif = "Concevoir des applications distribuées complexes et des systèmes multi-comptes sur AWS.",
    c.competences = ["AWS", "Architecture Cloud", "Multi-Account", "Disaster Recovery", "Cost Optimization", "Migration"],
    c.duree = "12 mois",
    c.prix = 300,
    c.budget = 300,
    c.url = "https://aws.amazon.com/certification/certified-solutions-architect-professional/",
    c.langues = ["Anglais", "Français"],
    c.temps_par_semaine = 10;

MERGE (c:Certification {id: "aws-sysops-associate"})
SET c.titre = "AWS SysOps Administrator Associate",
    c.domaine = "Cloud",
    c.niveau = "Intermédiaire",
    c.objectif = "Gérer et exploiter des systèmes sur AWS avec monitoring et automatisation.",
    c.competences = ["AWS", "CloudWatch", "Auto Scaling", "Systems Manager", "Backup", "Monitoring"],
    c.duree = "5 mois",
    c.prix = 150,
    c.budget = 150,
    c.url = "https://aws.amazon.com/certification/certified-sysops-admin-associate/",
    c.langues = ["Anglais"],
    c.temps_par_semaine = 8;

MERGE (c:Certification {id: "azure-solutions-architect"})
SET c.titre = "Microsoft Azure Solutions Architect Expert (AZ-305)",
    c.domaine = "Cloud",
    c.niveau = "Avancé",
    c.objectif = "Concevoir des solutions cloud Azure répondant aux exigences métier et techniques.",
    c.competences = ["Azure", "Architecture Cloud", "Governance", "Hybrid Cloud", "Security", "High Availability"],
    c.duree = "12 mois",
    c.prix = 330,
    c.budget = 330,
    c.url = "https://learn.microsoft.com/certifications/azure-solutions-architect/",
    c.langues = ["Anglais", "Français"],
    c.temps_par_semaine = 10;

MERGE (c:Certification {id: "azure-developer"})
SET c.titre = "Microsoft Azure Developer Associate (AZ-204)",
    c.domaine = "Cloud",
    c.niveau = "Intermédiaire",
    c.objectif = "Développer des solutions cloud Azure incluant compute, stockage et sécurité.",
    c.competences = ["Azure", "Azure Functions", "App Service", "Cosmos DB", "Azure Storage", "Azure SDK"],
    c.duree = "5 mois",
    c.prix = 165,
    c.budget = 165,
    c.url = "https://learn.microsoft.com/certifications/azure-developer/",
    c.langues = ["Anglais"],
    c.temps_par_semaine = 8;

MERGE (c:Certification {id: "gcp-professional-cloud-architect"})
SET c.titre = "Google Professional Cloud Architect",
    c.domaine = "Cloud",
    c.niveau = "Avancé",
    c.objectif = "Concevoir, développer et gérer des solutions cloud robustes et évolutives sur GCP.",
    c.competences = ["GCP", "Architecture Cloud", "BigQuery", "Cloud Spanner", "Security", "Migration"],
    c.duree = "12 mois",
    c.prix = 200,
    c.budget = 200,
    c.url = "https://cloud.google.com/certification/cloud-architect",
    c.langues = ["Anglais"],
    c.temps_par_semaine = 10;

MERGE (c:Certification {id: "cka-kubernetes"})
SET c.titre = "Certified Kubernetes Administrator (CKA)",
    c.domaine = "Cloud",
    c.niveau = "Intermédiaire",
    c.objectif = "Administrer des clusters Kubernetes en production avec gestion des workloads.",
    c.competences = ["Kubernetes", "Docker", "Container Orchestration", "kubectl", "YAML", "Helm"],
    c.duree = "4 mois",
    c.prix = 395,
    c.budget = 395,
    c.url = "https://www.cncf.io/certification/cka/",
    c.langues = ["Anglais"],
    c.temps_par_semaine = 10;

MERGE (c:Certification {id: "ckad-kubernetes"})
SET c.titre = "Certified Kubernetes Application Developer (CKAD)",
    c.domaine = "Cloud",
    c.niveau = "Intermédiaire",
    c.objectif = "Concevoir et déployer des applications cloud-native sur Kubernetes.",
    c.competences = ["Kubernetes", "Docker", "Microservices", "Pod Design", "Services", "ConfigMaps"],
    c.duree = "3 mois",
    c.prix = 395,
    c.budget = 395,
    c.url = "https://www.cncf.io/certification/ckad/",
    c.langues = ["Anglais"],
    c.temps_par_semaine = 8;

MERGE (c:Certification {id: "terraform-associate"})
SET c.titre = "HashiCorp Terraform Associate",
    c.domaine = "Cloud",
    c.niveau = "Intermédiaire",
    c.objectif = "Maîtriser l'Infrastructure as Code avec Terraform pour le multi-cloud.",
    c.competences = ["Terraform", "Infrastructure as Code", "HCL", "AWS", "Azure", "GCP"],
    c.duree = "3 mois",
    c.prix = 70,
    c.budget = 70,
    c.url = "https://www.hashicorp.com/certification/terraform-associate",
    c.langues = ["Anglais"],
    c.temps_par_semaine = 6;

MERGE (c:Certification {id: "finops-practitioner"})
SET c.titre = "FinOps Certified Practitioner",
    c.domaine = "Cloud",
    c.niveau = "Intermédiaire",
    c.objectif = "Optimiser les coûts cloud et établir des pratiques FinOps.",
    c.competences = ["FinOps", "Cloud Cost Management", "AWS", "Azure", "GCP", "Budgeting"],
    c.duree = "2 mois",
    c.prix = 300,
    c.budget = 300,
    c.url = "https://www.finops.org/certification/",
    c.langues = ["Anglais"],
    c.temps_par_semaine = 5;


// ============================================================
// DATA ENGINEERING & DATA SCIENCE CERTIFICATIONS (8 new)
// ============================================================

MERGE (c:Certification {id: "databricks-data-engineer-pro"})
SET c.titre = "Databricks Certified Data Engineer Professional",
    c.domaine = "Data",
    c.niveau = "Avancé",
    c.objectif = "Concevoir des solutions de données avancées et des architectures lakehouse.",
    c.competences = ["Databricks", "Apache Spark", "Delta Lake", "Data Modeling", "Performance Tuning", "Unity Catalog"],
    c.duree = "8 mois",
    c.prix = 200,
    c.budget = 200,
    c.url = "https://www.databricks.com/learn/certification/data-engineer-professional",
    c.langues = ["Anglais"],
    c.temps_par_semaine = 10;

MERGE (c:Certification {id: "snowflake-data-engineer"})
SET c.titre = "SnowPro Advanced: Data Engineer",
    c.domaine = "Data",
    c.niveau = "Avancé",
    c.objectif = "Concevoir des pipelines de données complexes sur Snowflake.",
    c.competences = ["Snowflake", "SQL", "Snowpipe", "Streams", "Tasks", "Data Sharing", "Performance"],
    c.duree = "6 mois",
    c.prix = 375,
    c.budget = 375,
    c.url = "https://www.snowflake.com/certifications/",
    c.langues = ["Anglais"],
    c.temps_par_semaine = 8;

MERGE (c:Certification {id: "gcp-data-engineer"})
SET c.titre = "Google Professional Data Engineer",
    c.domaine = "Data",
    c.niveau = "Avancé",
    c.objectif = "Concevoir et construire des systèmes de traitement de données sur GCP.",
    c.competences = ["GCP", "BigQuery", "Dataflow", "Pub/Sub", "Cloud Storage", "Dataproc", "SQL"],
    c.duree = "8 mois",
    c.prix = 200,
    c.budget = 200,
    c.url = "https://cloud.google.com/certification/data-engineer",
    c.langues = ["Anglais"],
    c.temps_par_semaine = 10;

MERGE (c:Certification {id: "aws-data-analytics"})
SET c.titre = "AWS Certified Data Analytics Specialty",
    c.domaine = "Data",
    c.niveau = "Avancé",
    c.objectif = "Concevoir des solutions analytiques avancées avec les services AWS.",
    c.competences = ["AWS", "Kinesis", "EMR", "Redshift", "QuickSight", "Elasticsearch", "Data Lakes"],
    c.duree = "8 mois",
    c.prix = 300,
    c.budget = 300,
    c.url = "https://aws.amazon.com/certification/certified-data-analytics-specialty/",
    c.langues = ["Anglais"],
    c.temps_par_semaine = 10;

MERGE (c:Certification {id: "dbt-analytics-engineering"})
SET c.titre = "dbt Analytics Engineering Certification",
    c.domaine = "Data",
    c.niveau = "Intermédiaire",
    c.objectif = "Maîtriser dbt pour la transformation de données et l'analytics engineering.",
    c.competences = ["dbt", "SQL", "Data Modeling", "Jinja", "Git", "Data Transformation"],
    c.duree = "3 mois",
    c.prix = 200,
    c.budget = 200,
    c.url = "https://www.getdbt.com/certifications/",
    c.langues = ["Anglais"],
    c.temps_par_semaine = 6;

MERGE (c:Certification {id: "airflow-fundamentals"})
SET c.titre = "Apache Airflow Fundamentals",
    c.domaine = "Data",
    c.niveau = "Intermédiaire",
    c.objectif = "Orchestrer des workflows de données avec Apache Airflow.",
    c.competences = ["Apache Airflow", "Python", "DAGs", "ETL", "Scheduling", "Operators"],
    c.duree = "2 mois",
    c.prix = 150,
    c.budget = 150,
    c.url = "https://www.astronomer.io/certification/",
    c.langues = ["Anglais"],
    c.temps_par_semaine = 5;

MERGE (c:Certification {id: "tableau-data-analyst"})
SET c.titre = "Tableau Certified Data Analyst",
    c.domaine = "Data",
    c.niveau = "Intermédiaire",
    c.objectif = "Créer des visualisations de données et tableaux de bord avec Tableau.",
    c.competences = ["Tableau", "Data Visualization", "Dashboard Design", "SQL", "Data Analysis"],
    c.duree = "3 mois",
    c.prix = 250,
    c.budget = 250,
    c.url = "https://www.tableau.com/learn/certification",
    c.langues = ["Anglais", "Français"],
    c.temps_par_semaine = 6;

MERGE (c:Certification {id: "power-bi-analyst"})
SET c.titre = "Microsoft Power BI Data Analyst (PL-300)",
    c.domaine = "Data",
    c.niveau = "Intermédiaire",
    c.objectif = "Concevoir des rapports et tableaux de bord avec Power BI.",
    c.competences = ["Power BI", "DAX", "Data Modeling", "SQL", "Data Visualization", "Azure"],
    c.duree = "4 mois",
    c.prix = 165,
    c.budget = 165,
    c.url = "https://learn.microsoft.com/certifications/power-bi-data-analyst-associate/",
    c.langues = ["Anglais", "Français"],
    c.temps_par_semaine = 6;


// ============================================================
// AI & MACHINE LEARNING CERTIFICATIONS (8 new)
// ============================================================

MERGE (c:Certification {id: "gcp-ml-engineer"})
SET c.titre = "Google Professional Machine Learning Engineer",
    c.domaine = "AI",
    c.niveau = "Avancé",
    c.objectif = "Concevoir et mettre en production des modèles ML sur Google Cloud.",
    c.competences = ["GCP", "TensorFlow", "Vertex AI", "MLOps", "BigQuery ML", "AutoML", "Feature Store"],
    c.duree = "10 mois",
    c.prix = 200,
    c.budget = 200,
    c.url = "https://cloud.google.com/certification/machine-learning-engineer",
    c.langues = ["Anglais"],
    c.temps_par_semaine = 12;

MERGE (c:Certification {id: "aws-ml-specialty"})
SET c.titre = "AWS Certified Machine Learning Specialty",
    c.domaine = "AI",
    c.niveau = "Avancé",
    c.objectif = "Concevoir et déployer des solutions ML sur AWS avec SageMaker.",
    c.competences = ["AWS", "SageMaker", "Machine Learning", "Deep Learning", "MLOps", "Feature Engineering"],
    c.duree = "10 mois",
    c.prix = 300,
    c.budget = 300,
    c.url = "https://aws.amazon.com/certification/certified-machine-learning-specialty/",
    c.langues = ["Anglais"],
    c.temps_par_semaine = 12;

MERGE (c:Certification {id: "azure-data-scientist"})
SET c.titre = "Microsoft Azure Data Scientist Associate (DP-100)",
    c.domaine = "AI",
    c.niveau = "Intermédiaire",
    c.objectif = "Appliquer des techniques de data science et ML avec Azure Machine Learning.",
    c.competences = ["Azure ML", "Python", "Scikit-learn", "AutoML", "MLOps", "Responsible AI"],
    c.duree = "6 mois",
    c.prix = 165,
    c.budget = 165,
    c.url = "https://learn.microsoft.com/certifications/azure-data-scientist/",
    c.langues = ["Anglais", "Français"],
    c.temps_par_semaine = 8;

MERGE (c:Certification {id: "tensorflow-developer"})
SET c.titre = "TensorFlow Developer Certificate",
    c.domaine = "AI",
    c.niveau = "Intermédiaire",
    c.objectif = "Construire et entraîner des réseaux de neurones avec TensorFlow.",
    c.competences = ["TensorFlow", "Keras", "Python", "Deep Learning", "CNN", "RNN", "NLP"],
    c.duree = "4 mois",
    c.prix = 100,
    c.budget = 100,
    c.url = "https://www.tensorflow.org/certificate",
    c.langues = ["Anglais"],
    c.temps_par_semaine = 8;

MERGE (c:Certification {id: "deeplearning-ai-specialization"})
SET c.titre = "Deep Learning Specialization (Andrew Ng)",
    c.domaine = "AI",
    c.niveau = "Intermédiaire",
    c.objectif = "Maîtriser les fondamentaux du deep learning avec les réseaux de neurones.",
    c.competences = ["Deep Learning", "Neural Networks", "CNN", "RNN", "Python", "TensorFlow"],
    c.duree = "5 mois",
    c.prix = 49,
    c.budget = 49,
    c.url = "https://www.coursera.org/specializations/deep-learning",
    c.langues = ["Anglais"],
    c.temps_par_semaine = 6;

MERGE (c:Certification {id: "huggingface-nlp"})
SET c.titre = "Hugging Face NLP Course",
    c.domaine = "AI",
    c.niveau = "Intermédiaire",
    c.objectif = "Maîtriser le NLP moderne avec Transformers et Hugging Face.",
    c.competences = ["NLP", "Transformers", "Hugging Face", "BERT", "GPT", "Python", "Fine-tuning"],
    c.duree = "3 mois",
    c.prix = 0,
    c.budget = 0,
    c.url = "https://huggingface.co/learn/nlp-course",
    c.langues = ["Anglais"],
    c.temps_par_semaine = 5;

MERGE (c:Certification {id: "generative-ai-google"})
SET c.titre = "Google Generative AI Learning Path",
    c.domaine = "AI",
    c.niveau = "Intermédiaire",
    c.objectif = "Comprendre et utiliser les modèles d'IA générative avec Google Cloud.",
    c.competences = ["Generative AI", "LLMs", "Prompt Engineering", "Vertex AI", "PaLM", "Gemini"],
    c.duree = "2 mois",
    c.prix = 0,
    c.budget = 0,
    c.url = "https://cloud.google.com/learn/training/machinelearning-ai",
    c.langues = ["Anglais"],
    c.temps_par_semaine = 4;

MERGE (c:Certification {id: "mlops-specialization"})
SET c.titre = "Machine Learning Engineering for Production (MLOps)",
    c.domaine = "AI",
    c.niveau = "Avancé",
    c.objectif = "Mettre en production des modèles ML avec les pratiques MLOps.",
    c.competences = ["MLOps", "ML Pipelines", "TensorFlow Extended", "Model Monitoring", "CI/CD for ML", "Kubernetes"],
    c.duree = "6 mois",
    c.prix = 49,
    c.budget = 49,
    c.url = "https://www.coursera.org/specializations/machine-learning-engineering-for-production-mlops",
    c.langues = ["Anglais"],
    c.temps_par_semaine = 8;


// ============================================================
// VERIFICATION - Run after import:
// MATCH (c:Certification) RETURN c.domaine, count(*) ORDER BY count(*) DESC;
// MATCH (c:Certification) RETURN count(*) as total;
// ============================================================

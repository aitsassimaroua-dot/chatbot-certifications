from app.database import get_recommendations_from_db

certifications = get_recommendations_from_db()

print(f"Nombre de certifications : {len(certifications)}")
for c in certifications:
    print(f"- {c['titre']} ({c['difficulte']})")

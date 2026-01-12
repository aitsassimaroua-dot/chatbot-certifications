import "./RecommendationPanel.css";

function RecommendationCard({ cert, rank }) {
  const title = cert.titre || cert.name || "Certification";
  const niveau = cert.niveau || "N/A";
  const prix = cert.prix != null ? `${cert.prix} €` : "N/A";
  const duree = cert.duree || "N/A";
  const domaine = cert.domaine || "";
  const score = Math.round(cert.combined_score || cert.relevance_score || 0);

  // Matched skills
  let matchedSkills = cert.matched_skills || [];
  if (typeof matchedSkills === "string") {
    matchedSkills = matchedSkills.split(",").map(s => s.trim()).filter(Boolean);
  }

  // Competences
  let competences = cert.competences || [];
  if (typeof competences === "string") {
    competences = competences.split(",").map(s => s.trim()).filter(Boolean);
  }

  const getDomainIcon = (d) => {
    const domain = (d || "").toLowerCase();
    if (domain.includes("cloud")) return "☁️";
    if (domain.includes("data")) return "📊";
    if (domain.includes("ai") || domain.includes("ia")) return "🤖";
    return "🎓";
  };

  const getNiveauColor = (n) => {
    const level = (n || "").toLowerCase();
    if (level.includes("débutant")) return "#22c55e";
    if (level.includes("intermédiaire")) return "#f59e0b";
    if (level.includes("avancé")) return "#ef4444";
    return "#94a3b8";
  };

  return (
    <div style={{
      background: 'linear-gradient(145deg, #1e293b 0%, #1a2332 100%)',
      borderRadius: '12px',
      border: '1px solid rgba(236, 72, 153, 0.2)',
      marginBottom: '12px',
      overflow: 'hidden'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        padding: '12px',
        background: 'linear-gradient(135deg, rgba(236, 72, 153, 0.15) 0%, rgba(244, 114, 182, 0.05) 100%)',
        borderBottom: '1px solid rgba(236, 72, 153, 0.1)'
      }}>
        <div style={{
          width: '28px',
          height: '28px',
          background: 'linear-gradient(135deg, #db2777, #ec4899)',
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontSize: '0.75rem',
          fontWeight: 700
        }}>
          #{rank}
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ fontSize: '1rem' }}>{getDomainIcon(domaine)}</span>
            <span style={{
              fontSize: '0.85rem',
              fontWeight: 600,
              color: '#f1f5f9',
              lineHeight: 1.3,
              wordBreak: 'break-word'
            }}>
              {title}
            </span>
          </div>
        </div>
        <div style={{
          background: 'rgba(236, 72, 153, 0.2)',
          padding: '4px 10px',
          borderRadius: '12px',
          fontSize: '0.75rem',
          fontWeight: 700,
          color: '#f9a8d4'
        }}>
          Score: {score}
        </div>
      </div>

      {/* META: Niveau / Prix / Durée */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: '1px',
        background: 'rgba(236, 72, 153, 0.1)'
      }}>
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          padding: '10px 8px',
          background: '#1e293b'
        }}>
          <span style={{ fontSize: '0.65rem', color: '#64748b', textTransform: 'uppercase', marginBottom: '4px' }}>
            Niveau
          </span>
          <span style={{ fontSize: '0.8rem', fontWeight: 600, color: getNiveauColor(niveau) }}>
            {niveau}
          </span>
        </div>
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          padding: '10px 8px',
          background: '#1e293b'
        }}>
          <span style={{ fontSize: '0.65rem', color: '#64748b', textTransform: 'uppercase', marginBottom: '4px' }}>
            Prix
          </span>
          <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#22c55e' }}>
            {prix}
          </span>
        </div>
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          padding: '10px 8px',
          background: '#1e293b'
        }}>
          <span style={{ fontSize: '0.65rem', color: '#64748b', textTransform: 'uppercase', marginBottom: '4px' }}>
            Durée
          </span>
          <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#e2e8f0' }}>
            {duree}
          </span>
        </div>
      </div>

      {/* Matched Skills */}
      {matchedSkills.length > 0 && (
        <div style={{
          padding: '10px 12px',
          borderTop: '1px solid rgba(34, 197, 94, 0.2)',
          background: 'rgba(34, 197, 94, 0.05)'
        }}>
          <div style={{ fontSize: '0.6rem', color: '#64748b', textTransform: 'uppercase', marginBottom: '6px' }}>
            Correspondance
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
            {matchedSkills.slice(0, 4).map((skill, i) => (
              <span key={i} style={{
                background: 'rgba(34, 197, 94, 0.2)',
                color: '#22c55e',
                padding: '3px 8px',
                borderRadius: '6px',
                fontSize: '0.7rem',
                fontWeight: 600
              }}>
                ✓ {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Competences */}
      {competences.length > 0 && (
        <div style={{
          padding: '10px 12px',
          borderTop: '1px solid rgba(236, 72, 153, 0.1)'
        }}>
          <div style={{ fontSize: '0.6rem', color: '#64748b', textTransform: 'uppercase', marginBottom: '6px' }}>
            Compétences
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
            {competences.slice(0, 4).map((comp, i) => (
              <span key={i} style={{
                background: '#334155',
                color: '#e2e8f0',
                padding: '3px 8px',
                borderRadius: '5px',
                fontSize: '0.68rem'
              }}>
                {comp}
              </span>
            ))}
            {competences.length > 4 && (
              <span style={{
                background: 'rgba(236, 72, 153, 0.15)',
                color: '#f9a8d4',
                padding: '3px 8px',
                borderRadius: '5px',
                fontSize: '0.65rem',
                fontWeight: 600
              }}>
                +{competences.length - 4}
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default function RecommendationPanel({ recommendations }) {
  const certs = Array.isArray(recommendations) ? recommendations : [];

  return (
    <div style={{
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      minHeight: 0,
      background: '#0f172a'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '16px 20px',
        borderBottom: '1px solid rgba(236, 72, 153, 0.15)',
        background: 'linear-gradient(135deg, rgba(236, 72, 153, 0.05) 0%, #0f172a 100%)'
      }}>
        <h3 style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontSize: '0.95rem',
          fontWeight: 600,
          color: '#f1f5f9',
          margin: 0
        }}>
          <span>💡</span>
          Recommandations
        </h3>
        {certs.length > 0 && (
          <span style={{
            fontSize: '0.75rem',
            color: '#f9a8d4',
            background: 'rgba(236, 72, 153, 0.15)',
            padding: '4px 12px',
            borderRadius: '12px',
            fontWeight: 600
          }}>
            {certs.length} résultat{certs.length > 1 ? 's' : ''}
          </span>
        )}
      </div>

      {/* List */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '16px'
      }}>
        {certs.length === 0 ? (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '48px 24px',
            textAlign: 'center',
            color: '#64748b'
          }}>
            <div style={{ fontSize: '3rem', marginBottom: '16px', opacity: 0.6 }}>🎓</div>
            <p>Les recommandations apparaîtront ici après votre première question</p>
          </div>
        ) : (
          certs.map((cert, index) => (
            <RecommendationCard
              key={cert.id || `cert-${index}`}
              cert={cert}
              rank={index + 1}
            />
          ))
        )}
      </div>
    </div>
  );
}

import { useState, useEffect } from "react";
import "./ProfilePanel.css";

// SCOPE: Cloud, Data, AI only
const DOMAINS = [
  { value: "", label: "Tous les domaines" },
  { value: "cloud", label: "Cloud Computing" },
  { value: "data", label: "Data Engineering & Analytics" },
  { value: "ai", label: "Intelligence Artificielle & ML" }
];

const LEVELS = [
  { value: "", label: "Tous les niveaux" },
  { value: "Débutant", label: "Débutant" },
  { value: "Intermédiaire", label: "Intermédiaire" },
  { value: "Avancé", label: "Avancé" }
];

export default function ProfilePanel({ filters, onFilterChange, skillAnalysis, contextUsed }) {
  const [localFilters, setLocalFilters] = useState(filters);

  useEffect(() => {
    setLocalFilters(filters);
  }, [filters]);

  const handleChange = (field, value) => {
    const newFilters = { ...localFilters, [field]: value };
    setLocalFilters(newFilters);
    onFilterChange(newFilters);
  };

  const extractedSkills = skillAnalysis?.extracted_skills || [];
  const skillVector = skillAnalysis?.skill_vector || {};
  const domains = skillAnalysis?.domains || [];
  const levelHint = skillAnalysis?.level_hint;

  // Show section if we have any analysis data (skills, domains, or level)
  const hasSkillData = extractedSkills.length > 0 || Object.keys(skillVector).length > 0 || domains.length > 0 || levelHint;

  return (
    <div className="profile-panel">
      {/* Filters Section */}
      <div className="panel-section">
        <h3 className="section-title">
          <span className="section-icon">💡</span>
          Filtres de recherche
        </h3>

        <div className="filter-group">
          <label className="filter-label">Domaine</label>
          <select
            className="filter-select"
            value={localFilters.domain}
            onChange={(e) => handleChange("domain", e.target.value)}
          >
            {DOMAINS.map((d) => (
              <option key={d.value} value={d.value}>
                {d.label}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-label">Niveau</label>
          <select
            className="filter-select"
            value={localFilters.level}
            onChange={(e) => handleChange("level", e.target.value)}
          >
            {LEVELS.map((l) => (
              <option key={l.value} value={l.value}>
                {l.label}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-label">Budget maximum (€)</label>
          <input
            type="number"
            className="filter-input"
            placeholder="Ex: 300"
            value={localFilters.budget}
            onChange={(e) => handleChange("budget", e.target.value)}
            min="0"
            step="50"
          />
        </div>
      </div>

      {/* Skill Analysis Section */}
      <div className="panel-section">
        <h3 className="section-title">
          <span className="section-icon">🧠</span>
          Analyse des compétences
        </h3>

        {!hasSkillData ? (
          <div className="empty-state">
            <p>Posez une question pour voir l'analyse de vos compétences</p>
          </div>
        ) : (
          <>
            {/* Detected Level */}
            {levelHint && (
              <div className="skill-info-row">
                <span className="info-label">Niveau détecté:</span>
                <span className={`level-badge level-${levelHint.toLowerCase()}`}>
                  {levelHint}
                </span>
              </div>
            )}

            {/* Detected Domains */}
            {domains.length > 0 && (
              <div className="skill-info-row">
                <span className="info-label">Domaines:</span>
                <div className="domain-tags">
                  {domains.map((d, i) => (
                    <span key={i} className="domain-tag">
                      {d}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Extracted Skills */}
            {extractedSkills.length > 0 && (
              <div className="skills-section">
                <span className="info-label">Compétences extraites:</span>
                <div className="skill-tags">
                  {extractedSkills.map((skill, i) => (
                    <span key={i} className="skill-tag">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

          </>
        )}
      </div>

      {/* Context Info - Only show for data queries, not social */}
      {contextUsed && contextUsed !== "SOCIAL" && (
        <div className="panel-section context-section">
          <h3 className="section-title">
            <span className="section-icon">📡</span>
            Source de données
          </h3>
          <div className="context-badge-wrapper">
            {contextUsed === "GRAPH_REASONING" && (
              <span className="context-badge context-graph">
                🗄️ Neo4j (Graph Reasoning)
              </span>
            )}
            {contextUsed === "PDF_WITH_GRAPH" && (
              <>
                <span className="context-badge context-pdf">
                  📄 RAG (PDF)
                </span>
                <span className="context-badge context-graph">
                  🗄️ Neo4j
                </span>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

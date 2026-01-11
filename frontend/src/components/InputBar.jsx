import { useState } from "react";
import "./InputBar.css";

export default function InputBar({ onSend, isLoading, onPdfChange, uploadedPdf, onClearCache, userId, onSkillAnalysisChange, onContextUsedChange }) {
  const [text, setText] = useState("");

  // 📄 Fonction pour uploader un PDF
  const handlePdfUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    console.log("[InputBar] Starting PDF upload:", file.name);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:8000/pdf/upload", {
        method: "POST",
        body: formData,
      });

      console.log("[InputBar] Response status:", res.status);

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();
      console.log("[InputBar] PDF upload response:", data);
      console.log("[InputBar] PDF words:", data.words);
      console.log("[InputBar] Skill analysis:", data.skill_analysis);

      // Notify parent about uploaded PDF (always do this if upload succeeded)
      if (onPdfChange) {
        const pdfInfo = {
          name: file.name,
          words: data.words || 0,
          preview: data.preview || ""
        };
        console.log("[InputBar] Setting uploadedPdf to:", pdfInfo);
        onPdfChange(pdfInfo);
      }

      // Update skill analysis panel with extracted skills from PDF
      if (data.skill_analysis && onSkillAnalysisChange) {
        console.log("[InputBar] Updating skill analysis with:", {
          extracted_skills: data.skill_analysis.extracted_skills,
          domains: data.skill_analysis.domains,
          level_hint: data.skill_analysis.level_hint
        });
        onSkillAnalysisChange(data.skill_analysis);
      }

      // Set context to indicate PDF mode
      if (onContextUsedChange) {
        onContextUsedChange("PDF_WITH_GRAPH");
      }

    } catch (error) {
      console.error("[InputBar] Erreur upload PDF:", error);
      alert("⚠️ Erreur lors de l'importation du PDF: " + error.message);
    }
  };

  // 🧹 Fonction pour vider le PDF du backend ET la mémoire de conversation
  const clearPdf = async () => {
    try {
      await fetch("http://localhost:8000/pdf/clear", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId || null })
      });
      console.log("[InputBar] PDF, skill analysis, and conversation memory cleared");

      // Notify parent that PDF is cleared
      if (onPdfChange) {
        onPdfChange(null);
      }

      // Clear skill analysis panel
      if (onSkillAnalysisChange) {
        onSkillAnalysisChange(null);
      }

      // Clear context indicator
      if (onContextUsedChange) {
        onContextUsedChange(null);
      }

    } catch (err) {
      console.error("Erreur clear PDF:", err);
      alert("⚠️ Impossible de vider le PDF");
    }
  };

  // 📩 Envoi du message texte
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim() || isLoading) return;
    onSend(text);
    setText("");
  };

  // Debug log
  console.log("[InputBar] uploadedPdf state:", uploadedPdf);

  return (
    <div className="input-bar-container">
      {/* PDF Upload Indicator */}
      {uploadedPdf && (
        <div className="pdf-indicator">
          <span className="pdf-icon">📄</span>
          <span className="pdf-name">{uploadedPdf.name}</span>
          <span className="pdf-words">({uploadedPdf.words} mots)</span>
          <button
            type="button"
            onClick={clearPdf}
            className="pdf-remove-btn"
            title="Supprimer le PDF"
          >
            ✕
          </button>
        </div>
      )}

      <form className="input-bar" onSubmit={handleSubmit}>
        {/* Champ de texte */}
        <input
          type="text"
          placeholder="Écris ta question ici (ex: 'Quelle certif Azure pour débuter ?')"
          value={text}
          onChange={(e) => setText(e.target.value)}
        />

        {/* Input PDF invisible */}
        <input
          type="file"
          id="pdfInput"
          accept="application/pdf"
          onChange={handlePdfUpload}
          style={{ display: "none" }}
        />

        {/* Bouton visible pour importer PDF */}
        <label htmlFor="pdfInput" className="pdf-upload-button">
          📄 {uploadedPdf ? "Changer" : "Importer CV"}
        </label>

        {/* Bouton vider PDF */}
        {uploadedPdf && (
          <button
            type="button"
            onClick={clearPdf}
            className="clear-pdf-button"
            title="Vider le PDF"
          >
            🧹 Vider PDF
          </button>
        )}

        {/* Bouton vider cache */}
        <button
          type="button"
          onClick={onClearCache}
          className="clear-cache-button"
          title="Vider le cache"
        >
          🗑️ Cache
        </button>

        {/* Bouton envoyer */}
        <button type="submit" disabled={isLoading}>
          {isLoading ? "..." : "Envoyer"}
        </button>
      </form>
    </div>
  );
}

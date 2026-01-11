import "./Message.css";

// Escape HTML to prevent injection
function escapeHtml(str = "") {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// Convert text to clean HTML (no raw markdown symbols)
function toCleanHtml(text = "") {
  let s = escapeHtml(text);

  // Remove markdown heading symbols (###, ##, #) but keep the text
  s = s.replace(/^#{1,6}\s+/gm, "");

  // Convert **bold** to <strong>
  s = s.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

  // Convert *italic* to <em> (but not inside words)
  s = s.replace(/(?<!\w)\*([^*]+)\*(?!\w)/g, "<em>$1</em>");

  // Process lines for lists and paragraphs
  const lines = s.split("\n");
  let html = "";
  let inList = false;

  for (const line of lines) {
    const trimmed = line.trim();

    // Bullet points (- or •)
    const isBullet = trimmed.startsWith("- ") || trimmed.startsWith("• ");
    if (isBullet) {
      if (!inList) {
        html += "<ul>";
        inList = true;
      }
      const item = trimmed.replace(/^(- |• )/, "");
      html += `<li>${item}</li>`;
    } else {
      if (inList) {
        html += "</ul>";
        inList = false;
      }
      // Empty line = break, otherwise add text with break
      if (trimmed === "") {
        html += "<br/>";
      } else {
        html += `${trimmed}<br/>`;
      }
    }
  }

  if (inList) html += "</ul>";

  return html;
}

export default function Message({ role, content, typing }) {
  const isUser = role === "user";

  return (
    <div className={`message-row ${isUser ? "user" : "assistant"}`}>
      <div className={`message-bubble ${isUser ? "user" : "assistant"}`}>
        {typing ? (
          <span className="typing">Recherche en cours…</span>
        ) : (
          <div
            className="message-content"
            dangerouslySetInnerHTML={{ __html: toCleanHtml(content) }}
          />
        )}
      </div>
    </div>
  );
}

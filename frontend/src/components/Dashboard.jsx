import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "./Sidebar";
import Message from "./Message";
import InputBar from "./InputBar";
import ProfilePanel from "./ProfilePanel";
import RecommendationPanel from "./RecommendationPanel";
import logo from "../assets/logo-certiprofile.png";
import "./Dashboard.css";

const API_URL = "http://127.0.0.1:8000";

export default function Dashboard() {
  const navigate = useNavigate();

  // Auth & user state
  const [email, setEmail] = useState(null);
  const [userId, setUserId] = useState(null);

  // Chat state
  const [chats, setChats] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Intelligence state - exposed from backend
  const [skillAnalysis, setSkillAnalysis] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [contextUsed, setContextUsed] = useState(null);

  // PDF state
  const [uploadedPdf, setUploadedPdf] = useState(null);

  // User filters
  const [filters, setFilters] = useState({
    domain: "",
    level: "",
    budget: ""
  });

  // Auth check
  useEffect(() => {
    const e = localStorage.getItem("email");
    const uid = localStorage.getItem("user_id");

    if (!e || !uid) {
      navigate("/");
      return;
    }
    setEmail(e);
    setUserId(uid);
  }, [navigate]);

  // Load chats from localStorage
  useEffect(() => {
    if (!email) return;

    const key = `certi_chats_${email}`;
    const saved = JSON.parse(localStorage.getItem(key) || "[]");

    if (saved.length > 0) {
      setChats(saved);
      setActiveChatId(saved[0].id);
    } else {
      const newChat = createNewChat();
      setChats([newChat]);
      setActiveChatId(newChat.id);
    }
  }, [email]);

  // Auto-save chats
  useEffect(() => {
    if (!email || chats.length === 0) return;
    const key = `certi_chats_${email}`;
    localStorage.setItem(key, JSON.stringify(chats));
  }, [chats, email]);

  const createNewChat = () => ({
    id: Date.now(),
    title: "Nouvelle conversation",
    messages: [],
    skillAnalysis: null,
    recommendations: []
  });

  const handleNewChat = () => {
    const newChat = createNewChat();
    setChats((prev) => [newChat, ...prev]);
    setActiveChatId(newChat.id);
    setSkillAnalysis(null);
    setRecommendations([]);
    setContextUsed(null);
  };

  const handleSelectChat = (id) => {
    setActiveChatId(id);
    const chat = chats.find((c) => c.id === id);
    if (chat) {
      setSkillAnalysis(chat.skillAnalysis || null);
      setRecommendations(chat.recommendations || []);
    }
  };

  const handleDeleteChat = (id) => {
    const updated = chats.filter((c) => c.id !== id);
    if (updated.length > 0) {
      setChats(updated);
      setActiveChatId(updated[0].id);
      const chat = updated[0];
      setSkillAnalysis(chat.skillAnalysis || null);
      setRecommendations(chat.recommendations || []);
    } else {
      const newChat = createNewChat();
      setChats([newChat]);
      setActiveChatId(newChat.id);
      setSkillAnalysis(null);
      setRecommendations([]);
    }
  };

  const handleFilterChange = useCallback((newFilters) => {
    setFilters(newFilters);
  }, []);

  const handleSendMessage = async (text) => {
    if (!text.trim() || !activeChatId) return;
    setIsLoading(true);

    // Reset recommendations immediately when new query starts
    setRecommendations([]);
    setSkillAnalysis(null);

    // Build query with filters if set
    let enrichedQuery = text;
    const filterParts = [];
    if (filters.domain) filterParts.push(`domaine: ${filters.domain}`);
    if (filters.level) filterParts.push(`niveau: ${filters.level}`);
    if (filters.budget) filterParts.push(`budget: ${filters.budget}€`);

    if (filterParts.length > 0) {
      enrichedQuery = `${text}\n[Filtres: ${filterParts.join(", ")}]`;
    }

    // Add user message to chat
    setChats((prev) =>
      prev.map((c) =>
        c.id === activeChatId
          ? {
              ...c,
              title:
                c.messages.length === 0
                  ? text.slice(0, 30) + (text.length > 30 ? "..." : "")
                  : c.title,
              messages: [...c.messages, { role: "user", content: text }],
            }
          : c
      )
    );

    try {
      const res = await fetch(`${API_URL}/chat-rag/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: enrichedQuery,
          user_id: userId
        }),
      });

      if (res.ok) {
        const data = await res.json();
        const answer = data.answer || "Pas de réponse.";

        // Extract intelligence data from response
        const newSkillAnalysis = data.skill_analysis || null;
        const newRecommendations = data.recommendations || [];
        const newContextUsed = data.context_used || null;

        // Debug log
        console.log("[Dashboard] Backend response:", data);
        console.log("[Dashboard] Recommendations from backend:", newRecommendations);
        console.log("[Dashboard] Recommendations count:", newRecommendations.length);

        // Update state with intelligence
        setSkillAnalysis(newSkillAnalysis);
        setRecommendations(newRecommendations);
        setContextUsed(newContextUsed);

        // Add assistant message and store intelligence in chat
        setChats((prev) =>
          prev.map((c) =>
            c.id === activeChatId
              ? {
                  ...c,
                  messages: [...c.messages, { role: "assistant", content: answer }],
                  skillAnalysis: newSkillAnalysis,
                  recommendations: newRecommendations
                }
              : c
          )
        );
      } else {
        const errorMsg = `Erreur backend (${res.status})`;
        // Keep recommendations cleared on error
        setChats((prev) =>
          prev.map((c) =>
            c.id === activeChatId
              ? {
                  ...c,
                  messages: [...c.messages, { role: "assistant", content: errorMsg }],
                  recommendations: []
                }
              : c
          )
        );
      }
    } catch (err) {
      console.error(err);
      // Keep recommendations cleared on error
      setChats((prev) =>
        prev.map((c) =>
          c.id === activeChatId
            ? {
                ...c,
                messages: [
                  ...c.messages,
                  { role: "assistant", content: "Serveur injoignable." },
                ],
                recommendations: []
              }
            : c
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("user_id");
    localStorage.removeItem("email");
    navigate("/");
  };

  // Clear all cached data and refresh
  const handleClearCache = () => {
    const email = localStorage.getItem("email");
    if (email) {
      localStorage.removeItem(`certi_chats_${email}`);
    }
    setChats([createNewChat()]);
    setActiveChatId(Date.now());
    setRecommendations([]);
    setSkillAnalysis(null);
    setContextUsed(null);
    setUploadedPdf(null);
    alert("Cache vidé !");
  };

  if (!email) return null;

  const activeChat = chats.find((c) => c.id === activeChatId);

  return (
    <div className="dashboard">
      {/* Left: Sidebar */}
      <Sidebar
        chats={chats}
        activeChatId={activeChatId}
        onNewChat={handleNewChat}
        onSelectChat={handleSelectChat}
        onDeleteChat={handleDeleteChat}
      />

      {/* Center: Chat */}
      <div className="dashboard-chat">
        <header className="chat-header">
          <div className="header-left">
            <img src={logo} alt="CertiProfile" className="header-logo" />
            <div className="header-text">
              <h1>CertiProfile AI</h1>
              <span className="header-subtitle">Recommandations intelligentes de certifications</span>
            </div>
          </div>
          <div className="header-right">
            <span className="user-email">{email}</span>
            <button className="logout-btn" onClick={handleLogout}>
              Déconnexion
            </button>
          </div>
        </header>

        <div className="chat-messages">
          {activeChat && activeChat.messages.length === 0 && (
            <div className="welcome-panel">
              <div className="welcome-icon">🎓</div>
              <h2>Bienvenue sur CertiProfile AI</h2>
              <p>
                Votre assistant intelligent pour les certifications
                <strong> Cloud</strong>, <strong>Data</strong> et <strong>IA</strong>.
                Décrivez votre profil ou importez votre CV.
              </p>
              <div className="welcome-features">
                <div className="feature">
                  <span className="feature-icon">☁️</span>
                  <span>Cloud (AWS, Azure, GCP)</span>
                </div>
                <div className="feature">
                  <span className="feature-icon">📈</span>
                  <span>Data Engineering & Analytics</span>
                </div>
                <div className="feature">
                  <span className="feature-icon">🧠</span>
                  <span>IA & Machine Learning</span>
                </div>
              </div>
            </div>
          )}

          {activeChat?.messages.map((m, i) => (
            <Message key={i} role={m.role} content={m.content} />
          ))}

          {isLoading && (
            <Message role="assistant" content="Analyse en cours..." typing />
          )}
        </div>

        <div className="chat-input-wrapper">
          <InputBar
            onSend={handleSendMessage}
            isLoading={isLoading}
            uploadedPdf={uploadedPdf}
            onPdfChange={setUploadedPdf}
            onClearCache={handleClearCache}
            userId={userId}
            onSkillAnalysisChange={setSkillAnalysis}
            onContextUsedChange={setContextUsed}
          />
        </div>
      </div>

      {/* Right: Intelligence Panel */}
      <div className="dashboard-intelligence">
        <ProfilePanel
          filters={filters}
          onFilterChange={handleFilterChange}
          skillAnalysis={skillAnalysis}
          contextUsed={contextUsed}
        />

        <RecommendationPanel recommendations={recommendations} />
      </div>
    </div>
  );
}

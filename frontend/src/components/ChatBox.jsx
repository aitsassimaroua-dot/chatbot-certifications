import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "./Sidebar";
import Message from "./Message";
import InputBar from "./InputBar";
import logo from "../assets/logo-certiprofile.png";
import "./ChatBox.css";

const API_URL = "http://127.0.0.1:8000/chat-rag/chat-rag/";

export default function ChatBox() {
  const navigate = useNavigate();

  const [email, setEmail] = useState(null);
  const [chats, setChats] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // 🔐 Vérifier auth
  useEffect(() => {
    const e = localStorage.getItem("email");
    const uid = localStorage.getItem("user_id");

    if (!e || !uid) {
      navigate("/");
      return;
    }
    setEmail(e);
  }, [navigate]);

  // ✅ Charger les chats du user (par email = stable)
  useEffect(() => {
    if (!email) return;

    const key = `certi_chats_${email}`;
    const saved = JSON.parse(localStorage.getItem(key) || "[]");

    if (saved.length > 0) {
      setChats(saved);
      setActiveChatId(saved[0].id);
    } else {
      const newChat = {
        id: Date.now(),
        title: "Nouvelle conversation",
        messages: [],
      };
      setChats([newChat]);
      setActiveChatId(newChat.id);
    }
  }, [email]);

  // 💾 Sauvegarder automatiquement
  useEffect(() => {
    if (!email) return;
    const key = `certi_chats_${email}`;
    localStorage.setItem(key, JSON.stringify(chats));
  }, [chats, email]);

  const handleNewChat = () => {
    const newChat = {
      id: Date.now(),
      title: "Nouvelle conversation",
      messages: [],
    };
    setChats((prev) => [newChat, ...prev]);
    setActiveChatId(newChat.id);
  };

  const handleSelectChat = (id) => setActiveChatId(id);

  const handleDeleteChat = (id) => {
    const updated = chats.filter((c) => c.id !== id);
    if (updated.length > 0) {
      setChats(updated);
      setActiveChatId(updated[0].id);
    } else {
      const newChat = {
        id: Date.now(),
        title: "Nouvelle conversation",
        messages: [],
      };
      setChats([newChat]);
      setActiveChatId(newChat.id);
    }
  };

  const handleSendMessage = async (text) => {
    if (!text.trim() || !activeChatId) return;
    setIsLoading(true);

    // add user msg
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
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: text }),
      });

      let answer = "Erreur backend.";
      if (res.ok) {
        const data = await res.json();
        answer = data.answer || "Pas de réponse.";
      } else {
        answer = `Erreur backend (${res.status})`;
      }

      setChats((prev) =>
        prev.map((c) =>
          c.id === activeChatId
            ? {
                ...c,
                messages: [...c.messages, { role: "assistant", content: answer }],
              }
            : c
        )
      );
    } catch (err) {
      console.error(err);
      setChats((prev) =>
        prev.map((c) =>
          c.id === activeChatId
            ? {
                ...c,
                messages: [
                  ...c.messages,
                  { role: "assistant", content: "Serveur injoignable." },
                ],
              }
            : c
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  if (!email) return null;

  const activeChat = chats.find((c) => c.id === activeChatId);

  return (
    <div className="app-shell">
      <Sidebar
        chats={chats}
        activeChatId={activeChatId}
        onNewChat={handleNewChat}
        onSelectChat={handleSelectChat}
        onDeleteChat={handleDeleteChat}
      />

      <div className="chat-main">
        <header className="chat-topbar">
          <div className="logo-block">
            <img src={logo} alt="CertiProfile" className="logo-img" />
            <div>
              <h1 className="app-name">CertiProfile ChatBot</h1>
              <p className="app-subtitle">
                Ton assistant intelligent pour trouver la meilleure certification ✨
              </p>
            </div>
          </div>
        </header>

        <div className="chat-messages">
          {/* 🌟 Bienvenue */}
          {activeChat && activeChat.messages.length === 0 && (
            <div className="chat-placeholder fade-in">
              <h2 className="placeholder-title">Bienvenue 👋</h2>
              <p className="placeholder-text">
                Je t’aide à trouver la certification la plus adaptée à ton niveau,
                ton budget et ton domaine.
              </p>
            </div>
          )}

          {/* 💬 Messages */}
          {activeChat?.messages.map((m, i) => (
            <Message key={i} role={m.role} content={m.content} />
          ))}

          {isLoading && <Message role="assistant" content="Recherche en cours…" typing />}
        </div>

        <div className="chat-input-area">
          <InputBar onSend={handleSendMessage} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
}

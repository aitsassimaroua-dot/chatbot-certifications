import "./Sidebar.css";

export default function Sidebar({
  chats,
  activeChatId,
  onNewChat,
  onSelectChat,
  onDeleteChat,
}) {
  const handleLogout = () => {
    // ✅ On enlève uniquement l’identité (auth)
    localStorage.removeItem("user_id");
    localStorage.removeItem("email");

    // ⚠️ NE PAS FAIRE localStorage.clear() sinon tu effaces les chats !
    window.location.href = "/";
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2>Sessions</h2>

        <div className="sidebar-buttons">
          <button className="new-chat-btn" onClick={onNewChat}>
            Nouveau chat
          </button>

          <button className="logout-btn" onClick={handleLogout}>
            Déconnexion
          </button>
        </div>
      </div>

      <div className="sidebar-list">
        {chats.map((chat) => (
          <div
            key={chat.id}
            className={
              "sidebar-item-wrapper" +
              (chat.id === activeChatId ? " sidebar-item-active" : "")
            }
          >
            <button
              className="sidebar-item"
              onClick={() => onSelectChat(chat.id)}
            >
              <span className="sidebar-dot">●</span>
              <span className="sidebar-title">{chat.title}</span>
            </button>

            <button
              className="delete-btn"
              onClick={(e) => {
                e.stopPropagation();
                onDeleteChat(chat.id);
              }}
              title="Supprimer"
            >
              ✕
            </button>
          </div>
        ))}
      </div>
    </aside>
  );
}

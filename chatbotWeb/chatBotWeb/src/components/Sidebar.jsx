import React from "react";

// Inline Icons to prevent errors if you don't have an icon library
const IconPlus = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
);

const IconMessage = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
);

function Sidebar({ isOpen, onNewChat, sessions = [], onSelectSession }) {
  return (
    <div className={`sidebar ${isOpen ? "open" : ""}`}>
      <div className="sidebar-header">
        <button className="new-chat-btn" onClick={onNewChat}>
          <IconPlus /> <span>New Chat</span>
        </button>
      </div>
      <div className="sidebar-content">
        <div className="history-label">Recent</div>
        <ul>
          {sessions.map((item) => (
            <li
              key={item.chat_session_id}
              className="history-item"
              onClick={() => onSelectSession?.(item.chat_session_id)}
              title={item.title}
            >
              <IconMessage /> <span>{item.title || "Untitled Chat"}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default Sidebar;

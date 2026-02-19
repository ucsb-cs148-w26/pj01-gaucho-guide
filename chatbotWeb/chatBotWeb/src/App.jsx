import { useState, useEffect, useRef } from "react";
import Header from "./components/Header";
import InputContainer from "./components/InputContainer";
import Sidebar from "./components/Sidebar";
import ProfilePage from "./components/ProfilePage";
import SignIn from "./components/SignIn";
import { useAuth } from "./contexts/AuthContext";
import "./App.css";
import gauchoLogo from "./assets/gaucho-logo.png";

function App() {
  const { user, loading, isAuthenticated } = useAuth();
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [inputMessage, setInputMessage] = useState("");
  const [theme, setTheme] = useState("light");
  const [showProfile, setShowProfile] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [isThinking, setIsThinking] = useState(false);
  const [hasSubmitted, setHasSubmitted] = useState(false);

  const bottomRef = useRef(null);
  const sessionIdRef = useRef(null);

  useEffect(() => {
    document.body.setAttribute("data-theme", theme);
  }, [theme]);

  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 2500);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isThinking]);

  const toggleTheme = () => setTheme((prev) => (prev === "light" ? "dark" : "light"));

  const getSessionId = () => {
    if (!sessionIdRef.current) sessionIdRef.current = crypto.randomUUID();
    return sessionIdRef.current;
  };

  const toText = (r) => {
    if (typeof r === "string") return r;
    if (Array.isArray(r)) {
      const parts = r.map((p) => p?.text).filter(Boolean);
      if (parts.length) return parts.join("\n");
    }
    try { return JSON.stringify(r); } catch { return String(r); }
  };

  const handleSubmit = async () => {
    if (isThinking) return;
    const text = inputMessage.trim();
    if (!text && !file) return;

    setHasSubmitted(true);
    setIsThinking(true);
    setMessages((m) => [...m, { role: "user", content: text }]);
    setInputMessage("");

    try {
      const res = await fetch("chat/response", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chat_session_id: getSessionId(), message: text }),
      });
      if (!res.ok) throw new Error(await res.text() || `HTTP ${res.status}`);
      const data = await res.json();
      setMessages((m) => [...m, { role: "assistant", content: toText(data.response) }]);
    } catch {
      setMessages((m) => [...m, { role: "assistant", content: "Something went wrong. Try again." }]);
    } finally {
      setIsThinking(false);
    }
  };

  if (loading) return (
    <div className="app" data-theme={theme}>
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading...</p>
      </div>
    </div>
  );

  if (!isAuthenticated) return <SignIn />;

  if (showProfile) return (
    <div className="app" data-theme={theme}>
      <ProfilePage onBack={() => setShowProfile(false)} />
    </div>
  );

  return (
    <div className="app" data-theme={theme}>
      <div className="hover-trigger" onMouseEnter={() => setIsSidebarOpen(true)} />
      <div className="sidebar-wrapper" onMouseLeave={() => setIsSidebarOpen(false)}>
        <Sidebar isOpen={isSidebarOpen} onNewChat={() => console.log("New Chat Started")} />
      </div>

      <div className={`logo-wrapper ${isLoading ? "loading-mode" : "background-mode"}`}>
        <img src={gauchoLogo} alt="Gaucho Logo" className="mascot-logo" />
      </div>

      <div className={`main-content-wrapper ${!isLoading ? "visible" : ""}`}>
        <Header theme={theme} toggleTheme={toggleTheme} user={user} onProfileClick={() => setShowProfile(true)} />

        <div className="center-content">
          {!hasSubmitted && <h2 className="prompt gold-text">How can I help you today?</h2>}

          {hasSubmitted && (
            <div className="chat-feed">
              {messages.map((m, i) => (
                <div key={i} className={`chat-bubble ${m.role === "user" ? "chat-user" : "chat-assistant"}`}>
                  {typeof m.content === "string" ? m.content : JSON.stringify(m.content)}
                </div>
              ))}
              {isThinking && <div className="chat-bubble chat-assistant chat-thinking">Thinking…</div>}
              <div ref={bottomRef} />
            </div>
          )}

          <InputContainer
            file={file}
            setFile={setFile}
            inputMessage={inputMessage}
            setInputMessage={setInputMessage}
            error={error}
            setError={setError}
            onSubmit={handleSubmit}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
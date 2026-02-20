import { useEffect, useRef, useState } from "react";
import Header from "./components/Header";
import InputContainer from "./components/InputContainer";
import Sidebar from "./components/Sidebar";
import ProfilePage from "./components/ProfilePage";
import SignIn from "./components/SignIn";
import { useAuth } from "./contexts/AuthContext";
import "./App.css";
import gauchoLogo from "./assets/gaucho-logo.png";

function App() {
  const { loading, isAuthenticated, getIdToken } = useAuth();
  const API_BASE =
    import.meta.env.VITE_API_BASE_URL ?? (import.meta.env.PROD ? "/api" : "");

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
  const [chatSessions, setChatSessions] = useState([]);
  const [historyError, setHistoryError] = useState("");

  const bottomRef = useRef(null);
  const sessionIdRef = useRef(null);

  const apiUrl = (path) => `${API_BASE}${path}`;

  useEffect(() => {
    document.body.setAttribute("data-theme", theme);
  }, [theme]);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 2500);

    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isThinking]);

  useEffect(() => {
    const nextTypingIndex = messages.findIndex(
      (m) =>
        m.role === "assistant" &&
        typeof m.content === "string" &&
        typeof m.displayed === "string" &&
        m.displayed.length < m.content.length
    );

    if (nextTypingIndex === -1) return;

    const intervalId = setInterval(() => {
      setMessages((prev) => {
        const current = prev[nextTypingIndex];
        if (!current || current.role !== "assistant") return prev;

        const fullText = current.content;
        const shownText = current.displayed ?? "";
        if (shownText.length >= fullText.length) return prev;

        const step = Math.max(1, Math.ceil(fullText.length / 180));
        const updated = [...prev];
        updated[nextTypingIndex] = {
          ...current,
          displayed: fullText.slice(0, shownText.length + step),
        };
        return updated;
      });
    }, 14);

    return () => clearInterval(intervalId);
  }, [messages]);

  useEffect(() => {
    const loadSessions = async () => {
      const token = await getIdToken();
      if (!token) return;
      try {
        const res = await fetch(apiUrl("/chat/sessions"), {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) {
          const errText = await res.text();
          setHistoryError(errText || `History load failed: HTTP ${res.status}`);
          return;
        }
        const data = await res.json();
        setChatSessions(Array.isArray(data.sessions) ? data.sessions : []);
        setHistoryError("");
      } catch {
        setHistoryError("Unable to load chat history right now.");
      }
    };
    loadSessions();
  }, [getIdToken]);

  const getSessionId = () => {
    if (!sessionIdRef.current) {
      sessionIdRef.current = crypto.randomUUID();
    }
    return sessionIdRef.current;
  };

  const toText = (response) => {
    if (typeof response === "string") return response;

    if (Array.isArray(response)) {
      const textParts = response
        .map((part) =>
          part && typeof part === "object" && typeof part.text === "string"
            ? part.text
            : null
        )
        .filter(Boolean);

      if (textParts.length) return textParts.join("\n");
    }

    try {
      return JSON.stringify(response);
    } catch {
      return String(response);
    }
  };

  const parseMaybeJson = (value) => {
    if (typeof value !== "string") return value;
    const trimmed = value.trim();
    if (
      !(trimmed.startsWith("{") || trimmed.startsWith("[")) ||
      !(trimmed.endsWith("}") || trimmed.endsWith("]"))
    ) {
      return value;
    }
    try {
      return JSON.parse(trimmed);
    } catch {
      return value;
    }
  };

  const normalizeStoredAssistantContent = (value) => {
    const parsed = parseMaybeJson(value);
    return toText(parsed);
  };

  const renderMarkdownBold = (text) => {
    const parts = text.split(/(\*\*[^*]+\*\*)/g);
    return parts.map((part, idx) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return <strong key={idx}>{part.slice(2, -2)}</strong>;
      }
      return <span key={idx}>{part}</span>;
    });
  };

  const normalizeAssistantText = (text) => {
    return text
      .replace(/\r\n/g, "\n")
      .replace(/\n{3,}/g, "\n\n")
      .trim();
  };

  const renderMessageContent = (content, role) => {
    if (typeof content !== "string") return JSON.stringify(content);
    if (role !== "assistant") return content;

    const normalized = normalizeAssistantText(content);

    return normalized.split("\n").map((rawLine, idx) => {
      const line = rawLine.trimEnd();
      if (!line) {
        return <span key={idx} className="assistant-line assistant-break" />;
      }

      const headingMatch = line.match(/^#{1,6}\s*(.+)$/);
      if (headingMatch) {
        return (
          <span key={idx} className="assistant-line assistant-heading">
            {renderMarkdownBold(headingMatch[1])}
          </span>
        );
      }

      const bulletMatch = line.match(/^[-*•]\s+(.+)$/);
      if (bulletMatch) {
        return (
          <span key={idx} className="assistant-line assistant-bullet">
            <span className="assistant-bullet-dot">•</span>
            <span>{renderMarkdownBold(bulletMatch[1])}</span>
          </span>
        );
      }

      return (
        <span key={idx} className="assistant-line">
          {renderMarkdownBold(line)}
        </span>
      );
    });
  };

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  const handleSubmit = async () => {
    if (isThinking) return;

    const text = inputMessage.trim();
    if (!text && !file) {
      setError("Please type a message or attach a transcript to continue.");
      return;
    }

    const sessionId = getSessionId();
    setError("");
    setHasSubmitted(true);
    setIsThinking(true);

    try {
      if (file) {
        const formData = new FormData();
        formData.append("session_id", sessionId);
        formData.append("file", file);

        const token = await getIdToken();
        const transcriptRes = await fetch(apiUrl("/transcript/parse"), {
          method: "POST",
          headers: token ? { Authorization: `Bearer ${token}` } : undefined,
          body: formData,
        });

        if (!transcriptRes.ok) {
          const errText = await transcriptRes.text();
          throw new Error(errText || `Transcript upload failed: HTTP ${transcriptRes.status}`);
        }

        const transcriptPayload = await transcriptRes.json();
        const major = transcriptPayload?.data?.major;
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: major
              ? `Transcript uploaded and added to context. I detected your major as ${major}.`
              : "Transcript uploaded and added to context.",
            displayed: "",
          },
        ]);
        setFile(null);
      }

      if (!text) {
        setInputMessage("");
        return;
      }

      setMessages((prev) => [...prev, { role: "user", content: text }]);
      setInputMessage("");

      const token = await getIdToken();
      const res = await fetch(apiUrl("/chat/response"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          chat_session_id: sessionId,
          message: text,
        }),
      });

      if (!res.ok) {
        const errText = await res.text();
        throw new Error(errText || `HTTP ${res.status}`);
      }

      const data = await res.json();
      const assistantText = toText(data.response);

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: assistantText, displayed: "" },
      ]);

      if (token) {
        const sessionsRes = await fetch(apiUrl("/chat/sessions"), {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (sessionsRes.ok) {
          const sessionsData = await sessionsRes.json();
          setChatSessions(
            Array.isArray(sessionsData.sessions) ? sessionsData.sessions : []
          );
        }
      }
    } catch (err) {
      const errMessage =
        err instanceof Error && err.message
          ? err.message
          : "Something went wrong. Try again.";
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: errMessage,
          displayed: "",
        },
      ]);
    } finally {
      setIsThinking(false);
    }
  };

  const handleNewChat = async () => {
    const oldSessionId = sessionIdRef.current;
    if (oldSessionId) {
      try {
        await fetch(
          apiUrl(`/transcript/clear?session_id=${encodeURIComponent(oldSessionId)}`),
          { method: "DELETE" }
        );
      } catch {
        // Ignore clear errors in UI reset path.
      }
    }

    sessionIdRef.current = null;
    setMessages([]);
    setHasSubmitted(false);
    setInputMessage("");
    setFile(null);
    setError("");
  };

  const handleSelectSession = async (chatSessionId) => {
    if (!chatSessionId) return;
    try {
      const token = await getIdToken();
      if (!token) return;
      const res = await fetch(apiUrl(`/chat/sessions/${encodeURIComponent(chatSessionId)}`), {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) return;
      const data = await res.json();
      const restored = (data.messages || []).map((m) => ({
        role: m.role === "ai" ? "assistant" : "user",
        content:
          m.role === "ai"
            ? normalizeStoredAssistantContent(m.content)
            : m.content,
        displayed:
          m.role === "ai"
            ? normalizeStoredAssistantContent(m.content)
            : undefined,
      }));
      sessionIdRef.current = chatSessionId;
      setMessages(restored);
      setHasSubmitted(restored.length > 0);
      setInputMessage("");
      setError("");
    } catch {
      // no-op
    }
  };

  const handleMouseEnterSidebar = () => setIsSidebarOpen(true);
  const handleMouseLeaveSidebar = () => setIsSidebarOpen(false);

  if (loading) {
    return (
      <div className="app" data-theme={theme}>
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <SignIn />;
  }

  if (showProfile) {
    return (
      <div className="app" data-theme={theme}>
        <ProfilePage onBack={() => setShowProfile(false)} />
      </div>
    );
  }

  return (
    <div className="app" data-theme={theme}>
      <div className="hover-trigger" onMouseEnter={handleMouseEnterSidebar} />

      <div className="sidebar-wrapper" onMouseLeave={handleMouseLeaveSidebar}>
        <Sidebar
          isOpen={isSidebarOpen}
          onNewChat={handleNewChat}
          sessions={chatSessions}
          onSelectSession={handleSelectSession}
        />
        {historyError && (
          <div className="history-error-inline">{historyError}</div>
        )}
      </div>

      <div
        className={`logo-wrapper ${
          isLoading ? "loading-mode" : "background-mode"
        }`}
      >
        <img src={gauchoLogo} alt="Gaucho Logo" className="mascot-logo" />
      </div>

      <div className={`main-content-wrapper ${!isLoading ? "visible" : ""}`}>
        <Header
          theme={theme}
          toggleTheme={toggleTheme}
          onProfileClick={() => setShowProfile(true)}
        />

        <div className="center-content">
          {!hasSubmitted && (
            <h2 className="prompt gold-text">How can I help you today?</h2>
          )}

          {hasSubmitted && (
            <div className="chat-feed">
              {messages.map((message, idx) => (
                <div
                  key={idx}
                  className={`chat-bubble ${
                    message.role === "user" ? "chat-user" : "chat-assistant"
                  }`}
                >
                  {renderMessageContent(
                    message.role === "assistant" &&
                      typeof message.displayed === "string"
                      ? message.displayed
                      : message.content,
                    message.role
                  )}
                </div>
              ))}

              {isThinking && (
                <div className="chat-bubble chat-assistant chat-thinking">
                  Thinking...
                </div>
              )}

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

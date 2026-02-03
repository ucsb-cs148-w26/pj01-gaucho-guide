import { useEffect, useRef, useState } from "react";
import Header from "./components/Header";
import InputContainer from "./components/InputContainer";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [inputMessage, setInputMessage] = useState("");
  const [theme, setTheme] = useState("light");

  const [messages, setMessages] = useState([]);
  const [isThinking, setIsThinking] = useState(false);
  const [hasSubmitted, setHasSubmitted] = useState(false);

  const bottomRef = useRef(null);
  const sessionIdRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isThinking]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  const getSessionId = () => {
    if (!sessionIdRef.current) {
      sessionIdRef.current = crypto.randomUUID();
    }
    return sessionIdRef.current;
  };

  const toText = (r) => {
    if (typeof r === "string") return r;
    if (Array.isArray(r)) {
      const textParts = r
        .map((p) =>
          p && typeof p === "object" && typeof p.text === "string"
            ? p.text
            : null
        )
        .filter(Boolean);
      if (textParts.length) return textParts.join("\n");
    }
    try {
      return JSON.stringify(r);
    } catch {
      return String(r);
    }
  };

  const handleSubmit = async () => {
    if (isThinking) return;

    const text = inputMessage.trim();
    if (!text && !file) return;

    setHasSubmitted(true);
    setIsThinking(true);

    const sessionId = getSessionId();

    setMessages((m) => [...m, { role: "user", content: text }]);
    setInputMessage("");


    try {
      const res = await fetch("chat/response", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
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

      setMessages((m) => [
        ...m,
        { role: "assistant", content: toText(data.response) },
      ]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: "Something went wrong. Try again.",
        },
      ]);
    } finally {
      setIsThinking(false);
    }
  };

  return (
    <div className="app" data-theme={theme}>
      <Header theme={theme} toggleTheme={toggleTheme} />

      <div className="center-content">
        {!hasSubmitted && (
          <h2 className="prompt gold-text">
            How can I help you today?
          </h2>
        )}

        {hasSubmitted && (
          <div className="chat-feed">
            {messages.map((m, i) => (
              <div
                key={i}
                className={`chat-bubble ${
                  m.role === "user" ? "chat-user" : "chat-assistant"
                }`}
              >
                {typeof m.content === "string"
                  ? m.content
                  : JSON.stringify(m.content)}
              </div>
            ))}

            {isThinking && (
              <div className="chat-bubble chat-assistant chat-thinking">
                Thinking…
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
  );
}

export default App;
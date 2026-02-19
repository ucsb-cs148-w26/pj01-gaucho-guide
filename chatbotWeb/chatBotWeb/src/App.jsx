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

  const renderMarkdownBold = (text) => {
    const parts = text.split(/(\*\*[^*]+\*\*)/g);
    return parts.map((part, idx) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return <strong key={idx}>{part.slice(2, -2)}</strong>;
      }
      return <span key={idx}>{part}</span>;
    });
  };

  const renderMessageContent = (content, role) => {
    if (typeof content !== "string") {
      return JSON.stringify(content);
    }

    if (role !== "assistant") {
      return content;
    }

    const lines = content.split("\n");
    return lines.map((line, idx) => (
      <span key={idx} className="assistant-line">
        {renderMarkdownBold(line)}
      </span>
    ));
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
      const assistantText = toText(data.response);

      setMessages((m) => [
        ...m,
        { role: "assistant", content: assistantText, displayed: "" },
      ]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: "Something went wrong. Try again.",
          displayed: "",
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
                {renderMessageContent(
                  m.role === "assistant" && typeof m.displayed === "string"
                    ? m.displayed
                    : m.content,
                  m.role
                )}
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

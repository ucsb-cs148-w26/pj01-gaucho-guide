import { useState, useEffect } from "react";
import Header from "./components/Header";
import InputContainer from "./components/InputContainer";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [inputMessage, setInputMessage] = useState("");
  
  // Initialize theme. Defaulting to light.
  const [theme, setTheme] = useState("light");

  // EFFECT: Apply the theme class to the actual HTML body element
  useEffect(() => {
    document.body.setAttribute("data-theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  const handleSubmit = () => {
    if (!file && !inputMessage.trim()) {
      setError("Please type a message or attach a transcript to continue.");
      return;
    }
    setError("");
    // Handle submission
    console.log("Submitting:", inputMessage, file ? file.name : "No file");
  };

  return (
    // The background blobs div has been removed from here
    <div className="app">
      <Header theme={theme} toggleTheme={toggleTheme} />

      <div className="center-content">
        <h2 className="prompt">How can I help you today?</h2>

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
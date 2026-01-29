import { useState } from "react";
import Header from "./components/Header";
import InputContainer from "./components/InputContainer";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  
  // State to capture the user's text message
  const [inputMessage, setInputMessage] = useState("");
  const [theme, setTheme] = useState("light");

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  const handleSubmit = () => {

    if (!file && !inputMessage.trim()) {
      // Only show error if BOTH file and text are missing
      setError("Please type a message or attach a transcript to continue.");
      return;
    }

    setError("");
    
    // Handle the submission (Text OR File OR Both)
    console.log("Submitting...");
    console.log("Message:", inputMessage);
    console.log("File:", file ? file.name : "No file attached");
    
    // Reset fields after submit if you want
    // setInputMessage("");
    // setFile(null);
  };

  return (
    <div className="app" data-theme={theme}>
      <Header theme={theme} toggleTheme={toggleTheme} />

      <div className="center-content">
        <h2 className="prompt">How can I help you today?</h2>

        <InputContainer
          file={file}
          setFile={setFile}
          // Pass the new message state down
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
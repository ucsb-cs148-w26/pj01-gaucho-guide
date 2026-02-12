import { useState, useEffect } from "react";
import Header from "./components/Header";
import InputContainer from "./components/InputContainer";
import Sidebar from "./components/Sidebar"; // Import the new Sidebar
import "./App.css";

// Import your logo
import gauchoLogo from "./assets/gaucho-logo.png"; 

function App() {
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [inputMessage, setInputMessage] = useState("");
  const [theme, setTheme] = useState("light");
  const [isLoading, setIsLoading] = useState(true);

  // NEW: Sidebar State
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  useEffect(() => {
    document.body.setAttribute("data-theme", theme);
  }, [theme]);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 2500);
    return () => clearTimeout(timer);
  }, []);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  const handleSubmit = () => {
    if (!file && !inputMessage.trim()) {
      setError("Please type a message or attach a transcript to continue.");
      return;
    }
    setError("");
    console.log("Submitting:", inputMessage, file ? file.name : "No file");
  };

  // Sidebar Handlers
  const handleMouseEnterSidebar = () => setIsSidebarOpen(true);
  const handleMouseLeaveSidebar = () => setIsSidebarOpen(false);

  return (
    <div className="app">
      
      {/* --- SIDEBAR LOGIC --- */}
      
      {/* 1. The Invisible Trigger Strip (Far Left) */}
      <div 
        className="hover-trigger" 
        onMouseEnter={handleMouseEnterSidebar}
      />

      {/* 2. The Sidebar Wrapper (Handles Mouse Leave) */}
      <div 
        className="sidebar-wrapper"
        onMouseLeave={handleMouseLeaveSidebar}
      >
        <Sidebar 
          isOpen={isSidebarOpen} 
          onNewChat={() => console.log("New Chat Started")}
        />
      </div>


      {/* --- REST OF THE APP --- */}

      <div className={`logo-wrapper ${isLoading ? "loading-mode" : "background-mode"}`}>
        <img src={gauchoLogo} alt="Gaucho Logo" className="mascot-logo" />
      </div>

      {/* We add a class to shift content slightly when sidebar is open if you want, 
          but usually for 'hover' mode, we just let it overlay. */}
      <div className={`main-content-wrapper ${!isLoading ? "visible" : ""}`}>
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

    </div>
  );
}

export default App;
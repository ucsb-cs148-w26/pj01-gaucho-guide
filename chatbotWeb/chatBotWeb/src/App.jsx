import { useState } from "react";
import Header from "./components/Header";
import InputContainer from "./components/InputContainer";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");

  const handleSubmit = () => {
    if (!file) {
      setError("Please attach your unofficial transcript before continuing.");
      return;
    }
    setError("");
    //alert("Transcript attached!");
  };

  return (
    <div className="app">
      <Header />

      <div className="center-content">
        <h2 className="prompt">What can I help you with?</h2>

        <InputContainer
          file={file}
          setFile={setFile}
          error={error}
          setError={setError}
          onSubmit={handleSubmit}
        />
      </div>
    </div>
  );
}

export default App;

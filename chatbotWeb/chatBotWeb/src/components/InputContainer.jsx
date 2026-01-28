import { useRef } from "react";
import PlusButton from "./PlusButton";

function InputContainer({
  file,
  setFile,
  error,
  setError,
  onSubmit,
}) {
  const fileInputRef = useRef(null);

  const handlePlusClick = () => {
    fileInputRef.current.click();
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];

    if (!selectedFile) return;

    if (selectedFile.type !== "application/pdf") {
      setError("Please upload your unofficial transcript as a PDF only.");
      setFile(null);
      return;
    }

    setError("");
    setFile(selectedFile);
  };

  return (
    <>
      <div className="input-container">
        <PlusButton onClick={handlePlusClick} />

        <input
          type="text"
          placeholder="Ask a question..."
          className="text-input"
        />

        <button className="submit-btn" onClick={onSubmit}>
          →
        </button>
      </div>

      <input
        type="file"
        accept="application/pdf"
        ref={fileInputRef}
        onChange={handleFileChange}
        hidden
      />

      {error && <p className="error">{error}</p>}
    </>
  );
}

export default InputContainer;

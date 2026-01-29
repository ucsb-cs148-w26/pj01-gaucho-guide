import { useRef, useState } from "react";
import PlusButton from "./PlusButton";

function InputContainer({ 
  file, 
  setFile, 
  inputMessage,     // Received from App
  setInputMessage,  // Received from App
  error, 
  setError, 
  onSubmit 
}) {
  const fileInputRef = useRef(null);
  const [showModal, setShowModal] = useState(false);

  const handlePlusClick = () => {
    setShowModal(true);
  };

  const handleConfirmUpload = () => {
    setShowModal(false);
    fileInputRef.current.click();
  };

  const handleCancel = () => {
    setShowModal(false);
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;

    // This Logic Remains: IF they pick a file, it MUST be a PDF.
    if (selectedFile.type !== "application/pdf") {
      setError("Error: The file selected was not a PDF.");
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
          placeholder={file ? `Attached: ${file.name}` : "Ask a question..."}
          className="text-input"
          // CONNECT TEXT STATE HERE
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          // Allow pressing "Enter" to submit
          onKeyDown={(e) => e.key === 'Enter' && onSubmit()}
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

      {/* MODAL */}
      {showModal && (
        <div className="modal-overlay" onClick={handleCancel}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Upload Transcript</h3>
            <p>
              To provide the best advice, we need your unofficial transcript.
              <br /><br />
              <strong>Please upload a PDF file only.</strong>
            </p>
            <div className="modal-actions">
              <button className="btn-secondary" onClick={handleCancel}>
                Cancel
              </button>
              <button className="btn-primary" onClick={handleConfirmUpload}>
                Select PDF
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default InputContainer;
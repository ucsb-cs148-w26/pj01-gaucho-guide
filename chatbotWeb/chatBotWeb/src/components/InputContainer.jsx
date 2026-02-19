import { useRef, useState } from "react";

// Inline SVG Icons for a Pro look (No npm install needed)
const IconAttachment = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>
);

const IconSend = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
);

function InputContainer({ 
  file, 
  setFile, 
  inputMessage, 
  setInputMessage, 
  error, 
  setError, 
  onSubmit 
}) {
  const fileInputRef = useRef(null);
  const [showModal, setShowModal] = useState(false);

  const handlePlusClick = () => setShowModal(true);
  const handleConfirmUpload = () => { setShowModal(false); fileInputRef.current.click(); };
  const handleCancel = () => setShowModal(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;
    if (selectedFile.type !== "application/pdf") {
      setError("Error: The file selected was not a PDF.");
      setFile(null);
      return;
    }
    setError("");
    setFile(selectedFile);
  };

  // Check if button should be clickable
  const isSendDisabled = !inputMessage.trim() && !file;

  return (
    <>
      <div className="input-container">
        {/* Replaced PlusButton component with this clean icon button */}
        <button 
            className="action-btn upload-btn" 
            onClick={handlePlusClick}
            title="Upload Transcript"
        >
          <IconAttachment />
        </button>

        <input
          type="text"
          placeholder={file ? `Attached: ${file.name}` : "Ask a question..."}
          className="text-input"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && onSubmit()}
        />

        <button 
            className="action-btn send-btn" 
            onClick={onSubmit}
            disabled={isSendDisabled}
        >
          <IconSend />
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

      {showModal && (
        <div className="modal-overlay" onClick={handleCancel}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3 style={{marginTop: 0}}>Upload Transcript</h3>
            <p style={{color: '#888', fontSize: '0.95rem'}}>
              To provide the best advice, we need your unofficial transcript.
              <br /><br />
              <strong>Please upload a PDF file only.</strong>
            </p>
            <div className="modal-actions">
              <button className="btn-secondary" onClick={handleCancel}>Cancel</button>
              <button className="btn-primary" onClick={handleConfirmUpload}>Select PDF</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default InputContainer;
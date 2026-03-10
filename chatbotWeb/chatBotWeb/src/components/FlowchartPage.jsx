import { useRef, useState } from "react";

function FlowchartPage({ apiUrl, getIdToken }) {
  const fileInputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");
  const [imageUrl, setImageUrl] = useState("");

  const handleChoosePdf = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event) => {
    const selectedFile = event.target.files?.[0];
    if (!selectedFile) return;

    if (selectedFile.type !== "application/pdf") {
      setError("Please upload a PDF transcript.");
      setFile(null);
      setImageUrl("");
      return;
    }

    setError("");
    setFile(selectedFile);
    setImageUrl("");
    setStatusMessage("");
  };

  const handleGenerate = async () => {
    if (!file || isGenerating) return;

    setIsGenerating(true);
    setError("");
    setImageUrl("");
    setStatusMessage("");

    try {
      const formData = new FormData();
      formData.append("file", file);

      const token = await getIdToken();
      const res = await fetch(apiUrl("/transcript/flowchart"), {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
        body: formData,
      });

      if (!res.ok) {
        const errText = await res.text();
        throw new Error(errText || `Flowchart generation failed: HTTP ${res.status}`);
      }

      const payload = await res.json();
      setStatusMessage(payload?.message || "Flowchart generated.");
      setImageUrl(typeof payload?.image_url === "string" ? payload.image_url : "");
    } catch (err) {
      const message =
        err instanceof Error && err.message
          ? err.message
          : "Flowchart generation failed.";
      setError(message);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="flowchart-page">
      <div className="flowchart-shell">
        <h2 className="flowchart-title">Flowchart Planner</h2>
        <p className="flowchart-subtitle">
          Upload your transcript PDF to generate your remaining CS prerequisite graph.
        </p>

        <div className="flowchart-actions">
          <button
            type="button"
            className="flowchart-btn flowchart-choose"
            onClick={handleChoosePdf}
          >
            Choose Transcript PDF
          </button>
          <button
            type="button"
            className="flowchart-btn flowchart-generate"
            onClick={handleGenerate}
            disabled={!file || isGenerating}
          >
            {isGenerating ? "Generating..." : "Generate Graph"}
          </button>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept="application/pdf"
          onChange={handleFileChange}
          hidden
        />

        <div className="flowchart-feedback">
          {file && <p className="flowchart-file">Selected: {file.name}</p>}
          {statusMessage && <p className="flowchart-status">{statusMessage}</p>}
          {error && <p className="error">{error}</p>}
        </div>

        {imageUrl && (
          <div className="flowchart-result">
            <img
              src={imageUrl}
              alt="Generated prerequisite flow chart"
              className="flowchart-image"
            />
            <a
              href={imageUrl}
              target="_blank"
              rel="noreferrer"
              className="flowchart-link"
            >
              Open image in new tab
            </a>
          </div>
        )}
      </div>
    </div>
  );
}

export default FlowchartPage;

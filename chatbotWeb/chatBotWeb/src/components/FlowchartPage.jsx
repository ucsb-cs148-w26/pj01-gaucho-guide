import { useCallback, useLayoutEffect, useMemo, useRef, useState } from "react";

function FlowchartPage({ apiUrl, getIdToken }) {
  const fileInputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [planData, setPlanData] = useState(null);
  const [edgePaths, setEdgePaths] = useState([]);
  const graphRef = useRef(null);
  const nodeRefs = useRef(new Map());

  const nodeById = useMemo(() => {
    const map = new Map();
    const nodes = Array.isArray(planData?.nodes) ? planData.nodes : [];
    nodes.forEach((node) => {
      if (node?.id) map.set(node.id, node);
    });
    return map;
  }, [planData]);

  const setNodeRef = useCallback(
    (nodeId) => (el) => {
      if (el) nodeRefs.current.set(nodeId, el);
      else nodeRefs.current.delete(nodeId);
    },
    []
  );

  const recomputeEdgePaths = useCallback(() => {
    if (!planData || !graphRef.current) {
      setEdgePaths([]);
      return;
    }

    const graphBox = graphRef.current.getBoundingClientRect();
    const edges = Array.isArray(planData.edges) ? planData.edges : [];
    const nextPaths = [];

    edges.forEach((edge, index) => {
      const sourceId = edge?.from;
      const targetId = edge?.to;
      if (!sourceId || !targetId) return;

      const sourceEl = nodeRefs.current.get(sourceId);
      const targetEl = nodeRefs.current.get(targetId);
      if (!sourceEl || !targetEl) return;

      const sourceBox = sourceEl.getBoundingClientRect();
      const targetBox = targetEl.getBoundingClientRect();
      const x1 = sourceBox.right - graphBox.left;
      const y1 = sourceBox.top + sourceBox.height / 2 - graphBox.top;
      const x2 = targetBox.left - graphBox.left;
      const y2 = targetBox.top + targetBox.height / 2 - graphBox.top;
      const curve = Math.max(24, (x2 - x1) * 0.45);
      const d = `M ${x1} ${y1} C ${x1 + curve} ${y1}, ${x2 - curve} ${y2}, ${x2} ${y2}`;

      nextPaths.push({
        id: `${sourceId}-${targetId}-${index}`,
        d,
      });
    });

    setEdgePaths(nextPaths);
  }, [planData]);

  useLayoutEffect(() => {
    if (!planData) {
      setEdgePaths([]);
      return undefined;
    }

    const raf = requestAnimationFrame(recomputeEdgePaths);
    window.addEventListener("resize", recomputeEdgePaths);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", recomputeEdgePaths);
    };
  }, [planData, recomputeEdgePaths]);

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
      setPlanData(null);
      setEdgePaths([]);
      return;
    }

    setError("");
    setFile(selectedFile);
    setImageUrl("");
    setPlanData(null);
    setEdgePaths([]);
    setStatusMessage("");
  };

  const handleGenerate = async () => {
    if (!file || isGenerating) return;

    setIsGenerating(true);
    setError("");
    setImageUrl("");
    setPlanData(null);
    setEdgePaths([]);
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
      setPlanData(
        payload?.upper_division_plan && typeof payload.upper_division_plan === "object"
          ? payload.upper_division_plan
          : null
      );
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

  const tiers = Array.isArray(planData?.tiers) ? planData.tiers : [];
  const takenCourses = Array.isArray(planData?.taken_courses) ? planData.taken_courses : [];
  const summary = planData?.summary && typeof planData.summary === "object" ? planData.summary : {};
  const columns = [
    ...(takenCourses.length > 0 ? [{ key: "taken", title: "Have Taken", courses: takenCourses }] : []),
    ...tiers.map((tierCourses, tierIndex) => ({
      key: `tier-${tierIndex + 1}`,
      title: `Tier ${tierIndex + 1}`,
      courses: tierCourses,
    })),
  ];
  const graphMinWidth = Math.max(760, columns.length * 250);

  const getNodeStatusText = (node) => {
    if (!node) return "";
    if (node.taken) return "HAVE TAKEN";
    if (node.eligible_now) return "Can take now";
    const prereqs = Array.isArray(node.remaining_prereqs) ? node.remaining_prereqs : [];
    if (node.unmet_prereq_count === 1 && prereqs.length > 0) {
      return `1 prerequisite left: ${prereqs[0]}`;
    }
    if (prereqs.length > 0) {
      const preview = prereqs.slice(0, 2).join(", ");
      const more = prereqs.length > 2 ? ` (+${prereqs.length - 2} more)` : "";
      return `${prereqs.length} prerequisite(s) left: ${preview}${more}`;
    }
    return `${node.unmet_prereq_count || 0} prerequisite(s) left`;
  };

  return (
    <div className="flowchart-page">
      <div className="flowchart-shell">
        <h2 className="flowchart-title">Flowchart Planner</h2>
        <p className="flowchart-subtitle">
          Upload your transcript PDF to generate a clean CMPSC 0-199 course planner.
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

        {planData && Array.isArray(planData.nodes) && planData.nodes.length > 0 && (
          <div className="flowchart-plan">
            <div className="flowchart-plan-summary">
              <p>
                Remaining CMPSC (0-199) courses:{" "}
                {typeof summary.remaining_cmpsc_0_199_courses === "number"
                  ? summary.remaining_cmpsc_0_199_courses
                  : typeof summary.remaining_upper_division_courses === "number"
                  ? summary.remaining_upper_division_courses
                  : planData.nodes.length}
              </p>
              <p>
                Have taken (from transcript):{" "}
                {typeof summary.taken_cmpsc_0_199_courses === "number"
                  ? summary.taken_cmpsc_0_199_courses
                  : takenCourses.length}
              </p>
              <p>
                Eligible now:{" "}
                {typeof summary.eligible_now === "number"
                  ? summary.eligible_now
                  : planData.nodes.filter((node) => node?.eligible_now).length}
              </p>
            </div>

            <div className="upper-flowchart-viewport">
              <div
                className="upper-flowchart"
                ref={graphRef}
                style={{ minWidth: `${graphMinWidth}px` }}
              >
                <svg className="upper-flowchart-lines" aria-hidden="true">
                  <defs>
                    <marker
                      id="upper-flow-arrow"
                      markerWidth="8"
                      markerHeight="8"
                      refX="7"
                      refY="4"
                      orient="auto"
                    >
                      <path d="M0,0 L8,4 L0,8 z" fill="rgba(20,80,141,0.6)" />
                    </marker>
                  </defs>
                  {edgePaths.map((path) => (
                    <path
                      key={path.id}
                      d={path.d}
                      className="upper-flowchart-edge"
                      markerEnd="url(#upper-flow-arrow)"
                    />
                  ))}
                </svg>

                <div
                  className="upper-flowchart-grid"
                  style={{
                    gridTemplateColumns: `repeat(${Math.max(columns.length, 1)}, minmax(220px, 1fr))`,
                  }}
                >
                  {columns.map((column) => (
                    <section key={column.key} className="upper-tier">
                      <h3 className="upper-tier-title">{column.title}</h3>
                      <div className="upper-tier-nodes">
                        {column.courses.map((courseId) => {
                          const node = nodeById.get(courseId);
                          if (!node) return null;
                          return (
                            <article
                              key={courseId}
                              className={`upper-node ${node.taken ? "taken" : node.eligible_now ? "ready" : "locked"}`}
                              ref={setNodeRef(courseId)}
                              data-node-id={courseId}
                              title={
                                node.taken
                                  ? "Completed in your transcript"
                                  : Array.isArray(node.remaining_prereqs) && node.remaining_prereqs.length > 0
                                  ? `Remaining prerequisites: ${node.remaining_prereqs.join(", ")}`
                                  : "No remaining prerequisites"
                              }
                            >
                              <p className="upper-node-code">{node.label}</p>
                              <p className="upper-node-meta">{getNodeStatusText(node)}</p>
                            </article>
                          );
                        })}
                      </div>
                    </section>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {!planData && imageUrl && (
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

import React, { useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import "./SignIn.css";

const SignIn = () => {
  const { signInWithGoogle, authEnabled } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleGoogleSignIn = async () => {
    if (loading) return;

    setError("");
    setLoading(true);

    try {
      await signInWithGoogle();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Google sign-in failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="signin-container">
      <div className="signin-card">
        <div className="signin-header">
          <h1 className="signin-title">GauchoGuide</h1>
          <p className="signin-subtitle">UCSB Academic Companion</p>
        </div>

        <div className="signin-content">
          <div className="signin-message">
            <h2>Welcome</h2>
            <p>Sign in using your UCSB Google account.</p>
          </div>

          {!authEnabled && (
            <div className="signin-error">
              Firebase auth is not configured.
            </div>
          )}

          {error && <div className="signin-error">{error}</div>}

          <button
            className="signin-btn"
            onClick={handleGoogleSignIn}
            disabled={loading || !authEnabled}
          >
            {loading ? "Signing in..." : "Sign in with Google"}
          </button>

          <div className="signin-notice">
            <p>
              <strong>Restriction:</strong> only <code>@ucsb.edu</code> accounts allowed.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SignIn;
import React, { useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import "./SignIn.css";

const SignIn = () => {
  const { signInWithEmail, signUpWithEmail, authEnabled } = useAuth();

  const [mode, setMode] = useState("signin");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const onSubmit = async (e) => {
    e.preventDefault();
    if (loading) return;

    setError("");
    setLoading(true);

    try {
      if (mode === "signup") {
        await signUpWithEmail(email, password, name);
      } else {
        await signInWithEmail(email, password);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed.");
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
            <h2>{mode === "signup" ? "Create your account" : "Welcome back"}</h2>
            <p>Use your UCSB email to access chat and history.</p>
          </div>

          {!authEnabled && (
            <div className="signin-error">
              Firebase auth is not configured. Add `VITE_FIREBASE_*` vars.
            </div>
          )}

          <form className="signin-form" onSubmit={onSubmit}>
            {mode === "signup" && (
              <input
                className="signin-input"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Full name"
              />
            )}

            <input
              className="signin-input"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@ucsb.edu"
              required
            />

            <input
              className="signin-input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              minLength={6}
              required
            />

            {error && <div className="signin-error">{error}</div>}

            <button className="signin-btn" type="submit" disabled={loading || !authEnabled}>
              {loading ? "Please wait..." : mode === "signup" ? "Create Account" : "Sign In"}
            </button>
          </form>

          <button
            className="signin-toggle"
            type="button"
            onClick={() => {
              setError("");
              setMode((m) => (m === "signup" ? "signin" : "signup"));
            }}
          >
            {mode === "signup"
              ? "Already have an account? Sign in"
              : "Need an account? Sign up"}
          </button>

          <div className="signin-notice">
            <p>
              <strong>Restriction:</strong> only `@ucsb.edu` emails are allowed.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SignIn;

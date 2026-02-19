import React from 'react';

const SignIn = () => {
  const handleSignIn = () => {
    window.location.href = 'http://localhost:8000/auth/login';
  };

  return (
    <div className="signin-page">
      <div className="header">
        <h1>Gaucho Guider</h1>
      </div>

      <div className="signin-center">
        <div className="signin-card">
          <h2 className="signin-title">GauchoGuide</h2>
          <p className="signin-subtitle">Your UCSB Campus Companion</p>

          <p className="signin-message">
            Sign in with your UCSB account to get started
          </p>

          <button className="google-signin-btn" onClick={handleSignIn}>
            Sign in with Google
          </button>

          <p className="signin-notice">
            Only <strong>@ucsb.edu</strong> email addresses are permitted
          </p>
        </div>
      </div>
    </div>
  );
};

export default SignIn;
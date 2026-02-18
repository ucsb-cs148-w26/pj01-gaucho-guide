import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [session, setSession] = useState(null);

  useEffect(() => {
    // Check for session in URL params or localStorage
    const urlParams = new URLSearchParams(window.location.search);
    const urlSession = urlParams.get('session');
    const storedSession = localStorage.getItem('gauchoguide_session');
    
    const activeSession = urlSession || storedSession;
    
    if (activeSession) {
      setSession(activeSession);
      if (urlSession) {
        // Store session and clean URL
        localStorage.setItem('gauchoguide_session', urlSession);
        window.history.replaceState({}, document.title, window.location.pathname);
      }
      verifySession(activeSession);
    } else {
      setLoading(false);
    }
  }, []);

  const verifySession = async (sessionId) => {
    try {
      const response = await fetch(`http://localhost:8000/auth/check?session=${sessionId}`);
      const data = await response.json();
      
      if (data.valid) {
        const userResponse = await fetch(`http://localhost:8000/auth/me?session=${sessionId}`);
        const userData = await userResponse.json();
        setUser(userData);
      } else {
        // Invalid session, clear it
        localStorage.removeItem('gauchoguide_session');
        setSession(null);
      }
    } catch (error) {
      console.error('Session verification failed:', error);
      localStorage.removeItem('gauchoguide_session');
      setSession(null);
    } finally {
      setLoading(false);
    }
  };

  const signIn = () => {
    window.location.href = 'http://localhost:8000/auth/login';
  };

  const signOut = async () => {
    if (session) {
      try {
        await fetch(`http://localhost:8000/auth/logout?session=${session}`, {
          method: 'POST'
        });
      } catch (error) {
        console.error('Logout failed:', error);
      }
    }
    
    localStorage.removeItem('gauchoguide_session');
    setUser(null);
    setSession(null);
  };

  const value = {
    user,
    loading,
    session,
    signIn,
    signOut,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

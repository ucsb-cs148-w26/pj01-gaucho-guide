import React from "react";
import { useAuth } from "../contexts/AuthContext";
import "./Header.css";

// Simple SVG icons for the toggle
const SunIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
);

const MoonIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
);

function Header({ theme, toggleTheme }) {
  const { user, signOut } = useAuth();

  return (
    <div className="header">
      <h1>Gaucho Guider</h1>
      
      {/* New Cooler Toggle Switch */}
      <label className="theme-switch">
        <input 
          type="checkbox" 
          onChange={toggleTheme} 
          checked={theme === "dark"} 
        />
        <span className="slider round">
            <span className="icon-sun"><SunIcon /></span>
            <span className="icon-moon"><MoonIcon /></span>
        </span>
      </label>
      <div className="header-controls">
        {user && (
          <div className="user-profile">
            <div className="user-info">
              <img 
                src={user.picture} 
                alt={user.name} 
                className="user-avatar"
                onError={(e) => {
                  e.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name)}&background=003660&color=febc11&size=32`;
                }}
              />
              <div className="user-details">
                <div className="user-name">{user.name}</div>
                <div className="user-email">{user.email}</div>
              </div>
            </div>
            <button onClick={signOut} className="logout-btn">
              Sign Out
            </button>
          </div>
        )}
        
        {/* Light/Dark Toggle Switch */}
        <label className="theme-switch">
          <input 
            type="checkbox" 
            onChange={toggleTheme} 
            checked={theme === "dark"} 
          />
          <span className="slider"></span>
        </label>
      </div>
    </div>
  );
}

export default Header;
import React from "react";
import { useAuth } from "../contexts/AuthContext";
import "./Header.css";

function Header({ theme, toggleTheme }) {
  const { user, signOut } = useAuth();

  return (
    <div className="header">
      <h1>Gaucho Guider</h1>
      
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
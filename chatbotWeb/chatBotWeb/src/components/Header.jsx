import React from "react";

function Header({ theme, toggleTheme, onProfileClick }) {
  return (
    <div className="header">
      <h1>Gaucho Guider</h1>
      
      <div className="header-controls">
        {/* Profile Button */}
        <button onClick={onProfileClick} className="profile-button">
          <img 
            src="https://ui-avatars.com/api/?name=Student&background=003660&color=febc11&size=32"
            alt="Profile"
            className="user-avatar"
          />
          <span className="profile-text">Profile</span>
        </button>
        
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
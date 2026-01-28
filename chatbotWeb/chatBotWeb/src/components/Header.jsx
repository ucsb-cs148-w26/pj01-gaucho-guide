import React from "react";

function Header({ theme, toggleTheme }) {
  return (
    <div className="header">
      <h1>Gaucho Guider</h1>
      
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
  );
}

export default Header;
import { useAuth } from "../contexts/AuthContext";

const SunIcon = () => (
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <circle cx="12" cy="12" r="5" />
    <line x1="12" y1="1" x2="12" y2="3" />
    <line x1="12" y1="21" x2="12" y2="23" />
    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
    <line x1="1" y1="12" x2="3" y2="12" />
    <line x1="21" y1="12" x2="23" y2="12" />
    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
  </svg>
);

const MoonIcon = () => (
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
  </svg>
);

const GoldLensIcon = () => (
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
  >
    <circle cx="11" cy="11" r="6" />
    <line x1="16.2" y1="16.2" x2="21" y2="21" />
    <line x1="8.5" y1="7.2" x2="10.2" y2="5.4" />
    <line x1="6.9" y1="9.1" x2="5.1" y2="9.1" />
    <line x1="9.1" y1="14.9" x2="9.1" y2="16.7" />
  </svg>
);

function Header({ theme, toggleTheme, onProfileClick }) {
  const { user, signOut } = useAuth();

  const avatarSrc = user?.picture
    ? user.picture
    : "https://ui-avatars.com/api/?name=Student&background=003660&color=febc11&size=32";

  return (
    <div className="header">
      <h1>Gaucho Guider</h1>

      <div className="header-controls">
        <button onClick={onProfileClick} className="profile-button" type="button">
          <img
            src={avatarSrc}
            alt="Profile"
            className="user-avatar"
            onError={(e) => {
              e.currentTarget.src =
                "https://ui-avatars.com/api/?name=Student&background=003660&color=febc11&size=32";
            }}
          />
          <span className="profile-text">Profile</span>
        </button>

        <a
          href="https://my.sa.ucsb.edu/gold/Home.aspx"
          target="_blank"
          rel="noopener noreferrer"
          className="gold-lens-link"
          title="Open UCSB GOLD"
          aria-label="Open UCSB GOLD in a new tab"
        >
          <span className="gold-lens-spark" />
          <span className="gold-lens-icon-wrap">
            <GoldLensIcon />
          </span>
          <span className="gold-lens-text">GOLD</span>
        </a>

        {user && (
          <button onClick={signOut} className="logout-btn" type="button">
            Sign Out
          </button>
        )}

        <label className="theme-switch">
          <input
            type="checkbox"
            onChange={toggleTheme}
            checked={theme === "dark"}
          />
          <span className="slider round">
            <span className="icon-sun">
              <SunIcon />
            </span>
            <span className="icon-moon">
              <MoonIcon />
            </span>
          </span>
        </label>
      </div>
    </div>
  );
}

export default Header;

import { useState } from 'react';
import logo from './assets/logo.png';
import './App.css';

// 1. Create simple placeholder components for your other views
// (You will eventually move these out into their own separate files)
function HomeView() {
  return (
    <div className="view-content">
      <h1 className="hero-title">Ticketing System</h1>
      <p className="hero-subtitle">
        Welcome to your ticketing system. Go to the <code>Tickets</code> tab to view your tickets.
      </p>
    </div>
  );
}

function TicketsView() {
  return (
    <div className="view-content">
      <h2>🎟️ Active Customer Tickets</h2>
      <p style={{ marginTop: '10px', color: '#64748b' }}>
        Database logs live feed. Click on an issue number to sync back to Gmail.
      </p>
      {/* Your ticket database mapping table will go right here later! */}
    </div>
  );
}

function LoginView() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false); // 👈 Track visibility state
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMessage('');

    if (!email || !password) {
      setErrorMessage('Please fill in all fields.');
      setIsLoading(false);
      return;
    }

    try {
      await new Promise((resolve) => setTimeout(resolve, 1500));
      alert(`Successfully logged in as: ${email}`);
    } catch (error) {
      setErrorMessage('Invalid credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-card">
      <div className="login-header">
        <h2>Welcome Back</h2>
        <p>Access your administrative token synchronization dashboard</p>
      </div>

      <form onSubmit={handleLoginSubmit} className="login-form">
        {errorMessage && <div className="error-alert">{errorMessage}</div>}

        <div className="input-group">
          <label htmlFor="email">Email Address</label>
          <input
            id="email"
            type="email"
            placeholder="admin@syncdesk.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={isLoading}
          />
        </div>

        {/* Password Input Field with Eye Toggle */}
        <div className="input-group">
          <label htmlFor="password">Password</label>
          <div className="password-wrapper">
            <input
              id="password"
              type={showPassword ? 'text' : 'password'} // 👈 Dynamically swaps input type
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={isLoading}
              style={{ paddingRight: '45px' }} // Make space so text doesn't overlap the icon
            />
            <button
              type="button" // 👈 CRITICAL: Stops button from accidentally submitting the form
              className="password-toggle-btn"
              onClick={() => setShowPassword(!showPassword)}
              disabled={isLoading}
              title={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? '🙈' : '👁️'}
            </button>
          </div>
        </div>

        <div className="form-actions">
          <a href="#forgot" className="forgot-link">Forgot Password?</a>
        </div>

        <button type="submit" className="login-submit-btn" disabled={isLoading}>
          {isLoading ? (
            <span className="spinner-text">
              <span className="spinner"></span> Authenticating...
            </span>
          ) : (
            'Sign In'
          )}
        </button>
      </form>
    </div>
  );
}

function App() {
  const [activeTab, setActiveTab] = useState('Home');
  const [isDarkMode, setIsDarkMode] = useState(false);

  // 2. Create a helper function to decide which component to display
  const renderTabContent = () => {
    switch (activeTab) {
      case 'Home':
        return <HomeView />;
      case 'Tickets':
        return <TicketsView />;
      case 'Login':
        return <LoginView />;
      default:
        return <HomeView />;
    }
  };

  return (
    <div className={`app-wrapper ${isDarkMode ? 'dark-mode' : 'light-mode'}`}>
      
      {/* NAVIGATION HEADER */}
      <header className="navbar">
        <div className="theme-switch" onClick={() => setIsDarkMode(!isDarkMode)}>
          <span className="theme-icon">{isDarkMode ? '🌙' : '☀️'}</span>
          <div className="switch-track">
            <div className={`switch-thumb ${isDarkMode ? 'active' : ''}`} />
          </div>
        </div>

        {/* Your Dynamic Navigation Tabs mapping loop stays exactly here */}
        <nav className="nav-menu">
          {['Home', 'Tickets', 'Login'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`nav-btn ${activeTab === tab ? 'active' : ''}`}
            >
              {tab}
            </button>
          ))}
        </nav>
      </header>

      {/* HERO / MAIN CONTENT CONTAINER */}
      <main className="hero-container">
        
        {/* Only show the logo when looking at the main Home dashboard page layout */}
        {activeTab === 'Home' && (
          <div className="logo-frame">
            <img src={logo} className="app-logo" alt="SyncDesk Logo" />
          </div>
        )}

        {/* 3. EXECUTE SWITCH-CASE PATH CONTENT */}
        {renderTabContent()}

      </main>
    </div>
  );
}

export default App;
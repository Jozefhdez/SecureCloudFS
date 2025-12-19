import { useNavigate } from "react-router-dom";

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="landing-container">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <div style={{ marginBottom: '2rem' }}>
            <svg viewBox="0 0 24 24" fill="currentColor" style={{ width: '3rem', height: '3rem', margin: '0 auto', color: 'var(--soft-charcoal)' }}>
              <path d="M18.944 11.112C18.507 7.67 15.56 5 12 5 9.244 5 6.85 6.611 5.757 9.15 3.609 9.792 2 11.82 2 14c0 2.757 2.243 5 5 5h11c2.206 0 4-1.794 4-4 0-1.657-1.007-3.085-2.446-3.685l-.61-.203z" />
              <path d="M12 10.5l-3-3m3 3 3-3m-3 3v6" />
            </svg>
          </div>

          <h1 className="hero-title">
            Your files, <em>encrypted</em> before they leave your device
          </h1>

          <p className="hero-subtitle">
            A sanctuary for sensitive documents
          </p>

          <p className="hero-description">
            Your files are encrypted on your device before upload. We never see your data.
          </p>

          <div className="hero-buttons">
            <button
              className="btn btn-large"
              onClick={() => navigate('/login')}
            >
              BEGIN
            </button>
            <button
              className="btn btn-outline btn-large"
              onClick={() => {
                document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
              }}
            >
              EXPLORE
            </button>
          </div>

          {/* Quick Start Commands */}
          <div className="commands-section">
            <h3 className="commands-title">Quick Start</h3>
            <div className="command-steps">
              <div className="command-step">
                <span className="step-label">1. Download client</span>
                <code className="command-code">curl -O https://raw.githubusercontent.com/Jozefhdez/SecureCloudFS/main/securecloud.py</code>
              </div>
              <div className="command-step">
                <span className="step-label">2. Install dependencies</span>
                <code className="command-code">pip install requests cryptography watchdog oci supabase</code>
              </div>
              <div className="command-step">
                <span className="step-label">3. Sync your folder</span>
                <code className="command-code">python3 securecloud.py sync --email your@email.com --password yourpassword --folder ./Documents</code>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="features-section">
        <h2 className="section-title">
          Security as <em>material</em>
        </h2>

        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
              </svg>
            </div>
            <h3>Privacy First</h3>
            <p>
              Encryption happens <em>client-side</em>, before files touch the network.
              Your password never leaves your machine.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 017.843 4.582M12 3a8.997 8.997 0 00-7.843 4.582m15.686 0A11.953 11.953 0 0112 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0121 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0112 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 013 12c0-1.605.42-3.113 1.157-4.418" />
              </svg>
            </div>
            <h3>Universal Access</h3>
            <p>
              View and download from any device. Your encrypted archive,
              accessible wherever you have connectivity.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
              </svg>
            </div>
            <h3>Automatic Sync</h3>
            <p>
              Set a folder and step away. The desktop client quietly maintains
              synchronization, unobtrusive and persistent.
            </p>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works-section">
        <h2 className="section-title">
          How it <em>works</em>
        </h2>

        <div className="steps-grid">
          <div className="step-card">
            <div className="step-number">I</div>
            <h3>Create Account</h3>
            <p>
              Begin with the web interface. A brief registration,
              no billing information required.
            </p>
          </div>

          <div className="step-card">
            <div className="step-number">II</div>
            <h3>Install Client</h3>
            <p>
              Download a single Python script. Dependencies install
              automatically—minimal friction by design.
            </p>
          </div>

          <div className="step-card">
            <div className="step-number">III</div>
            <h3>Begin Syncing</h3>
            <p>
              Point the client to your folder. Encryption and upload
              commence, quiet and thorough.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer" style={{ display: 'flex', justifyContent: 'center' }}>
        <div className="footer-container" style={{ padding: '6rem 3rem', borderTop: '1px solid var(--stone-light)', textAlign: 'center' }}>
          <p style={{ fontSize: '0.875rem', color: 'var(--muted-text)', marginBottom: '0.5rem' }}>
            Made by{' '}
            <a href="https://www.linkedin.com/in/jozefhdez/" target="_blank" rel="noopener noreferrer"
              style={{ textDecoration: 'none', borderBottom: '1px solid var(--stone)', color: 'var(--soft-charcoal)' }}>
              Jozefhdez
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
}

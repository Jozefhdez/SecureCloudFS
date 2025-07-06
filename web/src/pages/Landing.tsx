import { useNavigate } from "react-router-dom";

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="landing-container">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">
            <img src="/logo.png" alt="SecureCloudFS" className="hero-logo" />
            SecureCloudFS
          </h1>
          <p className="hero-subtitle">
            Your files, encrypted and secure in the cloud
          </p>
          <p className="hero-description">
            SecureCloudFS encrypts your files with AES-256 <strong>before</strong> they leave your computer. 
            Even we can't see your data.
          </p>
          
          <div className="hero-buttons">
            <button 
              className="btn btn-primary btn-large"
              onClick={() => navigate('/login')}
            >
              Get Started Free
            </button>
            <button 
              className="btn btn-secondary btn-large"
              onClick={() => {
                document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
              }}
            >
              Learn More
            </button>
          </div>

          <div className="hero-note">
            <p>⚠️ <strong>Important:</strong> To upload files, you need the desktop client. The web app is for viewing and downloading only.</p>
          </div>

          {/* Quick Start Commands */}
          <div className="commands-section">
            <h3 className="commands-title">Quick Start Commands</h3>
            <div className="command-steps">
              <div className="command-step">
                <span className="step-label">1. Download the client</span>
                <code className="command-code">curl -O https://raw.githubusercontent.com/Jozefhdez/SecureCloudFS/main/securecloud.py</code>
              </div>
              <div className="command-step">
                <span className="step-label">2. Install dependencies</span>
                <code className="command-code">pip install requests cryptography watchdog python-dotenv oci supabase</code>
              </div>
              <div className="command-step">
                <span className="step-label">3. Upload and sync a folder</span>
                <code className="command-code">python3 securecloud.py sync --email your@email.com --password yourpass --folder /path/to/folder</code>
              </div>
            </div>
            <div className="github-link">
              <a href="https://github.com/Jozefhdez/SecureCloudFS" target="_blank" rel="noopener noreferrer" className="btn btn-outline">
                <svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
                View on GitHub
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Section Divider */}
      <div className="section-divider"></div>

      {/* Features Section */}
      <section id="features" className="features-section">
        <div className="features-container">
          <h2 className="section-title">Why SecureCloudFS?</h2>
          
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon blue">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
                </svg>
              </div>
              <h3>True Privacy</h3>
              <p>Files are encrypted <em>before</em> upload with your password. We never see your data.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon green">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3s-4.5 4.03-4.5 9 2.015 9 4.5 9z" />
                </svg>
              </div>
              <h3>Access Anywhere</h3>
              <p>Web interface works on any device. Access your files from anywhere with internet.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon purple">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
                </svg>
              </div>
              <h3>Auto Sync</h3>
              <p>Desktop client syncs folders automatically. Set it and forget it.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Section Divider */}
      <div className="section-divider"></div>

      {/* How It Works Section */}
      <section className="how-it-works-section">
        <div className="how-it-works-container">
          <h2 className="section-title">How It Works</h2>
          
          <div className="steps-grid">
            <div className="step-card">
              <div className="step-number">1</div>
              <h3>Create Account</h3>
              <p>Sign up for free using the web app. No credit card required.</p>
            </div>

            <div className="step-card">
              <div className="step-number">2</div>
              <h3>Download Client</h3>
              <p>Download the Python client script to upload and sync files securely.</p>
            </div>

            <div className="step-card">
              <div className="step-number">3</div>
              <h3>Upload & Sync</h3>
              <p>Files are encrypted on your computer before upload. Access them anywhere.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Section Divider */}
      <div className="section-divider"></div>

      {/* Why Two Apps Section */}
      <section className="explanation-section">
        <div className="explanation-container">
          <h2 className="section-title">Why Two Apps?</h2>
          
          <div className="explanation-content">
            <div className="explanation-card">
              <div className="explanation-icon">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 17.25v1.007a3 3 0 01-.879 2.122L7.5 21h9l-.621-.621A3 3 0 0115 18.257V17.25m6-12V15a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 15V5.25m18 0A2.25 2.25 0 0018.75 3H5.25A2.25 2.25 0 003 5.25m18 0V12a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 12V5.25" />
                </svg>
              </div>
              <div className="explanation-text">
                <h3>Desktop Client</h3>
                <p><strong>For Uploading & Syncing</strong></p>
                <p>Files must be encrypted on <em>your computer</em> before upload for true security. This ensures that even we cannot see your data, maintaining zero-knowledge privacy.</p>
              </div>
            </div>

            <div className="explanation-card">
              <div className="explanation-icon">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3s-4.5 4.03-4.5 9 2.015 9 4.5 9z" />
                </svg>
              </div>
              <div className="explanation-text">
                <h3>Web App</h3>
                <p><strong>For Viewing & Downloading</strong></p>
                <p>Access your encrypted files from any device with internet. Download and decrypt files securely in your browser when you need them.</p>
              </div>
            </div>
          </div>

          <div className="explanation-note">
            <p>💡 <strong>The Result:</strong> Maximum security with maximum convenience. Your files are always encrypted, but you can access them from anywhere.</p>
          </div>
        </div>
      </section>

      {/* Section Divider */}
      <div className="section-divider"></div>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-container">
          <h2>Ready to Secure Your Files?</h2>
          <button 
            className="btn btn-primary btn-large"
            onClick={() => navigate('/login')}
          >
            Get Started Free
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-container">
          <p>Made by <a href="https://www.linkedin.com/in/jozefhdez/" target="_blank" rel="noopener noreferrer">Jozef Hernandez</a></p>
        </div>
      </footer>
    </div>
  );
}

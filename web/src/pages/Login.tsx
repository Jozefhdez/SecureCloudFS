import { useState } from "react";
import { supabase } from "../services/supabaseClient";
import { useNavigate } from "react-router-dom";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLogin, setIsLogin] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setInfo(null);
    setLoading(true);

    try {
      if (isLogin) {
        const { data, error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });

        if (error) {
          switch (error.message) {
            case "Invalid login credentials":
              setError("Incorrect email or password.");
              break;
            case "Email not confirmed":
              setError("You must confirm your email before logging in.");
              break;
            default:
              setError("Login error: " + error.message);
          }
          return;
        }

        if (data.session) {
          // Save credentials for local API
          sessionStorage.setItem('scfs_credentials', JSON.stringify({ email, password }));
          
          // Configure credentials for local API
          try {
            const { SecureCloudAPI } = await import('../services/apiService');
            SecureCloudAPI.setCredentials(email, password);
          } catch (err) {
            console.log('[WARNING] Local API not available, using Supabase only');
          }
          
          navigate("/dashboard");
        } else {
          setError("Could not sign in: invalid session.");
        }

      } else {
        const { error } = await supabase.auth.signUp({
          email,
          password,
        });

        if (error) {
          if (error.message.includes("User already registered")) {
            setError("Email is already registered.");
          } else {
            setError("Registration error: " + error.message);
          }
          return;
        }

        // In most cases, Supabase sends a confirmation email
        setInfo("Registration successful. Check your email to confirm your account.");
      }

    } catch (err) {
      console.error("Unhandled error:", err);
      setError("An unexpected error occurred.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1 className="login-title">
          SecureCloudFS
        </h1>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
        
        {info && (
          <div className="success-message">
            {info}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email" className="form-label">
              Email Address
            </label>
            <input
              id="email"
              type="email"
              placeholder="Enter your email"
              className="form-input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password" className="form-label">
              Password
            </label>
            <input
              id="password"
              type="password"
              placeholder="Enter your password"
              className="form-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-full"
            disabled={loading}
          >
            {loading ? (
              <div className="spinner"></div>
            ) : (
              isLogin ? "Sign In" : "Create Account"
            )}
          </button>
        </form>

        <div className="login-spacing">
          <button
            className="btn btn-secondary btn-full"
            onClick={() => {
              setIsLogin(!isLogin);
              setError(null);
              setInfo(null);
            }}
          >
            {isLogin ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
          </button>
        </div>
      </div>
    </div>
  );
}


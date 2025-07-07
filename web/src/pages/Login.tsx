import { useState } from "react";
import { supabase } from "../services/supabaseClient";
import { useNavigate } from "react-router-dom";

// Security validation patterns
const EMAIL_REGEX = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
const PASSWORD_REGEX = /^[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?~`\s]{6,128}$/;
const SQL_INJECTION_PATTERNS = [
  /('|(\\)|;|--|\/\*|\*\/)/i,
  /(union|select|insert|update|delete|drop|create|alter|exec|execute)/i,
  /(script|javascript|vbscript|onload|onerror|onclick)/i,
  /(<|>|&lt;|&gt;)/i
];

const validateInput = (input: string, type: 'email' | 'password'): { isValid: boolean; error?: string } => {
  // Check for SQL injection patterns
  for (const pattern of SQL_INJECTION_PATTERNS) {
    if (pattern.test(input)) {
      return { isValid: false, error: 'Invalid characters detected. Please use only allowed characters.' };
    }
  }
  
  // Type-specific validation
  if (type === 'email') {
    if (!EMAIL_REGEX.test(input)) {
      return { isValid: false, error: 'Please enter a valid email address.' };
    }
  } else if (type === 'password') {
    if (input.length < 6) {
      return { isValid: false, error: 'Password must be at least 6 characters long.' };
    }
    if (input.length > 128) {
      return { isValid: false, error: 'Password must be less than 128 characters long.' };
    }
    if (!PASSWORD_REGEX.test(input)) {
      return { isValid: false, error: 'Password contains invalid characters.' };
    }
  }
  
  return { isValid: true };
};

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLogin, setIsLogin] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [emailError, setEmailError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleEmailChange = (value: string) => {
    setEmail(value);
    setError(null);
    
    if (value.length > 0) {
      const validation = validateInput(value, 'email');
      setEmailError(validation.isValid ? null : validation.error || 'Invalid email');
    } else {
      setEmailError(null);
    }
  };

  const handlePasswordChange = (value: string) => {
    setPassword(value);
    setError(null);
    
    if (value.length > 0) {
      const validation = validateInput(value, 'password');
      setPasswordError(validation.isValid ? null : validation.error || 'Invalid password');
    } else {
      setPasswordError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setInfo(null);
    setLoading(true);

    try {
      // Validate email
      const emailValidation = validateInput(email, 'email');
      if (!emailValidation.isValid) {
        setError(emailValidation.error || 'Invalid email format');
        setLoading(false);
        return;
      }

      // Validate password
      const passwordValidation = validateInput(password, 'password');
      if (!passwordValidation.isValid) {
        setError(passwordValidation.error || 'Invalid password format');
        setLoading(false);
        return;
      }

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
        <div className="login-header">
          <button 
            className="btn-back"
            onClick={() => navigate('/')}
            title="Back to home"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
            </svg>
          </button>
          
          <h1 className="login-title">
            SecureCloudFS
          </h1>
        </div>

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
              className={`form-input ${emailError ? 'error' : ''}`}
              value={email}
              onChange={(e) => handleEmailChange(e.target.value)}
              required
            />
            {emailError && (
              <div className="field-error">
                {emailError}
              </div>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="password" className="form-label">
              Password
            </label>
            <input
              id="password"
              type="password"
              placeholder="Enter your password"
              className={`form-input ${passwordError ? 'error' : ''}`}
              value={password}
              onChange={(e) => handlePasswordChange(e.target.value)}
              required
            />
            {passwordError && (
              <div className="field-error">
                {passwordError}
              </div>
            )}
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-full"
            disabled={loading || emailError !== null || passwordError !== null || !email || !password}
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


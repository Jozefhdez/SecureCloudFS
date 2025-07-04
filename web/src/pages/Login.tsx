import { useState } from "react";
import { supabase } from "../services/supabaseClient";
import { useNavigate } from "react-router-dom";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLogin, setIsLogin] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setInfo(null);

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
            console.log('⚠️ API local no disponible, usando solo Supabase');
          }
          
          navigate("/dashboard");
        } else {
          setError("No se pudo iniciar sesión: sesión inválida.");
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

        // En la mayoría de los casos, Supabase envía un correo de confirmación
        setInfo("Registro exitoso. Revisa tu correo para confirmar tu cuenta.");
      }

    } catch (err) {
      console.error("Unhandled error:", err);
      setError("Ocurrió un error inesperado.");
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen">
      <h1 className="text-2xl font-semibold mb-4">
        {isLogin ? "Login" : "Register"}
      </h1>
      <form onSubmit={handleSubmit} className="w-full max-w-sm">
        <input
          type="email"
          placeholder="Email"
          className="w-full mb-2 p-2 border rounded"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          className="w-full mb-4 p-2 border rounded"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
        >
          {isLogin ? "Login" : "Register"}
        </button>
      </form>
      <button
        className="mt-4 text-sm text-gray-600 underline"
        onClick={() => {
          setIsLogin(!isLogin);
          setError(null);
          setInfo(null);
        }}
      >
        {isLogin ? "Create an account" : "Already have an account? Log in"}
      </button>

      {error && <p className="text-red-600 mt-4">{error}</p>}
      {info && <p className="text-green-600 mt-4">{info}</p>}
    </div>
  );
}


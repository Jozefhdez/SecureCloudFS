import { useEffect, useState } from "react";
import { supabase } from "@/services/supabaseClient";
import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom";
import type { Session } from "@supabase/supabase-js";
import LoginPage from "@/pages/Login";
import DashboardPage from "@/pages/Dashboard";

function App() {
  const [session, setSession] = useState<Session | null>(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });

    return () => subscription.unsubscribe();
  }, []);

  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={session ? <Navigate to="/dashboard" /> : <LoginPage />}
        />
        <Route
          path="/dashboard"
          element={session ? <DashboardPage /> : <Navigate to="/" />}
        />
      </Routes>
    </Router>
  );
}

export default App;

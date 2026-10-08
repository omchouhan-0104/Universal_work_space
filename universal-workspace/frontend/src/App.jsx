import { useState } from "react";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";

function App() {
  const [page, setPage] = useState(
    localStorage.getItem("access_token")
      ? "dashboard"
      : "login"
  );

  const handleLoginSuccess = () => {
    setPage("dashboard");
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    setPage("login");
  };

  if (page === "dashboard") {
    return (
      <Dashboard onLogout={handleLogout} />
    );
  }

  return (
    <div>
      {page === "login" && (
        <>
          <Login
            onLoginSuccess={handleLoginSuccess}
          />

          <button
            type="button"
            onClick={() => setPage("register")}
          >
            Create Account
          </button>
        </>
      )}

      {page === "register" && (
        <>
          <Register />

          <button
            type="button"
            onClick={() => setPage("login")}
          >
            Already have an account? Login
          </button>
        </>
      )}
    </div>
  );
}

export default App;
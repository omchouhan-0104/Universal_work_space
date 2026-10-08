import { useState } from "react";
import { loginUser } from "../services/authService";

function Login({ onLoginSuccess }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();

    setError("");
    setLoading(true);

    try {
      // Login and save JWT
      const data = await loginUser(
        email,
        password
      );

      console.log("Login successful:", data);

      // Tell App.jsx that login succeeded
      onLoginSuccess();

    } catch (err) {
      console.error("Login error:", err);

      setError(
        err.response?.data?.detail ||
        "Login failed"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Login</h1>

      <form onSubmit={handleLogin}>

        <div>
          <label>Email</label>

          <input
            type="email"
            value={email}
            onChange={(e) =>
              setEmail(e.target.value)
            }
            required
          />
        </div>

        <div>
          <label>Password</label>

          <input
            type="password"
            value={password}
            onChange={(e) =>
              setPassword(e.target.value)
            }
            required
          />
        </div>

        <button
          type="submit"
          disabled={loading}
        >
          {loading
            ? "Logging in..."
            : "Login"}
        </button>

      </form>

      {error && (
        <p>{error}</p>
      )}
    </div>
  );
}

export default Login;

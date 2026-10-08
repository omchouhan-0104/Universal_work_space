import { useState } from "react";
import { registerUser } from "../services/authService";

function Register() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleRegister = async (e) => {
    e.preventDefault();

    setMessage("");
    setError("");

    try {
      // Send the three values separately
      // because registerUser(name, email, password)
      // expects three arguments.
      const data = await registerUser(
        name,
        email,
        password
      );

      console.log("Registration response:", data);

      setMessage("Registration successful!");

      // Clear form after successful registration
      setName("");
      setEmail("");
      setPassword("");
    } catch (err) {
      console.error("Registration error:", err);

      setError(
        err.response?.data?.detail ||
        "Registration failed"
      );
    }
  };

  return (
    <div>
      <h1>Create Account</h1>

      <form onSubmit={handleRegister}>
        <div>
          <label>Name</label>

          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            minLength={2}
            maxLength={100}
          />
        </div>

        <div>
          <label>Email</label>

          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        <div>
          <label>Password</label>

          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
            maxLength={128}
          />
        </div>

        <button type="submit">
          Register
        </button>
      </form>

      {message && (
        <p>{message}</p>
      )}

      {error && (
        <p>{error}</p>
      )}
    </div>
  );
}

export default Register;
import { useState } from "react";
import { loginUser } from "../../services/authService";
import "../styles/login.css";

function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleLogin() {
  setMessage("");

  if (!username || !password) {
    setMessage("Please enter username and password.");
    return;
  }

  try {
    setLoading(true);

    const data = await loginUser(username, password);

    setMessage("Login successful.");
    console.log("Login response:", data);
  } catch (error) {
    console.error(error);
    setMessage(error.message || "Cannot connect to the server.");
  } finally {
    setLoading(false);
  }
}

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-header">
          <div className="logo-circle">DTC</div>
          <h1>Data Tracking Center</h1>
          <p>Web Frontend Version</p>
        </div>

        <form className="login-form">
          <label>Username</label>
          <input
            type="text"
            placeholder="Enter username"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
          />

          <label>Password</label>
          <input
            type="password"
            placeholder="Enter password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />

          <button type="button" onClick={handleLogin} disabled={loading}>
            {loading ? "Signing in..." : "Sign In"}
          </button>

          {message && <p className="message">{message}</p>}
        </form>

        <div className="login-footer">
          <p>FastAPI + Supabase + Render</p>
        </div>
      </div>
    </div>
  );
}

export default Login;
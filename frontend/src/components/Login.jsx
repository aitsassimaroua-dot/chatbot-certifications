import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import logo from "../assets/logo-certiprofile.png";
import "../index.css";

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        setError("Email ou mot de passe incorrect");
        setLoading(false);
        return;
      }

      const data = await res.json();

      localStorage.removeItem("user_id");
      localStorage.removeItem("email");

      localStorage.setItem("user_id", String(data.user_id));
      localStorage.setItem("email", email);

      navigate("/chat");
    } catch (err) {
      console.error(err);
      setError("Impossible de contacter le serveur");
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <img src={logo} alt="CertiProfile" className="auth-logo" />
        <h2>CertiProfile AI</h2>
        <p className="subtitle">Trouvez votre certification idéale</p>

        <form onSubmit={handleLogin}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <input
            type="password"
            placeholder="Mot de passe"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          {error && <p className="error">{error}</p>}

          <button type="submit" disabled={loading}>
            {loading ? "Connexion..." : "Se connecter"}
          </button>
        </form>

        <p className="auth-link">
          Pas de compte ? <Link to="/register">Créer un compte</Link>
        </p>
      </div>
    </div>
  );
}

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import logo from "../assets/logo-certiprofile.png";
import "../index.css";

export default function Register() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (password !== confirmPassword) {
      setError("Les mots de passe ne correspondent pas");
      return;
    }

    if (password.length < 6) {
      setError("Le mot de passe doit contenir au moins 6 caractères");
      return;
    }

    setLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        setError(errorData.detail || "Erreur lors de l'inscription");
        setLoading(false);
        return;
      }

      setSuccess("Compte créé avec succès ! Redirection...");
      setTimeout(() => navigate("/"), 1500);

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
        <h2>Créer un compte</h2>
        <p className="subtitle">Rejoignez CertiProfile AI</p>

        <form onSubmit={handleRegister}>
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

          <input
            type="password"
            placeholder="Confirmer le mot de passe"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />

          {error && <p className="error">{error}</p>}
          {success && <p className="success">{success}</p>}

          <button type="submit" disabled={loading}>
            {loading ? "Création..." : "S'inscrire"}
          </button>
        </form>

        <p className="auth-link">
          Déjà un compte ? <Link to="/">Se connecter</Link>
        </p>
      </div>
    </div>
  );
}

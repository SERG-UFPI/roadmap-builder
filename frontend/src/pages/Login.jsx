import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { apiFetch } from "../api/client";
import { useAuth } from "../auth/useAuth";

export default function Login() {
  const { user, loading, login, devLogin } = useAuth();
  const [devAvailable, setDevAvailable] = useState(false);
  const [devError, setDevError] = useState("");

  useEffect(() => {
    apiFetch("/api/health", { allowUnauthorized: true })
      .then((h) => setDevAvailable(Boolean(h?.dev_login)))
      .catch(() => setDevAvailable(false));
  }, []);

  if (loading) return <div className="page-center">Carregando…</div>;
  if (user) return <Navigate to="/" replace />;

  const enterDev = async () => {
    setDevError("");
    try {
      await devLogin();
    } catch (e) {
      setDevError(e.message);
    }
  };

  return (
    <div className="welcome-screen">
      <div className="welcome-content">
        <img
          src="/roadmap.png"
          alt="Roadmap Builder"
          className="welcome-logo"
        />
        <span className="welcome-tag">RoadMap Builder</span>
        <h1>Construa Roadmaps Inteligentes para o GitHub</h1>
        <p>
          Gestão centralizada de milestones, etiquetas, cronogramas e painéis de
          projeto — para vários projetos e times.
        </p>
        <button onClick={login} className="btn-welcome-start">
          Entrar com GitHub ➔
        </button>
        {devAvailable && (
          <div className="dev-login">
            <button
              type="button"
              className="btn-secondary"
              onClick={enterDev}
              title="Disponível só em desenvolvimento (DEV_LOGIN_ENABLED=true). Não usa o GitHub."
            >
              Entrar como usuário local (dev)
            </button>
            {devError && <div className="message error">{devError}</div>}
          </div>
        )}
      </div>
    </div>
  );
}

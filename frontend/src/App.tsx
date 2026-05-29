import { useEffect, useState } from "react";
import { Link, Route, Routes } from "react-router-dom";
import type { Lang } from "./types";
import { t } from "./i18n";
import {
  AI4AUTH_LOGOUT_URL,
  ai4authLoginUrl,
  getIdentity,
  type Identity,
} from "./auth";
import LanguageSwitcher from "./components/LanguageSwitcher";
import Survey from "./components/Survey";
import Dashboard from "./components/Dashboard";

function IconCloud() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z" />
    </svg>
  );
}

function IconSun() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M2 12h2M20 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
    </svg>
  );
}

function IconMoon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 12.79A9 9 0 1 1 11.21 3a7 7 0 0 0 9.79 9.79z" />
    </svg>
  );
}

export default function App() {
  const [lang, setLang] = useState<Lang>("it");
  const [isDark, setIsDark] = useState(() => {
    const saved = localStorage.getItem("theme");
    if (saved) return saved === "dark";
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  });
  // undefined = ancora in caricamento; null = anonimo.
  const [identity, setIdentity] = useState<Identity | null | undefined>(undefined);

  useEffect(() => {
    getIdentity().then(setIdentity);
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", isDark);
    localStorage.setItem("theme", isDark ? "dark" : "light");
  }, [isDark]);

  return (
    <div className="app">
      <header className="topbar">
        <Link to="/" className="brand">
          <span className="brand-icon"><IconCloud /></span>
          <span className="brand-copy">
            {t(lang, "appTitle")}
            <small>{t(lang, "subtitle")}</small>
          </span>
        </Link>
        <div className="topbar-actions">
          {identity?.is_admin && (
            <Link className="btn" to="/admin">
              {t(lang, "adminArea")}
            </Link>
          )}
          {identity?.authenticated ? (
            <a className="btn" href={AI4AUTH_LOGOUT_URL}>
              {t(lang, "logout")}
            </a>
          ) : (
            identity !== undefined && (
              <a className="btn" href={ai4authLoginUrl("/admin")}>
                {t(lang, "adminLogin")}
              </a>
            )
          )}
          <button
            type="button"
            className="icon-btn"
            title={isDark ? "Light mode" : "Dark mode"}
            onClick={() => setIsDark((d) => !d)}
          >
            {isDark ? <IconSun /> : <IconMoon />}
          </button>
          <LanguageSwitcher lang={lang} onChange={setLang} />
        </div>
      </header>

      <main className="app-main">
        <Routes>
          <Route path="/" element={<Home lang={lang} />} />
          <Route path="/survey/:qid" element={<Survey lang={lang} />} />
          {/* Area amministrazione: protetta a livello nginx (ai4auth forward-auth).
              Non linkata dalla home pubblica. */}
          <Route path="/admin" element={<AdminHome lang={lang} />} />
          <Route path="/admin/dashboard/:qid" element={<Dashboard lang={lang} />} />
        </Routes>
      </main>
    </div>
  );
}

// Home pubblica: solo avvio questionari (rispondenti). Nessun link dashboard.
function Home({ lang }: { lang: Lang }) {
  return (
    <div className="home">
      <div className="page-head">
        <span className="eyebrow">PRAXIS</span>
        <h1>{t(lang, "chooseQuestionnaire")}</h1>
        <p>{lang === "it" ? "Seleziona il percorso di rilevazione e compila il questionario." : "Select a survey path and complete the questionnaire."}</p>
      </div>
      <div className="cards">
        {(["studenti", "insegnanti"] as const).map((qid) => (
          <div className="card" key={qid}>
            <h2>{qid === "studenti" ? t(lang, "students") : t(lang, "teachers")}</h2>
            <p>{lang === "it" ? "Questionario di follow-up sull'uso dell'AI nei contesti educativi." : "Follow-up questionnaire on AI use in education contexts."}</p>
            <div className="card-actions">
              <Link className="btn primary" to={`/survey/${qid}`}>
                {t(lang, "start")}
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Pannello amministrazione: accesso alle dashboard. Raggiungibile solo via /admin
// (protetto da ai4auth, gruppo admins).
function AdminHome({ lang }: { lang: Lang }) {
  return (
    <div className="home">
      <div className="page-head">
        <span className="eyebrow">{t(lang, "adminArea")}</span>
        <h1>{t(lang, "adminPanel")}</h1>
        <p>{lang === "it" ? "Apri le dashboard live per monitorare risposte, medie e distribuzioni." : "Open live dashboards to monitor responses, means, and distributions."}</p>
      </div>
      <div className="cards">
        {(["studenti", "insegnanti"] as const).map((qid) => (
          <div className="card" key={qid}>
            <h2>{qid === "studenti" ? t(lang, "students") : t(lang, "teachers")}</h2>
            <p>{lang === "it" ? "Vista amministrativa con aggiornamento in tempo reale." : "Administrative view with real-time updates."}</p>
            <div className="card-actions">
              <Link className="btn primary" to={`/admin/dashboard/${qid}`}>
                {t(lang, "dashboard")}
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

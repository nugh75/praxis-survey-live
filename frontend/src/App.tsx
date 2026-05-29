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

export default function App() {
  const [lang, setLang] = useState<Lang>("it");
  // undefined = ancora in caricamento; null = anonimo.
  const [identity, setIdentity] = useState<Identity | null | undefined>(undefined);

  useEffect(() => {
    getIdentity().then(setIdentity);
  }, []);

  return (
    <div className="app">
      <header className="topbar">
        <Link to="/" className="brand">
          {t(lang, "appTitle")}
          <small>{t(lang, "subtitle")}</small>
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
          <LanguageSwitcher lang={lang} onChange={setLang} />
        </div>
      </header>

      <main>
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
      <h1>{t(lang, "chooseQuestionnaire")}</h1>
      <div className="cards">
        {(["studenti", "insegnanti"] as const).map((qid) => (
          <div className="card" key={qid}>
            <h2>{qid === "studenti" ? t(lang, "students") : t(lang, "teachers")}</h2>
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
      <h1>{t(lang, "adminPanel")}</h1>
      <div className="cards">
        {(["studenti", "insegnanti"] as const).map((qid) => (
          <div className="card" key={qid}>
            <h2>{qid === "studenti" ? t(lang, "students") : t(lang, "teachers")}</h2>
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

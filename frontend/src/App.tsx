import { useState } from "react";
import { Link, Route, Routes } from "react-router-dom";
import type { Lang } from "./types";
import { t } from "./i18n";
import LanguageSwitcher from "./components/LanguageSwitcher";
import Survey from "./components/Survey";
import Dashboard from "./components/Dashboard";

export default function App() {
  const [lang, setLang] = useState<Lang>("it");

  return (
    <div className="app">
      <header className="topbar">
        <Link to="/" className="brand">
          {t(lang, "appTitle")}
          <small>{t(lang, "subtitle")}</small>
        </Link>
        <LanguageSwitcher lang={lang} onChange={setLang} />
      </header>

      <main>
        <Routes>
          <Route path="/" element={<Home lang={lang} />} />
          <Route path="/survey/:qid" element={<Survey lang={lang} />} />
          <Route path="/dashboard/:qid" element={<Dashboard lang={lang} />} />
        </Routes>
      </main>
    </div>
  );
}

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
              <Link className="btn" to={`/dashboard/${qid}`}>
                {t(lang, "dashboard")}
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

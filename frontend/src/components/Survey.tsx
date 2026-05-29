import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import type { Lang, Questionnaire } from "../types";
import { fetchQuestionnaire, submitResponse } from "../api";
import { t } from "../i18n";
import QuestionField from "./QuestionField";

type Val = string | number | boolean | null;

export default function Survey({ lang }: { lang: Lang }) {
  const { qid } = useParams();
  const [q, setQ] = useState<Questionnaire | null>(null);
  const [answers, setAnswers] = useState<Record<string, Val>>({});
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (qid) fetchQuestionnaire(qid).then(setQ).catch(() => setError("not found"));
  }, [qid]);

  if (error) return <p className="error">{error}</p>;
  if (!q) return <p className="loading">{t(lang, "waiting")}</p>;

  if (done)
    return (
      <div className="thanks">
        <h2>{t(lang, "submitted")}</h2>
        <Link className="btn primary" to={`/dashboard/${q.id}`}>
          {t(lang, "dashboard")}
        </Link>{" "}
        <Link className="btn" to="/">
          {t(lang, "backHome")}
        </Link>
      </div>
    );

  const missing = q.questions.filter(
    (item) => item.required && (answers[item.key] === undefined || answers[item.key] === null || answers[item.key] === "")
  );
  const answered = q.questions.filter((item) => {
    const value = answers[item.key];
    return value !== undefined && value !== null && value !== "";
  }).length;
  const progress = Math.round((answered / q.questions.length) * 100);

  async function handleSubmit() {
    if (!q) return;
    if (missing.length > 0) {
      setError(t(lang, "required"));
      document.getElementById(`q-${missing[0].key}`)?.scrollIntoView({ behavior: "smooth" });
      return;
    }
    setError(null);
    await submitResponse({
      questionnaire: q.id,
      lang,
      answers: Object.entries(answers).map(([question_key, value]) => ({ question_key, value })),
    });
    setDone(true);
  }

  return (
    <div className="survey">
      <div className="survey-head">
        <div>
          <span className="eyebrow">PRAXIS</span>
          <h1>{q.title[lang]}</h1>
        </div>
        <div className="survey-progress" aria-label={`${progress}%`}>
          <span>{answered}/{q.questions.length}</span>
          <div className="progress-track">
            <div style={{ width: `${progress}%` }} />
          </div>
        </div>
      </div>
      <form onSubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
        {q.questions.map((item, i) => (
          <div id={`q-${item.key}`} className="q-block" key={item.key}>
            <div className="q-index">
              <span>{t(lang, "question")} {i + 1} {t(lang, "of")} {q.questions.length}</span>
              <span className="dim-tag">{item.dimension}</span>
            </div>
            <QuestionField
              q={item}
              lang={lang}
              value={answers[item.key] ?? null}
              onChange={(v) => setAnswers((a) => ({ ...a, [item.key]: v }))}
            />
          </div>
        ))}
        {error && <p className="error">{error}</p>}
        <button className="btn primary big" type="submit">
          {t(lang, "submit")}
        </button>
      </form>
    </div>
  );
}

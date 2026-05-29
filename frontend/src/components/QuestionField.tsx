import type { Lang, Question } from "../types";
import { t } from "../i18n";

type Val = string | number | boolean | null;

export default function QuestionField({
  q,
  lang,
  value,
  onChange,
}: {
  q: Question;
  lang: Lang;
  value: Val;
  onChange: (v: Val) => void;
}) {
  const label = q.label[lang];
  const note = q.note?.[lang];

  return (
    <div className="field">
      <label className="q-label">
        {label}
        {q.required && <span className="req">*</span>}
      </label>
      {note && <p className="q-note">{note}</p>}

      {q.type === "likert" && (
        <div className="likert">
          {Array.from({ length: (q.scale_max ?? 7) - (q.scale_min ?? 1) + 1 }, (_, i) => {
            const n = (q.scale_min ?? 1) + i;
            const anchor = q.anchors?.[lang]?.[i];
            return (
              <button
                key={n}
                type="button"
                className={value === n ? "likert-opt active" : "likert-opt"}
                onClick={() => onChange(n)}
                title={anchor}
              >
                <span className="num">{n}</span>
                {anchor && <span className="anchor">{anchor}</span>}
              </button>
            );
          })}
        </div>
      )}

      {q.type === "number" && (
        <input
          type="number"
          min={q.min ?? 0}
          max={q.max ?? undefined}
          value={value === null || value === undefined ? "" : String(value)}
          onChange={(e) => onChange(e.target.value === "" ? null : Number(e.target.value))}
        />
      )}

      {q.type === "boolean" && (
        <div className="bool">
          {[
            { v: "Si'", l: t(lang, "yes") },
            { v: "No", l: t(lang, "no") },
          ].map((o) => (
            <button
              key={o.v}
              type="button"
              className={value === o.v ? "btn active" : "btn"}
              onClick={() => onChange(o.v)}
            >
              {o.l}
            </button>
          ))}
        </div>
      )}

      {q.type === "single" && (
        <div className="options">
          {q.options?.map((o) => (
            <label key={o.value} className={value === o.value ? "opt active" : "opt"}>
              <input
                type="radio"
                name={q.key}
                checked={value === o.value}
                onChange={() => onChange(o.value)}
              />
              {o.label[lang]}
            </label>
          ))}
        </div>
      )}

      {q.type === "text" && (
        <textarea
          rows={3}
          value={value === null || value === undefined ? "" : String(value)}
          onChange={(e) => onChange(e.target.value === "" ? null : e.target.value)}
        />
      )}
    </div>
  );
}

import type { Lang } from "../types";

export default function LanguageSwitcher({
  lang,
  onChange,
}: {
  lang: Lang;
  onChange: (l: Lang) => void;
}) {
  return (
    <div className="lang-switch">
      {(["it", "en"] as const).map((l) => (
        <button
          key={l}
          className={l === lang ? "active" : ""}
          onClick={() => onChange(l)}
        >
          {l.toUpperCase()}
        </button>
      ))}
    </div>
  );
}

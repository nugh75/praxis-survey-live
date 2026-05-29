export type Lang = "it" | "en";

export interface LangText {
  it: string;
  en: string;
}

export interface Option {
  value: string;
  label: LangText;
}

export interface Question {
  key: string;
  dimension: string;
  type: "likert" | "number" | "boolean" | "single" | "multi" | "text";
  label: LangText;
  note?: { it: string | null; en: string | null };
  required: boolean;
  scale_min?: number;
  scale_max?: number;
  anchors?: { it: string[]; en: string[] };
  options?: Option[];
  min?: number;
  max?: number | null;
}

export interface Questionnaire {
  id: string;
  title: LangText;
  questions: Question[];
}

export interface PraxisMean {
  dimension: string;
  label: LangText;
  mean: number;
  n_items: number;
}

export interface ItemStat {
  key: string;
  dimension: string;
  type: string;
  label: LangText;
  n: number;
  mean: number | null;
  min: number | null;
  max: number | null;
}

export interface CategoricalStat {
  key: string;
  dimension: string;
  label: LangText;
  type: string;
  counts: Record<string, number>;
}

export interface Stats {
  questionnaire: string;
  title: LangText;
  total_responses: number;
  praxis_means: PraxisMean[];
  items: ItemStat[];
  categorical: CategoricalStat[];
}

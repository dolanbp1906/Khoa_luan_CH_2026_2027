export type Citation = {
  provision_id: string;
  label: string;
  document_title: string;
  document_number: string;
  article_no: number;
  article_title: string;
  clause_no: number;
  quote: string;
  score: number;
  in_force: boolean;
  expiry_note: string | null;
  source_url: string;
};

export type AskResponse = {
  question: string;
  mode: string;
  concepts: { id: string; label: string; score: number }[];
  answer: string;
  abstain: boolean;
  abstain_reason: string | null;
  citations: Citation[];
  generator: string;
  disclaimer: string;
};

export type ConceptCard = {
  id: string;
  label: string;
  alts: string[];
  broader: string[];
  provisions: { provision_id: string; label: string; article_title: string }[];
};

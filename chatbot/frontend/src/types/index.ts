/**
 * Types for the RAG Chatbot Frontend
 */

export enum QueryMode {
  SELECTED_TEXT = "selected-text",
  BOOK_WIDE = "book-wide",
}

export interface Source {
  passage_id: string;
  chapter: string;
  section: string;
  page: number | null;
  snippet: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  sources?: Source[];
  refused?: boolean;
  confidence?: number;
  mode?: QueryMode;
}

export interface ChatRequest {
  query: string;
  mode: QueryMode;
  context?: string;
  session_id?: string;
}

export interface ChatResponse {
  query_id: string;
  answer: string;
  sources: Source[];
  refused: boolean;
  refusal_reason?: string;
  confidence?: number;
  latency_ms: number;
  mode: QueryMode;
}

export interface BookChapter {
  id: string;
  number: number;
  title: string;
  content: string;
  sections: BookSection[];
}

export interface BookSection {
  id: string;
  title: string;
  content: string;
}

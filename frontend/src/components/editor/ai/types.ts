import type { Asset } from "@/app/contexts/LineageView";

export type AIMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

export type MessageHistoryPayload = {
  project_id: string;
  model: string;
  context_files: Array<string>;
  context_preview: string | null;
  asset_id: string | undefined;
  related_assets: Asset[] | undefined;
  asset_links: any | undefined;
  column_links: any | undefined;
  message_history: Omit<AIMessage, "id">[];
  compiled_query: string | null;
  file_problems: string[] | null;
  custom_selections: Array<{
    selection: string;
    start_line: number;
    end_line: number;
    file_name: string;
  }> | null;
};

export type AICompiledSql = {
  compiled_query: string;
  file_name: string;
}

export type AIQueryPreview = {
  table: string;
  file_name: string;
}

export type AIFileProblems = {
  problems: string[];
  file_name: string;
}

export type AICustomSelections = {
  selection: string;
  start_line: number;
  end_line: number;
  file_name: string;
}

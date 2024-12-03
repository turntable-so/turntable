import type { Asset } from "@/app/contexts/LineageView";

export type AIMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

export type MessageHistoryPayload = {
  model: string;
  context_files: Array<string>;
  asset_id: string | undefined;
  related_assets: Asset[] | undefined;
  asset_links: any | undefined;
  column_links: any | undefined;
  message_history: Omit<AIMessage, "id">[];
};

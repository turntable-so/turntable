export type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

export type MessageHistory = Array<Message>;

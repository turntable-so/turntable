import { Button } from "@/components/ui/button";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import { updateSettings } from "../actions/actions";
import type { Settings } from "./types";

type ApiKeysTableProps = {
  apiKeys: Settings["api_keys"];
};

export function ApiKeysTable({ apiKeys }: ApiKeysTableProps) {
  const [isSaving, setIsSaving] = useState(false);
  const [openAIKey, setOpenAIKey] = useState("");
  const [anthropicKey, setAnthropicKey] = useState("");

  const handleSubmit = async () => {
    try {
      setIsSaving(true);
      const response = await updateSettings({
        api_keys: {
          openai_api_key: openAIKey,
          anthropic_api_key: anthropicKey,
        },
      });

      if (!response.ok) {
        console.error("Failed to update API keys");
      } else {
        console.log("API keys updated successfully");
      }
    } catch (error) {
      console.error("Error updating API keys:", error);
    } finally {
      setIsSaving(false);
    }
  };

  useEffect(() => {
    setOpenAIKey(apiKeys.openai_api_key);
    setAnthropicKey(apiKeys.anthropic_api_key);
  }, [apiKeys]);

  return (
    <div className="flex flex-col gap-4">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>API Key</TableHead>
            <TableHead>Value</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow>
            <TableCell className="font-semibold">OpenAI</TableCell>
            <TableCell>
              <input
                type="text"
                value={openAIKey}
                onChange={(e) => setOpenAIKey(e.target.value)}
                className="w-full p-2 border rounded"
              />
            </TableCell>
          </TableRow>
          <TableRow>
            <TableCell className="font-semibold">Anthropic</TableCell>
            <TableCell>
              <input
                type="text"
                value={anthropicKey}
                onChange={(e) => setAnthropicKey(e.target.value)}
                className="w-full p-2 border rounded"
              />
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
      <div className="flex justify-end">
        <Button onClick={handleSubmit} disabled={isSaving}>
          {isSaving ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            "Save"
          )}
        </Button>
      </div>
    </div>
  );
}

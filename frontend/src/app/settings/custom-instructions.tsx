import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import { updateSettings } from "../actions/actions";

type CustomInstructionsProps = {
  instructions?: string;
};

export function CustomInstructions({ instructions }: CustomInstructionsProps) {
  const [isSaving, setIsSaving] = useState(false);
  const [customInstructions, setCustomInstructions] = useState("");

  const handleSubmit = async () => {
    try {
      setIsSaving(true);
      await updateSettings({
        ai_custom_instructions: customInstructions,
      });
    } catch (error) {
      console.error("Error updating custom instructions:", error);
    } finally {
      setIsSaving(false);
    }
  };

  useEffect(() => {
    setCustomInstructions(instructions || "");
  }, [instructions]);

  return (
    <div className="flex flex-col gap-4">
      <textarea
        value={customInstructions}
        onChange={(e) => setCustomInstructions(e.target.value)}
        className="w-full p-2 border rounded min-h-[200px]"
        placeholder="Custom instructions"
      />
      <div className="flex justify-end">
        <Button onClick={handleSubmit} disabled={isSaving}>
          {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : "Save"}
        </Button>
      </div>
    </div>
  );
} 
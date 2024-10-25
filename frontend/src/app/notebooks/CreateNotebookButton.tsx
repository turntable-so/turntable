"use client";
import { defaultEditorContent } from "@/lib/content";
import { Plus } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { LoaderButton } from "../../components/ui/LoadingSpinner";
import { Button } from "../../components/ui/button";
import { createNotebook } from "../actions/actions";

export default function CreateNotebookButton() {
  const router = useRouter();

  const [isLoading, setIsLoading] = useState<boolean>(false);

  const onNewNotebookClick = async () => {
    setIsLoading(true);
    const notebook = await createNotebook({
      title: "(Untitled)",
      json_contents: JSON.stringify(defaultEditorContent),
    });
    if (notebook.id) {
      router.push(`/notebooks/${notebook.id}`);
    }
  };

  return (
    <LoaderButton
      className="border"
      variant="secondary"
      onClick={onNewNotebookClick}
      isLoading={isLoading}
    >
      <Plus className="size-4 mr-2" />
      <div className="">New</div>
    </LoaderButton>
  );
}

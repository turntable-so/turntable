import { ReloadIcon } from "@radix-ui/react-icons";
import { useEffect, useRef, useState } from "react";
import { Card, CardContent } from "./ui/card";

import { Play, Sparkle, Sparkles } from "lucide-react";
import { useAppContext } from "../contexts/AppContext";
import { Button } from "./ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "./ui/popover";

export default function PromptBlock() {
  const [text, setText] = useState("");
  const [showRecommendationCard, setShowRecommendationCard] = useState(false);
  const [recommendations, setRecommendations] = useState<string[]>([]);
  const { sources } = useAppContext();
  const [isLoading, setIsLoading] = useState(false);

  const [content, setContent] = useState([
    { type: "text", text: "Initial text " },
  ]);
  const editableRef = useRef(null);

  useEffect(() => {
    // Convert content state to HTML
    const html = content
      .map((part) => {
        if (part.type === "mention") {
          return `<span class="mention">${part.text}</span>`;
        }
        return part.text;
      })
      .join("");

    if (editableRef.current) {
      // @ts-ignore
      editableRef.current.innerHTML = html;
    }
  }, [content]);

  const fetchRecommendations = () => {
    const searchTerm = text.split("@")[1];
    const relevantSources = sources
      .map((source: any) => ({
        ...source,
        relevancy:
          (2 * source.table.toLowerCase().includes(searchTerm) ? 1 : 0) +
          (source.id.toLowerCase().includes(searchTerm) ? 1 : 0),
      }))
      .sort((a: any, b: any) => b.relevancy - a.relevancy)
      .slice(0, 5);

    setRecommendations(relevantSources);
  };

  const onTextChange = (text: string) => {
    setText(text);
    const words = text.split(/\s+/);
    if (words.at(-1)?.startsWith("@")) {
      fetchRecommendations();
      setShowRecommendationCard(true);
    } else {
      setShowRecommendationCard(false);
    }
  };

  const selectRecommendation = (i: number) => {
    const selectedRecommendation = recommendations[i];
    const words = text.split(/\s+/);

    // @ts-ignore
    const replaceWith = `@ref:source-${selectedRecommendation.id}`;
    words[words.length - 1] = replaceWith;
    const newText = words.join(" ");
    setText(newText);
    setShowRecommendationCard(false);
  };

  const generate = () => {
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
    }, 3000);
  };

  const handleKeyUp = (e: any) => {
    const cursorPosition = e.target.selectionStart;
    const textUpToCursor = text.substring(0, cursorPosition);
    const indexOfLastAt = textUpToCursor.lastIndexOf("@");

    if (indexOfLastAt !== -1) {
      // Logic to display mentions dropdown
      // You can use `indexOfLastAt` to determine the position for the dropdown
      // and `cursorPosition` to know where to insert the selected mention
    }
  };

  return (
    <div>
      {showRecommendationCard && (
        <Card className="rounded-md border-none">
          <CardContent className="p-2 text-muted-foreground bg-muted">
            {recommendations.map((recommendation, i) => (
              // @ts-ignore
              <div
                className="cursor-pointer py-0.5 px-2 hover:bg-gray-200 rounded-md"
                onClick={() => selectRecommendation(i)}
                key={i}
              >
                {recommendation.table} ({recommendation.database})
              </div>
            ))}
          </CardContent>
        </Card>
      )}
      <Card className="rounded-md">
        <CardContent className="p-4 text-muted-foreground bg-muted/50">
          <textarea
            value={text}
            onChange={(e) => onTextChange(e.target.value)}
            onKeyUp={handleKeyUp}
            className="resize-none w-full bg-transparent outline-none text-md"
          />{" "}
        </CardContent>
      </Card>
      <div className="float-right my-4">
        <Button variant="outline" onClick={generate} disabled={isLoading}>
          {isLoading ? (
            <ReloadIcon className="mr-2 h-4 w-4 animate-spin text-purple-500" />
          ) : (
            <Sparkles className="mr-2 w-4 h-4 text-purple-500" />
          )}
          Generate
        </Button>
      </div>
    </div>
  );
}

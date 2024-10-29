import { Button } from "@/components/ui/button";
import { ChevronLeft } from "lucide-react";
import { useRouter } from "next/navigation";

export default function BackToConnectionsButton() {
  const router = useRouter();

  return (
    <Button
      variant="ghost"
      className="my-4 text-lg  flex items-center space-x-4"
      onClick={() => {
        router.push("/connections");
      }}
    >
      <ChevronLeft className="size-5" />
      <div>Add a new connection</div>
    </Button>
  );
}

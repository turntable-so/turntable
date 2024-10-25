import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

export default function WorkspaceIcon({
  name,
  iconUrl,
}: {
  name: string;
  iconUrl?: string;
}) {
  return (
    <Avatar className="size-16 rounded-md bg-muted">
      <AvatarImage src={iconUrl} />
      <AvatarFallback>{name[0].slice(0).toUpperCase()}</AvatarFallback>
    </Avatar>
  );
}

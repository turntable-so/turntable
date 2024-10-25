"use client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardTitle } from "@/components/ui/card";
import CreateWorkspaceForm from "@/components/workspaces/create-workspace-form";
import NewWorkspaceButton from "@/components/workspaces/new-workspace-button";
import WorkspaceIcon from "@/components/workspaces/workspace-icon";
import { Loader2, PlusIcon } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getWorkspaces, switchWorkspace } from "../actions/actions";
import useSession from "../hooks/use-session";

type Workspace = {
  id: string;
  name: string;
  icon_url: string;
  icon_file: string;
  member_count: number;
};

export default function WorkspacePage() {
  const router = useRouter();
  const { user } = useSession();

  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingWorkspaceId, setLoadingWorkspaceId] = useState<string | null>(
    null,
  );

  console.log({ user });

  useEffect(() => {
    const fetchWorkspaces = async () => {
      setLoading(true);
      const workspaces = await getWorkspaces();
      setWorkspaces(workspaces);
      setLoading(false);
    };
    fetchWorkspaces();
  }, []);

  const handleSwitchWorkspace = async (workspaceId: string) => {
    setLoadingWorkspaceId(workspaceId);
    const workspace = await switchWorkspace(workspaceId);
    if (workspace.id) {
      window.location.href = "/connections";
    }
  };

  return (
    <div className="h-screen w-full flex flex-col bg-muted items-center mt-[150px]">
      <Card className="w-[500px]">
        <CardTitle className="p-6 text-xl">Choose a Workspace</CardTitle>
        <CardContent className="text-xl font-medium my-8 space-y-4">
          {loading ? (
            <div className="flex items-center justify-center">
              <Loader2 className="text-center h-6 w-6 animate-spin opacity-50" />
            </div>
          ) : (
            workspaces.map((workspace: Workspace) => (
              <div
                className=" flex justify-between  items-center hover:bg-gray-50 p-4 rounded-md cursor-pointer"
                key={workspace.id}
                onClick={() => handleSwitchWorkspace(workspace.id)}
              >
                <div className="flex items-center space-x-4">
                  <WorkspaceIcon
                    name={workspace.name}
                    iconUrl={workspace.icon_url || ""}
                  />
                  <div>
                    <p className="text-lg font-medium">{workspace.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {workspace.member_count}{" "}
                      {workspace.member_count === 1 ? "Member" : "Members"}
                    </p>
                  </div>
                </div>
                <div>
                  {loadingWorkspaceId === workspace.id && (
                    <Loader2 className="text-center h-6 w-6 animate-spin opacity-50" />
                  )}
                </div>
              </div>
            ))
          )}
          <div className="pt-4">
            <NewWorkspaceButton />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

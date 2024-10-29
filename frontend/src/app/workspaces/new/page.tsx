import { Card, CardContent, CardTitle } from "@/components/ui/card";
import CreateWorkspaceForm from "@/components/workspaces/create-workspace-form";

export default async function WorkspacePage() {
  return (
    <div className="h-screen w-full flex flex-col bg-muted items-center mt-[150px]">
      <Card className="w-[500px]">
        <CardTitle className="p-6 text-xl">Create a Workspace</CardTitle>
        <CardContent className="text-xl font-medium my-8">
          <CreateWorkspaceForm />
        </CardContent>
      </Card>
    </div>
  );
}

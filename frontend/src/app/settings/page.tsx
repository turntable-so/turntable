import { Suspense } from "react";
import FullWidthPageLayout from "../../components/layout/FullWidthPageLayout";
import AuthenticationProfiles from "./AuthenticationProfiles";
import AISettings from "./AISettings";
import { getWorkspaceSettings } from "../actions/actions";

export default async function SettingsPage() {
  const authProfiles = [] as any;
  const workspaceSettings = await getWorkspaceSettings();

  return (
    <FullWidthPageLayout title="Settings">
      <div className="w-full py-4 rounded-lg space-y-16">
        <Suspense>
          <AuthenticationProfiles authProfiles={authProfiles || []} />
        </Suspense>
        <AISettings workspaceSettings={workspaceSettings}></AISettings>
      </div>
    </FullWidthPageLayout>
  );
}

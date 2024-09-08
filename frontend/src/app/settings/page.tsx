import FullWidthPageLayout from "../../components/layout/FullWidthPageLayout";
import AICredentialsConfiguration from "./AICredentialsConfiguration";

export default async function SettingsPage() {
  return (
    <FullWidthPageLayout title="Settings">
      <div className="w-full py-4 rounded-lg space-y-16">
        <AICredentialsConfiguration />
      </div>
    </FullWidthPageLayout>
  );
}

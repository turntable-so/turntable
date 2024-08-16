import { Suspense } from "react";
import FullWidthPageLayout from "../../components/layout/FullWidthPageLayout";
import AuthenticationProfiles from "./AuthenticationProfiles";


export default async function SettingsPage() {

    const authProfiles = [] as any

    return (
        <FullWidthPageLayout title='Settings'>
            <div className='w-full py-4 rounded-lg space-y-16' >
                <Suspense>
                    <AuthenticationProfiles authProfiles={authProfiles || []} />
                </Suspense>
            </div>
        </FullWidthPageLayout>
    )
} 
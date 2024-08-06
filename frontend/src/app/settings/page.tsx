import FullWidthPageLayout from "../../components/layout/FullWidthPageLayout";
import { getAuthProfiles, getGithubInstallation } from '../actions/actions'
import AuthenticationProfiles from "./AuthenticationProfiles";
import GithubConnection from "./GithubConnection";
import { Suspense } from "react";


export default async function SettingsPage() {

    const authProfiles = await getAuthProfiles() || []

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
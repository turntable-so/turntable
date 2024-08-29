// app/PostHogPageView.tsx
'use client'

import { usePathname, useSearchParams } from "next/navigation";
import { usePostHog } from 'posthog-js/react';
import { useEffect } from "react";
import useSession from "./hooks/use-session";

export default function PostHogPageView(): null {
    const pathname = usePathname();
    const searchParams = useSearchParams();
    const posthog = usePostHog();
    const session = useSession()
    useEffect(() => {
        // Track pageviews
        if (pathname && posthog) {
            let url = window.origin + pathname
            if (searchParams.toString()) {
                url = url + `?${searchParams.toString()}`
            }
            posthog.capture(
                '$pageview',
                {
                    '$current_url': url,
                }
            )
        }
        if (session?.user && session.user.current_workspace) {
            posthog.identify(`${session.user.current_workspace.id}:${session.user.id}`,
                {
                    email: session.user.email,
                    workspace_id: session.user?.current_workspace.id,
                    workspace_name: session.user?.current_workspace.name,
                }
            )
        }
    }, [pathname, searchParams, session])

    return null
}
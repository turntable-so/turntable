"use client";

import { usePathname, useSearchParams } from "next/navigation";
import { usePostHog } from "posthog-js/react";
import { useEffect } from "react";
import useSession from "./hooks/use-session";

export default function PostHogPageView(): null {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const posthog = usePostHog();
  const { user } = useSession();

  useEffect(() => {
    // Track pageviews
    if (pathname && posthog) {
      let url = window.origin + pathname;
      if (searchParams.toString()) {
        url = url + `?${searchParams.toString()}`;
      }
      posthog.capture("$pageview", {
        $current_url: url,
      });
    }
  }, [pathname, searchParams, posthog]);

  useEffect(() => {
    if (user && user.current_workspace) {
      posthog.identify(`${user.current_workspace.id}:${user.id}`, {
        email: user.email,
        workspace_id: user.current_workspace.id,
        workspace_name: user.current_workspace.name,
      });
    }
  }, [posthog, user]);

  return null;
}

import { fetcherAuth } from "@/app/fetcher";
import { AuthActions } from "@/lib/auth";
import { useRouter } from "next/navigation";
import { usePostHog } from "posthog-js/react";
import useSWR from "swr";

const useSession = () => {
  const router = useRouter();

  const { data: user, mutate } = useSWR("/auth/users/me/", fetcherAuth);

  const { logout: authLogout, removeTokens } = AuthActions();

  const posthog = usePostHog();

  const logout = () => {
    authLogout()
      .res(() => {
        removeTokens();
        mutate();
        router.push("/");
        if (posthog._isIdentified()) {
          posthog.reset();
        }
      })
      .catch(() => {
        removeTokens();
        router.push("/");
      });
  };

  return {
    user,
    logout,
    mutate,
  };
};

export default useSession;

import { useState, useEffect } from 'react';
import useSWR, { useSWRConfig } from "swr";
import { fetcherAuth } from '@/app/fetcher'
import { AuthActions } from "@/lib/auth";
import { useRouter } from 'next/navigation';

const useSession = () => {
    const router = useRouter();

    const { data: user, mutate } = useSWR("/auth/users/me/", fetcherAuth);

    const { logout: authLogout, removeTokens } = AuthActions();

    const logout = () => {
        authLogout()
            .res(() => {
                removeTokens();
                mutate()
                router.push("/");
            })
            .catch(() => {
                removeTokens();
                router.push("/");
            });
    };

    return {
        user,
        logout,
    }
}

export default useSession;
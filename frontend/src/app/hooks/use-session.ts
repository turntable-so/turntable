import { fetcherAuth } from '@/app/fetcher';
import { AuthActions } from "@/lib/auth";
import { useRouter } from 'next/navigation';
import { useState, useEffect, useCallback } from 'react';

const useSession = () => {
    const router = useRouter();
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    const { logout: authLogout, removeTokens } = AuthActions();

    // Function to fetch user data
    const fetchUser = useCallback(async () => {
        setLoading(true);
        try {
            const fetchedUser = await fetcherAuth('/auth/users/me/');
            setUser(fetchedUser);
        } catch (error) {
            console.error('Failed to fetch user:', error);
            setUser(null);
        } finally {
            setLoading(false);
        }
    }, []);

    // Call fetchUser on component mount
    useEffect(() => {
        fetchUser();
    }, [fetchUser]);

    const logout = async () => {
        try {
            await authLogout();
            removeTokens();
            setUser(null);
            router.push("/");
        } catch (error) {
            removeTokens();
            router.push("/");
        }
    };

    return {
        user: user || {},
        logout,
        refreshSession: fetchUser, // Expose a method to manually refresh session
        loading, // Indicate whether the session is being loaded
    };
};

export default useSession;

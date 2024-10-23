'use client'

import { useEffect, useState } from 'react';

export default function Tableau() {
    const [token, setToken] = useState<string | null>(null);

    useEffect(() => {
        const fetchToken = async () => {
            try {
                const response = await fetch('/api/tableau/sso');
                const data = await response.json();
                setToken(data.token);
            } catch (error) {
                console.error('Error fetching Tableau SSO token:', error);
            }
        };

        fetchToken();
    }, []);

    return (
        <div className="w-full h-full">
            {token ? <tableau-viz id="tableauViz"       
                src='https://us-east-1.online.tableau.com/views/Superstore/Overview'      
                token={token}
                >
            </tableau-viz> : null}
        </div>
    )
}
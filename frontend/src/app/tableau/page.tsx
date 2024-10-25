'use client'

import { useEffect, useState } from 'react';

export default function Tableau() {
    const [token, setToken] = useState<string | null>(null);

    const handleClick = () => {
        const viz = document.getElementById('tableau-viz');
        const sheet = viz.workbook.activeSheet;
        console.log("sheet: ", sheet);
        console.log("sheet worksheets:", sheet.worksheets);
        const saleMap = sheet.worksheets.find(ws => ws.name =="Sale Map");
        console.log("saleMap: ", saleMap);
        saleMap.applyFilterAsync("Region", ["Central"], "replace");
    }

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
        <div className="w-full h-full p-16">
            {
                token ? 
                <div>
                    <button onClick={handleClick}>Click me!</button>
                    <tableau-viz 
                        id='tableau-viz' 
                        src='https://us-east-1.online.tableau.com/t/turntable/views/Superstore/Overview' 
                        width='1280' 
                        height='1280' 
                        toolbar='bottom' 
                        token={token} 
                    >
                    </tableau-viz> 
                </div>
                : null
            }
        </div>
    )
}

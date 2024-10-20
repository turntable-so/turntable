'use client'
const EMBEDDING_KEY = '9da7582d6097b88628ca3fd6ea77c56fd5cf9abf7bfa118c0806ada16f1872c1'

const init = {
    headers: {
        "Content-Type": "application/json",
        "X-API-KEY": 'mb_N1WYELqzZqTrH7PFAMLMLlHUJZHOsHOUA5Q/qA97mGs=',
    },
};

const host = "http://metabase:4000";

async function getGroups() {
    const response = await fetch(`${host}/api/permissions/group`, {
        ...init,
    });
    return response.json();
}


import { useEffect, useState } from "react"

export default function EmbeddedCard({ questionId }: { questionId: number }) {

    const [iframeUrl, setIframeUrl] = useState('')
    const [isLoading, setIsLoading] = useState(false)

    useEffect(() => {
        const fetchData = async () => {
            setIsLoading(true)
            const response = await fetch(
                `http://localhost:3000/api/metabase/iframe_url?questionId=${questionId}`,
                {
                    method: 'GET'
                }
            )
            if (response.ok) {
                const data = await response.json()
                console.log({ data })
                setIframeUrl(data.iframeUrl)
            }
            setIsLoading(false)
        }
        fetchData()
    }, [])
    return (
        <div className="w-full h-[600px]">
            {iframeUrl && (
                <iframe
                    src={iframeUrl}
                    frameBorder={0}
                    width="100%"
                    height="100%"
                    allowTransparency
                />
            )
            }
        </div >
    )
}
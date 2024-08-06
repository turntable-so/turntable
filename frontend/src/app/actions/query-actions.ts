'use server'

import { fetcher } from "../fetcher";
import { cookies } from 'next/headers'


export async function getQueryBlockResult({ blockId }: {
    blockId: string
}) {
    const response = await fetcher(`/blocks/${blockId}/`, {
        cookies,
        method: "GET",
    });
    if (response.ok) {
        return await response.json();
    }
    return null
}
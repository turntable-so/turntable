export async function fetchApi(
    url: string,
    options: RequestInit = {},
    body: any | null = null
) {
    const resp = ''
    const jwt = 'await resp.getToken()'
    const headers = options.headers || {};

    if (jwt) {
        // @ts-ignore
        headers["Authorization"] = `Bearer ${jwt}`;
    }

    if (body) {
        return fetch(url, {
            ...options,
            headers: { ...headers, "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });
    }

    return fetch(url, {
        ...options,
        headers: headers,
    });
};
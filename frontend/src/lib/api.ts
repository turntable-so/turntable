export async function fetchApi(
  url: string,
  options: RequestInit = {},
  body: any | null = null,
) {
  const resp = "";
  const jwt = "await resp.getToken()";
  const headers: any = options.headers || {};

  if (jwt) {
    // @ts-ignore
    headers["Authorization"] = `Bearer ${jwt}`;
  }

  if (body) {
    if (!(body instanceof FormData)) {
      headers["Content-Type"] = "application/json";
    }

    return fetch(url, {
      ...options,
      headers: { ...headers },
      body: JSON.stringify(body),
    });
  }

  return fetch(url, {
    ...options,
    headers: headers,
  });
}

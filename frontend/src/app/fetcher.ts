import getUrl from "@/app/url";
import {AuthActions} from "@/lib/auth";
// Extract necessary functions from the AuthActions utility.
const { handleJWTRefresh, storeToken, getToken, removeTokens, isTokenExpired } =
  AuthActions();
const baseUrl = getUrl();
const fetchWithAuth = async (url: string, options = {} as any) => {
  let token = getToken("access", options?.cookies);

  if (token && isTokenExpired(token as string)) {
    try {
      console.log(`Token ${token} is expired, attempting a refresh`)
      const { access, refresh } = (await (
        await handleJWTRefresh(options?.cookies)
      ).json()) as any;
      console.log("Got new tokens: ", { access, refresh });
      storeToken(access, "access");
      storeToken(refresh, "refresh");
      token = access;
    } catch (e) {
      console.error("Error during token refresh:", e.message);
      removeTokens();
      return;
    }
  }

  const headers = {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  if (!(options?.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(url, { ...options, headers });

  if (response.status === 401) {
    try {
      const { access, refresh } = (await (
        await handleJWTRefresh(options?.cookies)
      ).json()) as any;
      storeToken(access, "access");
      storeToken(refresh, "refresh");

      const retryHeaders = {
        ...headers,
        Authorization: `Bearer ${access}`,
      };

      const retryResponse = await fetch(url, {
        ...options,
        headers: retryHeaders,
      });
      if (retryResponse.status === 401) {
        removeTokens();
      }

      return retryResponse.json();
    } catch (err) {
      removeTokens();
    }
  }

  return response;
};

export const fetcher = (
  url: string,
  options: {
    method?: string;
    body?: any;
    next?: any;
    cookies?: any;
    headers?: any;
  } = {},
  signal: any = null,
): Promise<any> => {
  const { method = "GET", body, next, cookies } = options;
  const fullUrl = `${baseUrl}${url}`;
  const fetchOptions: any = {
    method,
    ...(body
      ? { body: body instanceof FormData ? body : JSON.stringify(body) }
      : {}),
    ...(cookies ? { cookies } : {}),
    signal,
  };
  if (!(body instanceof FormData)) {
    fetchOptions["headers"] = {
      "Content-Type": "application/json",
    };
  }

  if (next?.tags) {
    // @ts-ignore
    fetchOptions.headers = {
      // @ts-ignore
      ...fetchOptions.headers,
      "Cache-Control": `max-age=0, s-maxage=86400, stale-while-revalidate, tag=${next.tags.join(",")}`,
    };
  }

  return fetchWithAuth(fullUrl, fetchOptions);
};

export const fetcherAuth = async (url: string): Promise<any> => {
  const response = await fetchWithAuth(`${baseUrl}${url}`);
  return response.json();
};

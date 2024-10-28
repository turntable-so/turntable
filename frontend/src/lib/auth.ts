import getUrl from "@/app/url";
import { deleteCookie, getCookie, setCookie } from "cookies-next";
import wretch from "wretch";
// Base API setup for making HTTP requests
const baseUrl = getUrl();
const api = wretch(baseUrl).accept("application/json");

/**
 * Stores a token in cookies.
 * @param {string} token - The token to be stored.
 * @param {"access" | "refresh"} type - The type of the token (access or refresh).
 */
const storeToken = (token: string, type: "access" | "refresh") => {
  setCookie(type + "Token", token);
};

/**
 * Retrieves a token from cookies.
 * @param {"access" | "refresh"} type - The type of the token to retrieve (access or refresh).
 * @returns {string | undefined} The token, if found.
 */
const getToken = (type: string, cookies?: any) => {
  if (typeof window === "undefined" && cookies) {
    return getCookie(type + "Token", { cookies });
  } else {
    return getCookie(type + "Token");
  }
};

/**
 * Removes both access and refresh tokens from cookies.
 */
const removeTokens = () => {
  deleteCookie("accessToken");
  deleteCookie("refreshToken");
};

/**
 * Registers a new user.
 * @param {string} email - The email of the account.
 * @param {string} username - The username of the account.
 * @param {string} password - The password for the account.
 * @returns {Promise} A promise that resolves with the registration response.
 */
const register = (email: string, password: string, invitationCode = "") => {
  if (invitationCode && invitationCode.length > 0) {
    return api.post({ email, password, invitationCode }, "/users/invitations/");
  }
  return api.post({ email, password, invitationCode }, "/auth/users/");
};

/**
 * Logs in a user and stores access and refresh tokens.
 * @param {string} email - The user's email.
 * @param {string} password - The user's password.
 * @returns {Promise} A promise that resolves with the login response.
 */
const login = (email: string, password: string) => {
  return api.post({ email, password }, "/auth/jwt/create");
};

const loginOauth = (provider: string, token: string, invitationCode = "") => {
  return api.post(
    { provider, token, invitation_code: invitationCode },
    "/oauth/auth",
  );
};

/**
 * Logout a user.
 * @returns {Promise} A promise that resolves with the login response.
 */
const logout = () => {
  const refreshToken = getToken("refresh");
  return api.post({ refresh: refreshToken }, "/auth/logout/");
};

/**
 * Refreshes the JWT token using the stored refresh token.
 * @returns {Promise} A promise that resolves with the new access token.
 */
const handleJWTRefresh = (cookies: any = null) => {
  const refreshToken = getToken("refresh", cookies);
  return api.post({ refresh: refreshToken }, "/auth/jwt/refresh");
};

/**
 * Initiates a password reset request.
 * @param {string} email - The email of the user requesting a password reset.
 * @returns {Promise} A promise that resolves with the password reset response.
 */
const resetPassword = (email: string) => {
  return api.post({ email }, "/auth/users/reset_password/");
};

/**
 * Confirms the password reset with new password details.
 * @param {string} new_password - The new password.
 * @param {string} re_new_password - Confirmation of the new password.
 * @param {string} token - The token for authenticating the password reset request.
 * @param {string} uid - The user ID.
 * @returns {Promise} A promise that resolves with the password reset confirmation response.
 */
const resetPasswordConfirm = (
  new_password: string,
  re_new_password: string,
  token: string,
  uid: string,
) => {
  return api.post(
    { uid, token, new_password, re_new_password },
    "/auth/users/reset_password_confirm/",
  );
};

/**
 * Exports authentication-related actions.
 * @returns {Object} An object containing all the auth actions.
 */
export const AuthActions = () => {
  return {
    login,
    resetPasswordConfirm,
    handleJWTRefresh,
    register,
    resetPassword,
    storeToken,
    getToken,
    logout,
    removeTokens,
    loginOauth,
  };
};

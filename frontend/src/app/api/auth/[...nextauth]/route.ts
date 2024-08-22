import NextAuth from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import GitHubProvider from "next-auth/providers/github";
import CredentialsProvider from "next-auth/providers/credentials";
import { AuthActions } from "@/lib/auth";
import { NextResponse } from "next/server";
const { login, storeToken, loginOauth } = AuthActions();
import {
  setCookie, deleteCookie,
} from "cookies-next";
import { cookies } from "next/headers";



const handler = NextAuth({
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID || "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
      authorization: {
        params: {
          invitationCode: "",
        },
      },
    }),
    GitHubProvider({
      clientId: process.env.GITHUB_CLIENT_ID || "",
      clientSecret: process.env.GITHUB_CLIENT_SECRET || "",
    }),
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials, req) {
        try {
          console.log("Authorizing credentials:", credentials);

          const answer = await login(
            (credentials as any).email,
            (credentials as any).password
          );
          const json: any = await answer.json();
          console.log("Login response:", json);

          setCookie("accessToken", json.access, { cookies });
          setCookie("refreshToken", json.refresh, { cookies });
          return {
            email: (credentials as any).email,
            accessToken: json.access,
            refreshToken: json.refresh,
          } as any;
        } catch (error) {
          console.error("Error errror:", error);

          return null;
        }
      },
    }),
  ],
  jwt: {
    secret: process.env.NEXTAUTH_SECRET,
  },
  callbacks: {
    async signIn({ user, account, profile }: any) {
      if (account.provider === "google") {
        const cookieStore = cookies();
        let invitationCode : any = cookieStore.get("invitationCode");
        invitationCode = invitationCode?.value;
        deleteCookie("invitationCode");
        try {
          const response = await loginOauth(account.provider, account.id_token, invitationCode);

          const data: any = await response.json();
          if (data.access && data.refresh) {
            setCookie("accessToken", data.access, { cookies });
            setCookie("refreshToken", data.refresh, { cookies });
            user.accessToken = data.access;
            user.refreshToken = data.refresh;

            return true;
          } else {
            return false;
          }
        } catch (error) {
          console.error("Error during OAuth authentication:", error);
          return false;
        }
      } else if (account.provider === "github") {
        try {
          const response = await loginOauth(
            account.provider,
            account.access_token
          );
          const data: any = await response.json();
          if (data.access && data.refresh) {
            setCookie("accessToken", data.access, { cookies });
            setCookie("refreshToken", data.refresh, { cookies });
            user.accessToken = data.access;
            user.refreshToken = data.refresh;
            return true;
          } else {
            return false;
          }
        } catch (error) {
          console.error("Error during OAuth authentication:", error);
          return false;
        }
      }
      return true;
    },
    async jwt({ token, user }) {
      if (user) {
        token.accessToken = (user as any).accessToken;
        token.refreshToken = (user as any).refreshToken;
      }
      return token;
    },
    async session({ session, token }) {
      (session.user as any).accessToken = token.accessToken;
      (session.user as any).refreshToken = token.refreshToken;
      return session;
    },
    async redirect({ url, baseUrl }) {
      return baseUrl;
    },
  },
});

export { handler as GET, handler as POST };

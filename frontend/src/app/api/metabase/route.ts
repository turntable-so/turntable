import jwt from "jsonwebtoken";
import { type NextRequest, NextResponse } from "next/server";

const METABASE_SITE_URL = "https://turntable.metabaseapp.com";
const METABASE_JWT_SHARED_SECRET =
  "7fb93725616f077a6f17a3946e8f82f35e4cb0717d6c4eee971083d607736075";

const signUserToken = (user: any) => {
  return jwt.sign(
    {
      email: user.email,
      first_name: user.firstName,
      last_name: user.lastName,
      exp: Math.round(Date.now() / 1000) + 60 * 10,
    },
    METABASE_JWT_SHARED_SECRET,
  );
};

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const returnTo = searchParams.get("return_to") || "/";

  // Replace with actual user data retrieval logic
  const user = {
    email: "accounts@turntable.so",
    firstName: "Accounts",
    lastName: "Turntable",
  };

  const token = signUserToken(user);

  const ssoUrl = new URL("/auth/sso", METABASE_SITE_URL);
  ssoUrl.searchParams.set("token", "true");
  ssoUrl.searchParams.set("jwt", token);

  console.log({ ssoUrl: ssoUrl.toString(), returnTo });

  try {
    const response = await fetch(ssoUrl.toString());
    const data = await response.json();

    console.log("Received token", data);
    return NextResponse.json(data);
  } catch (error: any) {
    console.error("Authentication failed", error);
    return NextResponse.json(
      {
        status: "error",
        message: "Authentication failed",
        error: error.message,
      },
      { status: 401 },
    );
  }
}

import { NextResponse } from 'next/server';
import jwt from 'jsonwebtoken';

const METABASE_SITE_URL = 'https://turntable.metabaseapp.com';
const METABASE_JWT_SHARED_SECRET = '7fb93725616f077a6f17a3946e8f82f35e4cb0717d6c4eee971083d607736075';

const signUserToken = (user: any) => {
    return jwt.sign(
        {
            email: user.email,
            first_name: user.firstName,
            last_name: user.lastName,
            exp: Math.round(Date.now() / 1000) + 60 * 10,
        },
        METABASE_JWT_SHARED_SECRET
    );
};

export async function GET(request: Request) {
    const { searchParams } = new URL(request.url);
    const returnTo = searchParams.get('return_to') || '/';

    const user = { email: 'accounts@turntable.so', firstName: 'Accounts', lastName: 'Turntable' };

    const ssoUrl = new URL('/auth/sso', METABASE_SITE_URL);
    ssoUrl.searchParams.set('jwt', signUserToken(user));
    ssoUrl.searchParams.set(
      "return_to",
      `${returnTo ?? "/"}?logo=false&top_nav=false`,
    );

    console.log({ ssoUrl: ssoUrl.toString(), returnTo })

    return NextResponse.redirect(ssoUrl.toString());
}

import { NextResponse } from 'next/server';
import jwt from 'jsonwebtoken';
import { v4 as uuidv4 } from 'uuid';

const TABLEAU_CONNECTED_APP_CLIENT_ID = process.env.TABLEAU_CONNECTED_APP_CLIENT_ID!;
const TABLEAU_CONNECTED_APP_SECRET_KEY = process.env.TABLEAU_CONNECTED_APP_SECRET_KEY!;
const TABLEAU_CONNECTED_APP_SECRET_ID = process.env.TABLEAU_CONNECTED_APP_SECRET_ID!;

export async function GET(request: Request) {
    const user = 'accounts@turntable.so';

    const payload = {
        iss: TABLEAU_CONNECTED_APP_CLIENT_ID,
        exp: Math.floor(Date.now() / 1000) + (10 * 60),
        jti: uuidv4(),
        aud: 'tableau',
        sub: user,
        scp: ['tableau:views:embed', 'tableau:metrics:embed'],
    };

    const headers = {
        kid: TABLEAU_CONNECTED_APP_SECRET_ID,
        iss: TABLEAU_CONNECTED_APP_CLIENT_ID
    };

    const token = jwt.sign(payload, TABLEAU_CONNECTED_APP_SECRET_KEY, {
        algorithm: 'HS256',
        header: headers
    });

    return NextResponse.json({ token });
}

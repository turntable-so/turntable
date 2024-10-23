import jwt from 'jsonwebtoken';
import { NextResponse } from 'next/server';

export async function GET(request: Request) {
    const { searchParams } = new URL(request.url)
    const questionId = Number(searchParams.get('questionId'))
    const params = null

    const METABASE_SITE_URL = 'http://localhost:4000';
    const METABASE_EMBEDDING_KEY = '373df5d1699f50fe2fc4677c30cae799ad997fb4848ba179a4ff3df8f066e112';


    // // Ensure the embedding key and site URL are set
    if (!METABASE_SITE_URL || !METABASE_EMBEDDING_KEY) {
        return NextResponse.json({ error: 'Metabase configuration is missing.' });
    }

    // make embeddable
    /* This code snippet is making a PUT request to the Metabase API in order to make a specific question
    embeddable. */
    try {

        const makeEmbeddable = await fetch(`http://metabase:4000/api/dashboard/${questionId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                "X-API-KEY": 'mb_pqo6+Ypcd1roXBTHmkv7zP4wK19V2LEKNTCpBOudrH4=',

            },
            body: JSON.stringify({ enable_embedding: true }),
        });
        console.log({ makeEmbeddable: makeEmbeddable.status })
    } catch (error) {
        console.error('Error making question embeddable:', error);
    }


    // // Construct the payload
    const payload = {
        resource: { dashboard: questionId },
        params: params ? JSON.parse(params) : {},
        exp: Math.floor(Date.now() / 1000) + 60 * 10, // Token valid for 10 minutes
    };

    // // Generate the JWT token
    const token = jwt.sign(payload, METABASE_EMBEDDING_KEY);

    // // Construct the iframe URL
    const iframeUrl = METABASE_SITE_URL + "/embed/dashboard/" + token +
        "#theme=transparent&bordered=false&titled=false";

    // Return the iframe URL
    return NextResponse.json({ iframeUrl });

}

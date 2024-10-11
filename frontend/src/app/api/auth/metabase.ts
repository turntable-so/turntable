// pages/api/metabase.js

import jwt from 'jsonwebtoken';

export default function handler(req, res) {
    const { questionId, params } = req.query;

    const METABASE_SITE_URL = 'http://localhost:4000';
    const METABASE_EMBEDDING_KEY = 'a1ed35e2bec9192530c1bd26c3b0248cae3c8acfb0ed54eeb30d816eedac1f42';

    // Ensure the embedding key and site URL are set
    if (!METABASE_SITE_URL || !METABASE_EMBEDDING_KEY) {
        return res.status(500).json({ error: 'Metabase configuration is missing.' });
    }

    // Construct the payload
    const payload = {
        resource: { question: Number(questionId) },
        params: params ? JSON.parse(params) : {},
        exp: Math.floor(Date.now() / 1000) + 60 * 10, // Token valid for 10 minutes
    };

    // Generate the JWT token
    const token = jwt.sign(payload, METABASE_EMBEDDING_KEY);

    // Construct the iframe URL
    const iframeUrl = `${METABASE_SITE_URL}/embed/question/${token}#bordered=true&titled=true`;

    // Return the iframe URL
    res.status(200).json({ iframeUrl });
}

import { NextResponse } from 'next/server';

export async function GET(request: Request) {
    const METABASE_DASHBOARD_PATH = "/dashboard/11";
    const iframeUrl = `/api/metabase/sso?return_to=${METABASE_DASHBOARD_PATH}`;
    
    const iframeContent = `<iframe src="${iframeUrl}" frameborder="0" width="1280" height="600" allowtransparency></iframe>`;

    console.log({ iframeContent })

    return new NextResponse("Hello World", {
        headers: {
            'Content-Type': 'text/plain',
        },
    });
    
    // return new NextResponse(iframeContent, {
    //     headers: {
    //         'Content-Type': 'text/html',
    //     },
    // });
}

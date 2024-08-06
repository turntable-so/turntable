// 'use client';

// import { useUser } from '@clerk/nextjs';
// import posthog from 'posthog-js';
// import { PostHogProvider } from 'posthog-js/react';
// import { useEffect } from 'react';

// if (typeof window !== 'undefined') {
//     posthog.init('phc_XL4KyheAjc4gJV4Fzpg1lbn7goFP1QNqsnNUhY1O1CU', {
//         api_host: 'https://us.i.posthog.com',
//         capture_pageview: true // Disable automatic pageview capture, as we capture manually
//     })
// }

// const PHProvider = ({ children }: { children: React.ReactNode }) => {
//     useEffect(() => {
//         if (user) {

//             posthog.identify(user?.id,
//                 {
//                     name: user?.fullName,
//                     email: user?.primaryEmailAddress?.emailAddress,
//                 })
//         }

//     }, [user])

//     return <PostHogProvider client={posthog}>{children}</PostHogProvider>;
// };

// export default PHProvider;
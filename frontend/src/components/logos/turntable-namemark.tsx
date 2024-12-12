import React from "react";
import dynamic from "next/dynamic";

const ClientNameMark = dynamic(
  () => import("./client-turntable-namemark"),
  {
    ssr: false,
    loading: () => null // Prevent flash while loading
  }
);

// Export the client-side component directly
export default ClientNameMark;

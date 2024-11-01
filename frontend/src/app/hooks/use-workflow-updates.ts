"use client";
import getUrl from "@/app/url";
import { AuthActions } from "@/lib/auth";
import { useEffect, useRef, useState } from "react";
import jwt_decode from "jwt-decode"; // Import jwt-decode

const baseUrl = getUrl();
const protocol = process.env.NODE_ENV === "development" ? "ws" : "wss";

const useWorkflowUpdates = (workspaceId: string) => {
  const [workflowStatus, setWorkflowStatus] = useState<string | null>(null);
  const [resource, setResource] = useState<any>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const heartbeatInterval = useRef<number | null>(null);
  const reconnectTimeout = useRef<number | null>(null);
  const retryDelay = useRef<number>(2000); // Start with 2 seconds delay
  const { getToken, handleJWTRefresh, storeToken, removeTokens, isTokenExpired } = AuthActions();

  const connectWebSocket = async () => {
    let accessToken = getToken("access");

    if (!accessToken || isTokenExpired(accessToken)) {
      try {
        // Refresh the token
        const refreshResponse = await handleJWTRefresh();
        const refreshData: any = await refreshResponse.json();
        if (refreshData.access) {
          accessToken = refreshData.access;
          storeToken(accessToken as string, "access");
        } else {
          removeTokens();
          return;
        }
      } catch (err) {
        removeTokens();
        return;
      }
    }

    // Construct the WebSocket URL with the (possibly refreshed) token
    const base = new URL(baseUrl).host;
    const socketUrl = `${protocol}://${base}/ws/subscribe/${workspaceId}/?token=${accessToken}`;

    const socket = new WebSocket(socketUrl);
    socketRef.current = socket;

    // Send a "ping" message every 30 seconds to keep the connection alive
    const sendHeartbeat = () => {
      if (
        socketRef.current &&
        socketRef.current.readyState === WebSocket.OPEN
      ) {
        socketRef.current.send(JSON.stringify({ type: "ping" }));
      }
    };

    socket.onopen = () => {
      retryDelay.current = 2000; // Reset retry delay on successful connection
      // Start the heartbeat interval
      heartbeatInterval.current = window.setInterval(sendHeartbeat, 30000); // Ping every 30 seconds
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "pong") {
        console.log("Received pong");
      } else {
        setWorkflowStatus(data.status);
        setResource(data.resource_id);
      }
    };

    socket.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    socket.onclose = async (event) => {
      if (heartbeatInterval.current) {
        clearInterval(heartbeatInterval.current);
      }

      // If the close was due to authentication (e.g., token expired)
      if (event.code === 4401 || event.code === 4001) { // Custom codes for authentication errors
        // Attempt to refresh the token and reconnect
        try {
          const refreshResponse = await handleJWTRefresh();
          const refreshData = await refreshResponse.json();
          if (refreshResponse.ok && refreshData.access) {
            accessToken = refreshData.access;
            storeToken(accessToken, "access");
            retryDelay.current = 2000; // Reset retry delay
            connectWebSocket(); // Reconnect with new token
            return;
          } else {
            // Token refresh failed
            removeTokens();
            if (typeof window !== "undefined") {
              window.location.replace("/");
            }
            return;
          }
        } catch (err) {
          // Handle errors during token refresh
          removeTokens();
          if (typeof window !== "undefined") {
            window.location.replace("/");
          }
          return;
        }
      }

      // RECONNECT with exponential backoff
      if (!reconnectTimeout.current) {
        reconnectTimeout.current = window.setTimeout(() => {
          retryDelay.current = Math.min(retryDelay.current * 2, 30000); // Cap delay at 30 seconds
          connectWebSocket(); // Try reconnecting
          reconnectTimeout.current = null; // Reset timeout
        }, retryDelay.current);
      }
    };
  };

  useEffect(() => {
    connectWebSocket();

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
      if (heartbeatInterval.current) {
        clearInterval(heartbeatInterval.current);
      }
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
    };
  }, [workspaceId]);

  return [workflowStatus, resource];
};

export default useWorkflowUpdates;

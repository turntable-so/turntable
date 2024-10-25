"use client";
import getUrl from "@/app/url";
import { AuthActions } from "@/lib/auth";
import { useEffect, useRef, useState } from "react";

const baseUrl = getUrl();
const protocol = process.env.NODE_ENV === "development" ? "ws" : "wss";

const useWorkflowUpdates = (workspaceId: string) => {
  const [workflowStatus, setWorkflowStatus] = useState<string | null>(null);
  const [resource, setResource] = useState<any>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const heartbeatInterval = useRef<number | null>(null);
  const reconnectTimeout = useRef<number | null>(null);
  const retryDelay = useRef<number>(2000); // Start with 2 seconds delay
  const { getToken } = AuthActions();
  const accessToken = getToken("access");

  const connectWebSocket = () => {
    // Construct the WebSocket URL
    const base = new URL(baseUrl).host;
    const socketUrl = `${protocol}://${base}/ws/subscribe/${workspaceId}/?token=${accessToken}`;
    console.log(`Attempting to connect to ${socketUrl}`);

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
      console.log(`WebSocket connection established: ${socketUrl}`);
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
        console.log(
          `Workflow Run ${data.workflow_run_id} status updated: ${data.status}`,
        );
      }
    };

    socket.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    socket.onclose = () => {
      console.log("WebSocket connection closed.");
      if (heartbeatInterval.current) {
        clearInterval(heartbeatInterval.current);
      }

      // RECONNECT with exponential backoff
      if (!reconnectTimeout.current) {
        console.log(`Reconnecting in ${retryDelay.current / 1000} seconds...`);
        reconnectTimeout.current = window.setTimeout(() => {
          console.log("Reconnecting...");
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

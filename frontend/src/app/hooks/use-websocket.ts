import { useCallback, useEffect, useRef, useState } from "react";

interface UseWebSocketOptions {
  onOpen?: (event: Event) => void;
  onMessage?: (event: MessageEvent) => void;
  onError?: (event: Event) => void;
  onClose?: (event: CloseEvent) => void;
  /**
   * Timeout in milliseconds after which the WebSocket connection will be closed if no events are received.
   */
  timeout?: number;
}

export function useWebSocket(url: string, options?: UseWebSocketOptions) {
  const ws = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const timeoutIdRef = useRef<number | null>(null);

  const startWebSocket = useCallback(() => {
    if (ws.current) {
      console.warn("WebSocket is already connected.");
      return;
    }

    console.log('Attempting to connect WebSocket...');
    ws.current = new WebSocket(url);

    ws.current.onopen = (event) => {
      console.log('WebSocket opened successfully');
      setIsConnected(true);
      options?.onOpen?.(event);

      if (options?.timeout) {
        if (timeoutIdRef.current) {
          clearTimeout(timeoutIdRef.current);
        }
        timeoutIdRef.current = window.setTimeout(() => {
          console.warn(
            "WebSocket timeout: No events received within the specified time.",
          );
          ws.current?.close();
        }, options.timeout);
      }
    };

    ws.current.onmessage = (event) => {
      console.log('WebSocket message received:', event.data);
      options?.onMessage?.(event);

      if (options?.timeout) {
        if (timeoutIdRef.current) {
          clearTimeout(timeoutIdRef.current);
        }
        timeoutIdRef.current = window.setTimeout(() => {
          console.warn(
            "WebSocket timeout: No events received within the specified time.",
          );
          ws.current?.close();
        }, options.timeout);
      }
    };

    ws.current.onerror = (event) => {
      options?.onError?.(event);

      if (timeoutIdRef.current) {
        clearTimeout(timeoutIdRef.current);
        timeoutIdRef.current = null;
      }
    };

    ws.current.onclose = (event) => {
      console.log(`WebSocket closed with code: ${event.code}, reason: ${event.reason}`);
      setIsConnected(false);
      ws.current = null;
      options?.onClose?.(event);

      if (timeoutIdRef.current) {
        clearTimeout(timeoutIdRef.current);
        timeoutIdRef.current = null;
      }
    };
  }, [url, options]);

  const stopWebSocket = useCallback(() => {
    if (ws.current) {
      ws.current.close();
      ws.current = null;
    }

    if (timeoutIdRef.current) {
      clearTimeout(timeoutIdRef.current);
      timeoutIdRef.current = null;
    }
  }, []);

  const sendMessage = useCallback(
    (message: string | ArrayBuffer | Blob | ArrayBufferView) => {
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
        ws.current.send(message);
      } else {
        console.warn("WebSocket is not open.");
      }
    },
    [],
  );

  useEffect(() => {
    return () => {
      if (ws.current) {
        ws.current.close();
      }

      if (timeoutIdRef.current) {
        clearTimeout(timeoutIdRef.current);
        timeoutIdRef.current = null;
      }
    };
  }, []);

  return { startWebSocket, stopWebSocket, sendMessage, isConnected };
}

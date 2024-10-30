import { useCallback, useEffect, useRef, useState } from "react";

type UseWebSocketOptions<P = undefined> = P extends undefined
  ? {
      onOpen?: (data: { event: Event }) => void;
      onMessage?: (data: { event: MessageEvent }) => void;
      onError?: (data: { event: Event }) => void;
      onClose?: (data: { event: CloseEvent }) => void;
    }
  : {
      onOpen?: (data: { event: Event; payload: P }) => void;
      onMessage?: (data: { event: MessageEvent; payload: P }) => void;
      onError?: (data: { event: Event; payload: P }) => void;
      onClose?: (data: { event: CloseEvent; payload: P }) => void;
    };

export function useWebSocket<P = undefined>(
  url: string,
  options?: UseWebSocketOptions<P>,
) {
  const ws = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const payloadRef = useRef<P | undefined>(undefined);

  const startWebSocket = useCallback(
    (payload: P extends undefined ? void : P) => {
      if (ws.current) {
        console.warn("WebSocket is already connected.");
        return;
      }

      payloadRef.current = payload as P;

      ws.current = new WebSocket(url);

      ws.current.onopen = (event) => {
        setIsConnected(true);
        if (options?.onOpen) {
          if (payloadRef.current !== undefined) {
            // When P is defined
            (options.onOpen as (data: { event: Event; payload: P }) => void)({
              event,
              payload: payloadRef.current,
            });
          } else {
            // When P is undefined
            (options.onOpen as (data: { event: Event }) => void)({ event });
          }
        }
      };

      ws.current.onmessage = (event) => {
        if (options?.onMessage) {
          if (payloadRef.current !== undefined) {
            // When P is defined
            (
              options.onMessage as (data: {
                event: MessageEvent;
                payload: P;
              }) => void
            )({
              event,
              payload: payloadRef.current,
            });
          } else {
            // When P is undefined
            (options.onMessage as (data: { event: MessageEvent }) => void)({
              event,
            });
          }
        }
      };

      ws.current.onerror = (event) => {
        if (options?.onError) {
          if (payloadRef.current !== undefined) {
            // When P is defined
            (options.onError as (data: { event: Event; payload: P }) => void)({
              event,
              payload: payloadRef.current,
            });
          } else {
            // When P is undefined
            (options.onError as (data: { event: Event }) => void)({ event });
          }
        }
      };

      ws.current.onclose = (event) => {
        setIsConnected(false);
        ws.current = null;

        if (options?.onClose) {
          if (payloadRef.current !== undefined) {
            // When P is defined
            (options.onClose as (data: { event: Event; payload: P }) => void)({
              event,
              payload: payloadRef.current,
            });
          } else {
            // When P is undefined
            (options.onClose as (data: { event: Event }) => void)({ event });
          }
        }
      };
    },
    [url, options],
  );

  const stopWebSocket = useCallback(() => {
    if (ws.current) {
      ws.current.close();
      ws.current = null;
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
    };
  }, []);

  return {
    startWebSocket,
    stopWebSocket,
    sendMessage,
    isConnected,
  };
}

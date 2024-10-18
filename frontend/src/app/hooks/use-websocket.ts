import { useState, useEffect, useRef, useCallback } from 'react';

interface UseWebSocketOptions {
  onOpen?: (event: Event) => void;
  onMessage?: (event: MessageEvent) => void;
  onError?: (event: Event) => void;
  onClose?: (event: CloseEvent) => void;
}

export function useWebSocket(url: string, options?: UseWebSocketOptions) {
  const ws = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState<boolean>(false);

  const startWebSocket = useCallback(() => {
    if (ws.current) {
      console.warn('WebSocket is already connected.');
      return;
    }

    ws.current = new WebSocket(url);

    ws.current.onopen = (event) => {
      setIsConnected(true);
      options?.onOpen?.(event);
    };

    ws.current.onmessage = (event) => {
      options?.onMessage?.(event);
    };

    ws.current.onerror = (event) => {
      options?.onError?.(event);
    };

    ws.current.onclose = (event) => {
      setIsConnected(false);
      ws.current = null;
      options?.onClose?.(event);
    };
  }, [url, options]);

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
        console.warn('WebSocket is not open.');
      }
    },
    []
  );

  useEffect(() => {
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, []);

  return { startWebSocket, stopWebSocket, sendMessage, isConnected };
}

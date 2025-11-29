import { useEffect, useCallback, useState } from 'react';
import { wsService } from '@/services/websocket';
import type { WebSocketMessage } from '@/types/flood.types';

export function useWebSocket() {
  const [connected, setConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);

  useEffect(() => {
    wsService
      .connect()
      .then(() => setConnected(true))
      .catch((error) => {
        console.error('WebSocket connection failed:', error);
        setConnected(false);
      });

    wsService.on('all', (message: WebSocketMessage) => {
      setLastMessage(message);
    });

    return () => {
      wsService.disconnect();
    };
  }, []);


  const subscribe = useCallback((resource: string) => {
    wsService.subscribe(resource);
  }, []);

  const onMessage = useCallback((type: string, callback: (data: any) => void) => {
    wsService.on(type, callback);
    return () => wsService.off(type, callback);
  }, []);

  return { connected, lastMessage, subscribe, onMessage };
}

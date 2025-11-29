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

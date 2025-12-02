// Runtime configuration loaded from window object
export interface RuntimeConfig {
  API_BASE_URL: string;
  WS_URL: string;
}

declare global {
  interface Window {
    __RUNTIME_CONFIG__?: RuntimeConfig;
  }
}

// Get runtime config with fallbacks
export const getRuntimeConfig = (): RuntimeConfig => {
  // Determine WebSocket protocol based on page protocol
  const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const defaultWsUrl = `${wsProtocol}//${window.location.host}/ws`;

  return {
    API_BASE_URL: window.__RUNTIME_CONFIG__?.API_BASE_URL || "/api",
    WS_URL: window.__RUNTIME_CONFIG__?.WS_URL || defaultWsUrl,
  };
};

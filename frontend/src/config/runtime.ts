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
  return {
    API_BASE_URL: window.__RUNTIME_CONFIG__?.API_BASE_URL || "/api",
    WS_URL:
      window.__RUNTIME_CONFIG__?.WS_URL || `ws://${window.location.host}/ws`,
  };
};

/**
 * Application-wide constants
 */

// API Configuration
export const API_CONFIG = {
  TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000, // 1 second
} as const;

// Map Configuration
export const MAP_CONFIG = {
  DEFAULT_CENTER: [38.9072, -77.0369] as [number, number], // Washington DC
  DEFAULT_ZOOM: 8,
  MIN_ZOOM: 3,
  MAX_ZOOM: 18,
  TILE_LAYER_URL: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
  TILE_LAYER_ATTRIBUTION:
    '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
} as const;

// Gauge Stages
export const GAUGE_STAGES = {
  NORMAL: 'normal',
  ACTION: 'action',
  FLOOD: 'flood',
  MAJOR: 'major',
} as const;

export const GAUGE_STAGE_COLORS = {
  normal: '#16A34A', // Green
  action: '#CA8A04', // Yellow
  flood: '#EA580C', // Orange
  major: '#DC2626', // Red
} as const;

// Risk Levels
export const RISK_LEVELS = {
  LOW: 'low',
  MODERATE: 'moderate',
  HIGH: 'high',
  SEVERE: 'severe',
} as const;

export const RISK_LEVEL_COLORS = {
  low: '#16A34A', // Green
  moderate: '#CA8A04', // Yellow
  high: '#EA580C', // Orange
  severe: '#DC2626', // Red
} as const;

export const RISK_LEVEL_RANGES = {
  low: [0, 25],
  moderate: [25, 50],
  high: [50, 75],
  severe: [75, 100],
} as const;

// Data Refresh Intervals
export const REFRESH_INTERVALS = {
  GAUGES: 300000, // 5 minutes
  PREDICTIONS: 600000, // 10 minutes
  WEATHER: 900000, // 15 minutes
  WEBSOCKET_PING: 30000, // 30 seconds
} as const;

// Local Storage Keys
export const STORAGE_KEYS = {
  MAP_CENTER: 'flood_app_map_center',
  MAP_ZOOM: 'flood_app_map_zoom',
  SELECTED_GAUGE: 'flood_app_selected_gauge',
  THEME: 'flood_app_theme',
  USER_PREFERENCES: 'flood_app_preferences',
} as const;

// Units
export const UNITS = {
  FLOW: 'cfs', // Cubic feet per second
  HEIGHT: 'ft', // Feet
  PRECIPITATION: 'in', // Inches
  TEMPERATURE: '°F', // Fahrenheit
  AREA: 'sq mi', // Square miles
} as const;

// Thresholds
export const THRESHOLDS = {
  HIGH_FLOW: 10000, // CFS
  HIGH_PRECIPITATION: 2.0, // Inches per hour
  LOW_CONFIDENCE: 0.5, // 50%
  STALE_DATA_HOURS: 24, // Hours
} as const;

// Error Messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Unable to connect to the server. Please check your internet connection.',
  TIMEOUT_ERROR: 'Request timed out. Please try again.',
  SERVER_ERROR: 'Server error occurred. Please try again later.',
  NOT_FOUND: 'Requested resource not found.',
  VALIDATION_ERROR: 'Invalid data received from server.',
  WEBSOCKET_ERROR: 'Real-time connection lost. Attempting to reconnect...',
  UNKNOWN_ERROR: 'An unexpected error occurred. Please try again.',
} as const;

// Success Messages
export const SUCCESS_MESSAGES = {
  DATA_REFRESHED: 'Data refreshed successfully',
  SETTINGS_SAVED: 'Settings saved successfully',
  CONNECTION_ESTABLISHED: 'Real-time connection established',
} as const;

// Date Formats
export const DATE_FORMATS = {
  FULL: 'PPpp', // Dec 2, 2024, 3:45 PM
  DATE_ONLY: 'PP', // Dec 2, 2024
  TIME_ONLY: 'p', // 3:45 PM
  SHORT: 'MM/dd/yyyy', // 12/02/2024
  ISO: "yyyy-MM-dd'T'HH:mm:ss", // 2024-12-02T15:45:00
} as const;

// WebSocket Events
export const WS_EVENTS = {
  CONNECTION: 'connection',
  GAUGE_UPDATE: 'gauge_update',
  RISK_ALERT: 'risk_alert',
  PREDICTION_UPDATE: 'prediction_update',
  ERROR: 'error',
  PING: 'ping',
  PONG: 'pong',
} as const;

// Feature Flags
export const FEATURES = {
  HEATMAP: true,
  WEBSOCKET: true,
  PRECIPITATION_OVERLAY: true,
  HISTORICAL_DATA: true,
  EXPORT_DATA: false, // Not implemented yet
  NOTIFICATIONS: false, // Not implemented yet
} as const;

// Pagination
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  PAGE_SIZE_OPTIONS: [10, 20, 50, 100],
} as const;

// Chart Colors
export const CHART_COLORS = {
  PRIMARY: '#3B82F6', // Blue
  SECONDARY: '#8B5CF6', // Purple
  SUCCESS: '#10B981', // Green
  WARNING: '#F59E0B', // Amber
  DANGER: '#EF4444', // Red
  INFO: '#06B6D4', // Cyan
} as const;

// Animation Durations
export const ANIMATION = {
  FAST: 150,
  NORMAL: 300,
  SLOW: 500,
} as const;

// Breakpoints (matches Tailwind)
export const BREAKPOINTS = {
  SM: 640,
  MD: 768,
  LG: 1024,
  XL: 1280,
  '2XL': 1536,
} as const;

// Application Metadata
export const APP_INFO = {
  NAME: 'Urban Flood Prediction System',
  VERSION: '1.0.0',
  DESCRIPTION: 'Real-time flood monitoring and prediction system',
  AUTHOR: 'Flood Prediction Team',
  REPOSITORY: 'https://github.com/yourusername/flood-prediction-system',
} as const;
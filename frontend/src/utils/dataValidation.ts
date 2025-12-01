import type { GaugeData, FloodPrediction } from '@/types/flood.types';

export class ValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

export function validateGaugeData(data: any): data is GaugeData {
  if (!data || typeof data !== 'object') {
    throw new ValidationError('Gauge data must be an object');
  }

  if (typeof data.id !== 'number') {
    throw new ValidationError('Gauge id must be a number');
  }

  if (typeof data.usgs_site_id !== 'string') {
    throw new ValidationError('USGS site ID must be a string');
  }

  if (typeof data.name !== 'string') {
    throw new ValidationError('Gauge name must be a string');
  }

  if (typeof data.latitude !== 'number' || data.latitude < -90 || data.latitude > 90) {
    throw new ValidationError('Latitude must be a number between -90 and 90');
  }

  if (typeof data.longitude !== 'number' || data.longitude < -180 || data.longitude > 180) {
    throw new ValidationError('Longitude must be a number between -180 and 180');
  }

  if (typeof data.last_updated !== 'string') {
    throw new ValidationError('Last updated must be a string (ISO date)');
  }

  return true;
}

export function validatePrediction(data: any): data is FloodPrediction {
  if (!data || typeof data !== 'object') {
    throw new ValidationError('Prediction data must be an object');
  }

  if (typeof data.id !== 'number') {
    throw new ValidationError('Prediction id must be a number');
  }

  if (!['low', 'moderate', 'high', 'severe'].includes(data.risk_level)) {
    throw new ValidationError('Risk level must be low, moderate, high, or severe');
  }

  if (typeof data.risk_score !== 'number' || data.risk_score < 0 || data.risk_score > 100) {
    throw new ValidationError('Risk score must be a number between 0 and 100');
  }

  return true;
}

export function validateCoordinates(lat: number, lon: number): boolean {
  return (
    typeof lat === 'number' &&
    typeof lon === 'number' &&
    lat >= -90 &&
    lat <= 90 &&
    lon >= -180 &&
    lon <= 180
  );
}

export function sanitizeString(str: string): string {
  return str.replace(/[<>]/g, '').trim();
}

export function validateEnvironmentVariables(): void {
  const required = ['VITE_API_BASE_URL', 'VITE_WS_URL'];
  
  const missing = required.filter((key) => !import.meta.env[key]);
  
  if (missing.length > 0) {
    throw new ValidationError(
      `Missing required environment variables: ${missing.join(', ')}`
    );
  }
}

export function isValidDate(dateString: string): boolean {
  const date = new Date(dateString);
  return !isNaN(date.getTime());
}

export function validateNumberInRange(
  value: number,
  min: number,
  max: number,
  fieldName: string
): void {
  if (typeof value !== 'number' || isNaN(value)) {
    throw new ValidationError(`${fieldName} must be a valid number`);
  }
  if (value < min || value > max) {
    throw new ValidationError(`${fieldName} must be between ${min} and ${max}`);
  }
}

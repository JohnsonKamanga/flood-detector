import { formatDistanceToNow, format, parseISO } from 'date-fns';

/**
 * Format a number with commas for thousands
 */
export function formatNumber(num: number, decimals: number = 0): string {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(num);
}

/**
 * Format flow rate in cubic feet per second
 */
export function formatFlowRate(cfs: number | null): string {
  if (cfs === null || cfs === undefined) return 'N/A';
  
  if (cfs >= 1000) {
    return `${formatNumber(cfs / 1000, 2)}k cfs`;
  }
  
  return `${formatNumber(cfs, 0)} cfs`;
}

/**
 * Format gauge height in feet
 */
export function formatGaugeHeight(feet: number | null): string {
  if (feet === null || feet === undefined) return 'N/A';
  return `${formatNumber(feet, 2)} ft`;
}

/**
 * Format precipitation in inches
 */
export function formatPrecipitation(inches: number | null): string {
  if (inches === null || inches === undefined) return 'N/A';
  return `${formatNumber(inches, 2)} in`;
}

/**
 * Format percentage
 */
export function formatPercentage(value: number | null): string {
  if (value === null || value === undefined) return 'N/A';
  return `${formatNumber(value, 1)}%`;
}

/**
 * Format date relative to now (e.g., "2 hours ago")
 */
export function formatRelativeTime(dateString: string): string {
  try {
    const date = typeof dateString === 'string' ? parseISO(dateString) : dateString;
    return formatDistanceToNow(date, { addSuffix: true });
  } catch (error) {
    console.error('Error formatting relative time:', error);
    return 'Unknown';
  }
}

/**
 * Format date as readable string
 */
export function formatDate(dateString: string, formatStr: string = 'PPpp'): string {
  try {
    const date = typeof dateString === 'string' ? parseISO(dateString) : dateString;
    return format(date, formatStr);
  } catch (error) {
    console.error('Error formatting date:', error);
    return 'Invalid date';
  }
}

/**
 * Format coordinates
 */
export function formatCoordinates(lat: number, lon: number): string {
  const latDir = lat >= 0 ? 'N' : 'S';
  const lonDir = lon >= 0 ? 'E' : 'W';
  
  return `${Math.abs(lat).toFixed(4)}°${latDir}, ${Math.abs(lon).toFixed(4)}°${lonDir}`;
}

/**
 * Format area in square miles
 */
export function formatArea(sqmi: number | null): string {
  if (sqmi === null || sqmi === undefined) return 'N/A';
  return `${formatNumber(sqmi, 0)} sq mi`;

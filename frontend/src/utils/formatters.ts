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
}

/**
 * Format risk score to visual representation
 */
export function formatRiskScore(score: number): {
  label: string;
  color: string;
  bgColor: string;
  textColor: string;
} {
  if (score >= 75) {
    return {
      label: 'Severe',
      color: '#DC2626',
      bgColor: 'bg-red-100',
      textColor: 'text-red-800',
    };
  } else if (score >= 50) {
    return {
      label: 'High',
      color: '#EA580C',
      bgColor: 'bg-orange-100',
      textColor: 'text-orange-800',
    };
  } else if (score >= 25) {
    return {
      label: 'Moderate',
      color: '#CA8A04',
      bgColor: 'bg-yellow-100',
      textColor: 'text-yellow-800',
    };
  } else {
    return {
      label: 'Low',
      color: '#16A34A',
      bgColor: 'bg-green-100',
      textColor: 'text-green-800',
    };
  }
}

/**
 * Format gauge stage to visual representation
 */
export function formatStage(stage: string | null): {
  label: string;
  color: string;
  bgColor: string;
} {
  switch (stage) {
    case 'major':
      return { label: 'Major Flood', color: '#DC2626', bgColor: 'bg-red-500' };
    case 'flood':
      return { label: 'Flood', color: '#EA580C', bgColor: 'bg-orange-500' };
    case 'action':
      return { label: 'Action', color: '#CA8A04', bgColor: 'bg-yellow-500' };
    case 'normal':
      return { label: 'Normal', color: '#16A34A', bgColor: 'bg-green-500' };
    default:
      return { label: 'Unknown', color: '#6B7280', bgColor: 'bg-gray-500' };
  }
}

/**
 * Truncate text with ellipsis
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength - 3) + '...';
}

/**
 * Format file size
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

/**
 * Format duration in milliseconds to readable string
 */
export function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  if (ms < 3600000) return `${(ms / 60000).toFixed(1)}m`;
  return `${(ms / 3600000).toFixed(1)}h`;
}

/**
 * Format confidence level
 */
export function formatConfidence(confidence: number | null): string {
  if (confidence === null || confidence === undefined) return 'N/A';
  return `${formatNumber(confidence * 100, 0)}%`;
}
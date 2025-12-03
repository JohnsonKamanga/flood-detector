import axios, { AxiosInstance, AxiosError } from 'axios';
import type { GaugeData, GaugeMeasurement, FloodPrediction, RiskZone, HeatmapData } from '@/types/flood.types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.client.interceptors.request.use(
      (config) => {
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }
  async getGauges(params?: {
    lat?: number;
    lon?: number;
    radius_km?: number;
    stage?: string;
  }): Promise<GaugeData[]> {
    const response = await this.client.get<GaugeData[]>('/gauges', { params });
    return response.data;
  }

  async getGauge(gaugeId: number): Promise<GaugeData> {
    const response = await this.client.get<GaugeData>(`/gauges/${gaugeId}`);
    return response.data;
  }

  async getGaugeMeasurements(gaugeId: number, hours: number = 24): Promise<GaugeMeasurement[]> {
    const response = await this.client.get<GaugeMeasurement[]>(
      `/gauges/${gaugeId}/measurements`,
      { params: { hours } }
    );
    return response.data;
  }

  async refreshGauge(usgs_site_id: string): Promise<any> {
    const response = await this.client.post(`/gauges/refresh/${usgs_site_id}`);
    return response.data;
  }
  async getGauges(params?: {
    lat?: number;
    lon?: number;
    radius_km?: number;
    stage?: string;
  }): Promise<GaugeData[]> {
    const response = await this.client.get<GaugeData[]>('/gauges', { params });
    return response.data;
  }

  async getGauge(gaugeId: number): Promise<GaugeData> {
    const response = await this.client.get<GaugeData>(`/gauges/${gaugeId}`);
    return response.data;
  }

  async getGaugeMeasurements(gaugeId: number, hours: number = 24): Promise<GaugeMeasurement[]> {
    const response = await this.client.get<GaugeMeasurement[]>(
      `/gauges/${gaugeId}/measurements`,
      { params: { hours } }
    );
    return response.data;
  }

  async refreshGauge(usgs_site_id: string): Promise<any> {
    const response = await this.client.post(`/gauges/refresh/${usgs_site_id}`);
    return response.data;
  } 
   async getPredictions(params?: {
    hours?: number;
    risk_level?: string;
  }): Promise<FloodPrediction[]> {
    const response = await this.client.get<FloodPrediction[]>('/predictions', { params });
    return response.data;
  }

  async getLatestPrediction(): Promise<FloodPrediction> {
    const response = await this.client.get<FloodPrediction>('/predictions/latest');
    return response.data;
  }

  async calculateRisk(data: {
    latitude: number;
    longitude: number;
    radius_km?: number;
  }): Promise<any> {
    const response = await this.client.post('/predictions/calculate', data);
    return response.data;
  }

  async getRiskZones(): Promise<RiskZone[]> {
    const response = await this.client.get<RiskZone[]>('/predictions/zones');
    return response.data;
  }

  async getRiskHeatmap(bbox: string, resolution: number = 50): Promise<HeatmapData> {
    const response = await this.client.get<HeatmapData>('/predictions/heatmap', {
      params: { bbox, resolution },
    });
    return response.data;
  }
  async healthCheck(): Promise<{ status: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService; 
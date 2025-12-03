import axios, { AxiosInstance, AxiosError } from "axios";
import type {
  GaugeData,
  GaugeMeasurement,
  FloodPrediction,
  RiskZone,
  HeatmapData,
} from "@/types/flood.types";
import { getRuntimeConfig } from "@/config/runtime";

const API_BASE_URL = getRuntimeConfig().API_BASE_URL;

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        console.error("API Error:", error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }
  // Gauge endpoints
  getGauges(params?: {
    lat?: number;
    lon?: number;
    radius_km?: number;
    stage?: string;
  }): Promise<GaugeData[]>;
  async getGauges(params?: {
    lat?: number;
    lon?: number;
    radius_km?: number;
    stage?: string;
  }): Promise<GaugeData[]> {
    const response = await this.client.get<GaugeData[]>("/gauges", { params });
    return response.data;
  }

  getGauge(gaugeId: number): Promise<GaugeData>;
  async getGauge(gaugeId: number): Promise<GaugeData> {
    const response = await this.client.get<GaugeData>(`/gauges/${gaugeId}`);
    return response.data;
  }

  getGaugeMeasurements(
    gaugeId: number,
    hours?: number
  ): Promise<GaugeMeasurement[]>;
  async getGaugeMeasurements(
    gaugeId: number,
    hours: number = 24
  ): Promise<GaugeMeasurement[]> {
    const response = await this.client.get<GaugeMeasurement[]>(
      `/gauges/${gaugeId}/measurements`,
      { params: { hours } }
    );
    return response.data;
  }

  refreshGauge(usgs_site_id: string): Promise<any>;
  async refreshGauge(usgs_site_id: string): Promise<any> {
    const response = await this.client.post(`/gauges/refresh/${usgs_site_id}`);
    return response.data;
  }

  // Prediction endpoints
  async getPredictions(params?: {
    hours?: number;
    risk_level?: string;
  }): Promise<FloodPrediction[]> {
    const response = await this.client.get<FloodPrediction[]>("/predictions", {
      params,
    });
    return response.data;
  }

  async getLatestPrediction(): Promise<FloodPrediction> {
    const response = await this.client.get<FloodPrediction>(
      "/predictions/latest"
    );
    return response.data;
  }

  async calculateRisk(data: {
    latitude: number;
    longitude: number;
    radius_km?: number;
  }): Promise<any> {
    const response = await this.client.post("/predictions/calculate", data);
    return response.data;
  }

  async getRiskZones(): Promise<RiskZone[]> {
    const response = await this.client.get<RiskZone[]>("/predictions/zones");
    return response.data;
  }

  async getRiskHeatmap(
    bbox: string,
    resolution: number = 50
  ): Promise<HeatmapData> {
    const response = await this.client.get<HeatmapData>(
      "/predictions/heatmap",
      {
        params: { bbox, resolution },
      }
    );
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    const response = await this.client.get("/health");
    return response.data;
  }

  // Historical flood endpoints
  async getHistoricalFloods(params?: {
    skip?: number;
    limit?: number;
    severity?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<any[]> {
    const response = await this.client.get("/historical", { params });
    return response.data;
  }

  async getHistoricalFloodById(floodId: number): Promise<any> {
    const response = await this.client.get(`/historical/${floodId}`);
    return response.data;
  }

  async getFloodStatistics(params?: {
    start_date?: string;
    end_date?: string;
  }): Promise<any> {
    const response = await this.client.get("/historical/statistics", {
      params,
    });
    return response.data;
  }

  async getFloodsByDecade(): Promise<any> {
    const response = await this.client.get("/historical/by-decade");
    return response.data;
  }

  async getNearbyHistoricalFloods(params: {
    lat: number;
    lon: number;
    radius_km?: number;
  }): Promise<any[]> {
    const response = await this.client.get("/historical/location/nearby", {
      params,
    });
    return response.data;
  }

  async getFloodsByGauge(gaugeId: number): Promise<any[]> {
    const response = await this.client.get(`/historical/gauge/${gaugeId}`);
    return response.data;
  }

  async getFloodImpacts(floodId: number): Promise<any[]> {
    const response = await this.client.get(`/historical/${floodId}/impacts`);
    return response.data;
  }

  async getRecurrenceIntervals(gaugeId: number): Promise<any[]> {
    const response = await this.client.get(
      `/historical/gauge/${gaugeId}/recurrence`
    );
    return response.data;
  }

  async calculateReturnPeriod(
    gaugeId: number,
    dischargeCfs: number
  ): Promise<any> {
    const response = await this.client.get(
      `/historical/gauge/${gaugeId}/return-period`,
      {
        params: { discharge_cfs: dischargeCfs },
      }
    );
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService;

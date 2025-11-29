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

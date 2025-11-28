
import React, { useState, useEffect } from 'react';
import FloodMap from '@/components/Map/FloodMap';
import AlertPanel from './AlertPanel';
import GaugeList from './GaugeList';
import RiskSummary from './RiskSummary';
import { useFloodData } from '@/hooks/useFloodData';
import { useWebSocket } from '@/hooks/useWebSocket';
import { apiService } from '@/services/api';
import type { GaugeData, HeatmapData } from '@/types/flood.types';
import LoadingSpinner from '@/components/shared/LoadingSpinner';
import ErrorMessage from '@/components/shared/ErrorMessage';


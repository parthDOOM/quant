import axios from 'axios';
import type { 
  HRPRequest, 
  HRPResponse, 
  CorrelationRequest, 
  CorrelationResponse,
  PairTestRequest,
  CointResult,
  FindPairsRequest,
  FindPairsResponse,
  SpreadAnalysisRequest,
  SpreadAnalysisResponse
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`, config.data);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status}`, response.data);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    
    if (error.response) {
      // Server responded with error status
      throw new Error(error.response.data?.detail || 'An error occurred');
    } else if (error.request) {
      // Request made but no response
      throw new Error('No response from server. Please check if the backend is running.');
    } else {
      // Error in request setup
      throw new Error(error.message);
    }
  }
);

export const hrpApi = {
  /**
   * Perform full HRP analysis
   */
  async analyzeHRP(request: HRPRequest): Promise<HRPResponse> {
    const response = await api.post<HRPResponse>('/hrp/analyze', request);
    return response.data;
  },

  /**
   * Calculate correlation matrix only
   */
  async getCorrelation(request: CorrelationRequest): Promise<CorrelationResponse> {
    const response = await api.post<CorrelationResponse>('/hrp/correlation', request);
    return response.data;
  },

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string; api: string }> {
    const response = await api.get('/health');
    return response.data;
  },
};

// Statistical Arbitrage API
export const statArbApi = {
  /**
   * Test a single pair for cointegration
   */
  async testPair(request: PairTestRequest): Promise<CointResult> {
    const response = await api.post<CointResult>('/stat-arb/test-pair', request);
    return response.data;
  },

  /**
   * Find all cointegrated pairs in a list of tickers
   */
  async findPairs(request: FindPairsRequest): Promise<FindPairsResponse> {
    const response = await api.post<FindPairsResponse>('/stat-arb/find-pairs', request);
    return response.data;
  },

  /**
   * Analyze spread with trading signals
   */
  async analyzeSpread(request: SpreadAnalysisRequest): Promise<SpreadAnalysisResponse> {
    const response = await api.post<SpreadAnalysisResponse>('/stat-arb/spread-analysis', request);
    return response.data;
  },
};

export default api;

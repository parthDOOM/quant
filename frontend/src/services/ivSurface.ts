import axios from 'axios';
import type { IVSurfaceResponse, ExpirationFilter } from '../types/ivSurface';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const ivSurfaceService = {
  /**
   * Check health status of IV Surface API
   */
  async checkHealth(): Promise<{ status: string; service: string; capabilities: string[] }> {
    const response = await axios.get(`${API_BASE_URL}/iv/health`);
    return response.data;
  },

  /**
   * Fetch IV surface data for a ticker
   */
  async fetchIVSurface(
    ticker: string,
    expirationFilter: ExpirationFilter = 'first',
    minVolume: number = 10
  ): Promise<IVSurfaceResponse> {
    const response = await axios.get(`${API_BASE_URL}/iv/surface/${ticker.toUpperCase()}`, {
      params: {
        expiration_filter: expirationFilter,
        min_volume: minVolume,
      },
    });
    return response.data;
  },
};

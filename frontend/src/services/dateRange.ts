import axios from 'axios';

export interface DateRangeRequest {
  tickers: string[];
}

export interface DateRangeResponse {
  min_date: string;
  max_date: string;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function fetchDateRange(tickers: string[]): Promise<DateRangeResponse> {
  const response = await axios.post<DateRangeResponse>(
    `${API_BASE_URL}/monte-carlo/date-range`,
    { tickers }
  );
  return response.data;
}

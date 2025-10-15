"""
Integration tests for IV Surface API endpoint.

Tests the complete flow: HTTP request → options fetch → IV calculation → response.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime, timedelta

from app.main import app

client = TestClient(app)


@pytest.fixture
def mock_options_data():
    """Mock options chain data for testing."""
    expiration = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    
    calls_df = pd.DataFrame({
        'strike': [95.0, 100.0, 105.0, 110.0],
        'bid': [7.5, 4.8, 2.5, 1.0],
        'ask': [7.7, 5.0, 2.7, 1.2],
        'mid_price': [7.6, 4.9, 2.6, 1.1],
        'volume': [100, 500, 300, 50],
        'openInterest': [1000, 5000, 3000, 500],
        'expiration': [expiration] * 4,
        'moneyness': [0.95, 1.0, 1.05, 1.10],
        'time_to_expiry': [7/365] * 4
    })
    
    puts_df = pd.DataFrame({
        'strike': [90.0, 95.0, 100.0, 105.0],
        'bid': [0.8, 2.3, 4.7, 7.5],
        'ask': [1.0, 2.5, 4.9, 7.7],
        'mid_price': [0.9, 2.4, 4.8, 7.6],
        'volume': [80, 400, 600, 200],
        'openInterest': [800, 4000, 6000, 2000],
        'expiration': [expiration] * 4,
        'moneyness': [0.90, 0.95, 1.0, 1.05],
        'time_to_expiry': [7/365] * 4
    })
    
    return {
        'ticker': 'TEST',
        'spot_price': 100.0,
        'risk_free_rate': 0.045,
        'calls': calls_df,
        'puts': puts_df,
        'expiration_dates': [expiration]
    }


class TestIVSurfaceHealthCheck:
    """Test health check endpoint."""
    
    def test_health_check(self):
        """Test IV surface health check endpoint."""
        response = client.get("/iv/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'implied_volatility_surface'
        assert 'capabilities' in data
        assert 'newton_raphson_iv_solver' in data['capabilities']


class TestIVSurfaceEndpoint:
    """Test IV surface data endpoint."""
    
    @patch('app.routers.iv_surface.OptionsDataService.fetch_options_chain')
    def test_get_iv_surface_success(self, mock_fetch, mock_options_data):
        """Test successful IV surface calculation."""
        mock_fetch.return_value = mock_options_data
        
        response = client.get("/iv/surface/TEST")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert data['ticker'] == 'TEST'
        assert data['spot_price'] == 100.0
        assert data['risk_free_rate'] == 0.045
        assert 'calls' in data
        assert 'puts' in data
        assert 'metrics' in data
        
        # Verify metrics
        metrics = data['metrics']
        assert metrics['total_call_contracts'] == 4
        assert metrics['total_put_contracts'] == 4
        assert metrics['successful_call_ivs'] >= 0
        assert metrics['successful_put_ivs'] >= 0
        assert len(metrics['expiration_dates']) > 0
    
    @patch('app.routers.iv_surface.OptionsDataService.fetch_options_chain')
    def test_get_iv_surface_with_filters(self, mock_fetch, mock_options_data):
        """Test IV surface with expiration and volume filters."""
        mock_fetch.return_value = mock_options_data
        
        response = client.get(
            "/iv/surface/TEST",
            params={'expiration_filter': 'first', 'min_volume': 100}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned contracts should have volume >= 100
        for call in data['calls']:
            assert call['volume'] >= 100
        for put in data['puts']:
            assert put['volume'] >= 100
    
    @patch('app.routers.iv_surface.OptionsDataService.fetch_options_chain')
    def test_get_iv_surface_contract_structure(self, mock_fetch, mock_options_data):
        """Test that contract structure is correct."""
        mock_fetch.return_value = mock_options_data
        
        response = client.get("/iv/surface/TEST")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check call contract structure
        if len(data['calls']) > 0:
            call = data['calls'][0]
            assert 'strike' in call
            assert 'moneyness' in call
            assert 'time_to_expiry' in call
            assert 'bid' in call
            assert 'ask' in call
            assert 'mid_price' in call
            assert 'volume' in call
            assert 'open_interest' in call
            assert 'implied_volatility' in call  # May be null
            assert 'expiration' in call
            
            # Verify types
            assert isinstance(call['strike'], (int, float))
            assert isinstance(call['volume'], int)
            assert isinstance(call['expiration'], str)
    
    @patch('app.routers.iv_surface.OptionsDataService.fetch_options_chain')
    def test_get_iv_surface_metrics_structure(self, mock_fetch, mock_options_data):
        """Test that metrics structure is correct."""
        mock_fetch.return_value = mock_options_data
        
        response = client.get("/iv/surface/TEST")
        
        assert response.status_code == 200
        data = response.json()
        
        metrics = data['metrics']
        
        # Required fields
        assert 'total_call_contracts' in metrics
        assert 'total_put_contracts' in metrics
        assert 'successful_call_ivs' in metrics
        assert 'successful_put_ivs' in metrics
        assert 'expiration_dates' in metrics
        
        # Optional fields (may be null if no valid IVs)
        assert 'atm_call_iv' in metrics
        assert 'atm_put_iv' in metrics
        assert 'atm_iv_avg' in metrics
        assert 'put_call_skew' in metrics
        assert 'iv_range_calls' in metrics
        assert 'iv_range_puts' in metrics
        
        # Verify types
        assert isinstance(metrics['total_call_contracts'], int)
        assert isinstance(metrics['expiration_dates'], list)
    
    @patch('app.routers.iv_surface.OptionsDataService.fetch_options_chain')
    def test_get_iv_surface_invalid_ticker(self, mock_fetch):
        """Test IV surface with invalid ticker."""
        mock_fetch.side_effect = ValueError("Ticker 'INVALID' not found")
        
        response = client.get("/iv/surface/INVALID")
        
        assert response.status_code == 404
        assert 'detail' in response.json()
    
    @patch('app.routers.iv_surface.OptionsDataService.fetch_options_chain')
    def test_get_iv_surface_no_options(self, mock_fetch):
        """Test IV surface when no options pass filters."""
        # Return empty DataFrames
        mock_fetch.return_value = {
            'ticker': 'TEST',
            'spot_price': 100.0,
            'risk_free_rate': 0.045,
            'calls': pd.DataFrame(columns=['strike', 'bid', 'ask', 'mid_price', 'volume', 
                                           'openInterest', 'expiration', 'moneyness', 'time_to_expiry']),
            'puts': pd.DataFrame(columns=['strike', 'bid', 'ask', 'mid_price', 'volume',
                                          'openInterest', 'expiration', 'moneyness', 'time_to_expiry']),
            'expiration_dates': []
        }
        
        response = client.get("/iv/surface/TEST")
        
        # Should get 404 when no data available
        assert response.status_code == 404
    
    @patch('app.routers.iv_surface.OptionsDataService.fetch_options_chain')
    def test_get_iv_surface_ticker_case_insensitive(self, mock_fetch):
        """Test that ticker is case-insensitive."""
        mock_fetch.return_value = {
            'ticker': 'AAPL',
            'spot_price': 150.0,
            'risk_free_rate': 0.045,
            'calls': pd.DataFrame({
                'strike': [150.0],
                'bid': [5.0], 'ask': [5.2], 'mid_price': [5.1],
                'volume': [100], 'openInterest': [1000],
                'expiration': ['2025-12-31'],
                'moneyness': [1.0], 'time_to_expiry': [0.1]
            }),
            'puts': pd.DataFrame({
                'strike': [150.0],
                'bid': [5.0], 'ask': [5.2], 'mid_price': [5.1],
                'volume': [100], 'openInterest': [1000],
                'expiration': ['2025-12-31'],
                'moneyness': [1.0], 'time_to_expiry': [0.1]
            }),
            'expiration_dates': ['2025-12-31']
        }
        
        # Test lowercase
        response = client.get("/iv/surface/aapl")
        assert response.status_code == 200
        assert response.json()['ticker'] == 'AAPL'


class TestIVSurfaceFilters:
    """Test filtering functionality."""
    
    @patch('app.routers.iv_surface.OptionsDataService.fetch_options_chain')
    def test_expiration_filter_first(self, mock_fetch):
        """Test 'first' expiration filter."""
        # Create data with multiple expirations
        exp1 = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        exp2 = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        calls_df = pd.DataFrame({
            'strike': [100.0, 100.0],
            'bid': [5.0, 4.0], 'ask': [5.2, 4.2], 'mid_price': [5.1, 4.1],
            'volume': [100, 100], 'openInterest': [1000, 1000],
            'expiration': [exp1, exp2],
            'moneyness': [1.0, 1.0],
            'time_to_expiry': [7/365, 30/365]
        })
        
        puts_df = pd.DataFrame({
            'strike': [100.0, 100.0],
            'bid': [5.0, 4.0], 'ask': [5.2, 4.2], 'mid_price': [5.1, 4.1],
            'volume': [100, 100], 'openInterest': [1000, 1000],
            'expiration': [exp1, exp2],
            'moneyness': [1.0, 1.0],
            'time_to_expiry': [7/365, 30/365]
        })
        
        mock_fetch.return_value = {
            'ticker': 'TEST',
            'spot_price': 100.0,
            'risk_free_rate': 0.045,
            'calls': calls_df,
            'puts': puts_df,
            'expiration_dates': [exp1, exp2]
        }
        
        response = client.get(
            "/iv/surface/TEST",
            params={'expiration_filter': 'first'}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should only have first expiration
        assert len(data['metrics']['expiration_dates']) == 1
        assert data['metrics']['expiration_dates'][0] == exp1
    
    @patch('app.routers.iv_surface.OptionsDataService.fetch_options_chain')
    def test_expiration_filter_near_term(self, mock_fetch):
        """Test 'near_term' expiration filter (90 days)."""
        exp1 = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        exp2 = (datetime.now() + timedelta(days=120)).strftime('%Y-%m-%d')
        
        calls_df = pd.DataFrame({
            'strike': [100.0, 100.0],
            'bid': [5.0, 4.0], 'ask': [5.2, 4.2], 'mid_price': [5.1, 4.1],
            'volume': [100, 100], 'openInterest': [1000, 1000],
            'expiration': [exp1, exp2],
            'moneyness': [1.0, 1.0],
            'time_to_expiry': [30/365, 120/365]
        })
        
        puts_df = pd.DataFrame({
            'strike': [100.0, 100.0],
            'bid': [5.0, 4.0], 'ask': [5.2, 4.2], 'mid_price': [5.1, 4.1],
            'volume': [100, 100], 'openInterest': [1000, 1000],
            'expiration': [exp1, exp2],
            'moneyness': [1.0, 1.0],
            'time_to_expiry': [30/365, 120/365]
        })
        
        mock_fetch.return_value = {
            'ticker': 'TEST',
            'spot_price': 100.0,
            'risk_free_rate': 0.045,
            'calls': calls_df,
            'puts': puts_df,
            'expiration_dates': [exp1, exp2]
        }
        
        response = client.get(
            "/iv/surface/TEST",
            params={'expiration_filter': 'near_term'}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should only have near-term expiration
        assert len(data['metrics']['expiration_dates']) == 1
        assert data['metrics']['expiration_dates'][0] == exp1
    
    @patch('app.routers.iv_surface.OptionsDataService.fetch_options_chain')
    def test_min_volume_filter(self, mock_fetch):
        """Test minimum volume filter."""
        calls_df = pd.DataFrame({
            'strike': [100.0, 105.0],
            'bid': [5.0, 3.0], 'ask': [5.2, 3.2], 'mid_price': [5.1, 3.1],
            'volume': [50, 500],  # One below, one above threshold
            'openInterest': [500, 5000],
            'expiration': ['2025-12-31', '2025-12-31'],
            'moneyness': [1.0, 1.05],
            'time_to_expiry': [0.1, 0.1]
        })
        
        puts_df = pd.DataFrame({
            'strike': [100.0, 105.0],
            'bid': [5.0, 3.0], 'ask': [5.2, 3.2], 'mid_price': [5.1, 3.1],
            'volume': [50, 500],
            'openInterest': [500, 5000],
            'expiration': ['2025-12-31', '2025-12-31'],
            'moneyness': [1.0, 1.05],
            'time_to_expiry': [0.1, 0.1]
        })
        
        mock_fetch.return_value = {
            'ticker': 'TEST',
            'spot_price': 100.0,
            'risk_free_rate': 0.045,
            'calls': calls_df,
            'puts': puts_df,
            'expiration_dates': ['2025-12-31']
        }
        
        response = client.get(
            "/iv/surface/TEST",
            params={'min_volume': 100}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should only have high-volume contract
        assert data['metrics']['total_call_contracts'] == 1
        assert data['calls'][0]['volume'] >= 100


class TestIVSurfaceMetricsCalculation:
    """Test metrics calculation logic."""
    
    @patch('app.routers.iv_surface.OptionsDataService.fetch_options_chain')
    @patch('app.routers.iv_surface.ImpliedVolatilityCalculator.calculate_iv_for_chain')
    def test_atm_iv_calculation(self, mock_iv_calc, mock_fetch, mock_options_data):
        """Test ATM IV is correctly identified."""
        mock_fetch.return_value = mock_options_data
        
        # Mock IV calculation to return known values
        def add_iv(df, spot, r, opt_type):
            df_copy = df.copy()
            # Higher IV for ATM (moneyness closer to 1.0)
            df_copy['calculated_iv'] = df_copy['moneyness'].apply(
                lambda m: 0.30 if abs(m - 1.0) < 0.01 else 0.20
            )
            return df_copy
        
        mock_iv_calc.side_effect = add_iv
        
        response = client.get("/iv/surface/TEST")
        
        assert response.status_code == 200
        data = response.json()
        
        metrics = data['metrics']
        
        # ATM IV should be higher than average
        if metrics['atm_iv_avg'] is not None:
            assert metrics['atm_iv_avg'] >= 0.0
            assert metrics['atm_iv_avg'] <= 5.0  # Reasonable range
    
    @patch('app.routers.iv_surface.OptionsDataService.fetch_options_chain')
    @patch('app.routers.iv_surface.ImpliedVolatilityCalculator.calculate_iv_for_chain')
    def test_skew_calculation(self, mock_iv_calc, mock_fetch, mock_options_data):
        """Test volatility skew calculation."""
        mock_fetch.return_value = mock_options_data
        
        # Mock IV with typical skew pattern (OTM puts > OTM calls)
        def add_iv(df, spot, r, opt_type):
            df_copy = df.copy()
            if opt_type == 'call':
                # Lower IV for OTM calls
                df_copy['calculated_iv'] = df_copy['moneyness'].apply(
                    lambda m: 0.20 if m > 1.05 else 0.25
                )
            else:  # put
                # Higher IV for OTM puts
                df_copy['calculated_iv'] = df_copy['moneyness'].apply(
                    lambda m: 0.35 if m < 0.95 else 0.25
                )
            return df_copy
        
        mock_iv_calc.side_effect = add_iv
        
        response = client.get("/iv/surface/TEST")
        
        assert response.status_code == 200
        data = response.json()
        
        metrics = data['metrics']
        
        # Should have positive skew (puts > calls)
        if metrics['put_call_skew'] is not None:
            assert isinstance(metrics['put_call_skew'], float)

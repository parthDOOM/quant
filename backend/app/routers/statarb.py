"""
Statistical Arbitrage API Router

Provides endpoints for:
- Testing cointegration between asset pairs
- Finding cointegrated pairs within a cluster
- Analyzing spread dynamics and generating trading signals
"""

from fastapi import APIRouter, HTTPException
from typing import List
import pandas as pd
import itertools
import asyncio
import logging

from app.models.statarb import (
    PairTestRequest,
    CointResult,
    FindPairsRequest,
    FindPairsResponse,
    CointegratedPair,
    SpreadAnalysisRequest,
    SpreadAnalysisResponse,
    SpreadPoint,
    SpreadStatistics
)
from app.services.cointegration import CointegrationService
from app.services.data_ingestion import fetch_prices

router = APIRouter(tags=["Statistical Arbitrage"])
logger = logging.getLogger(__name__)


@router.post("/test-pair", response_model=CointResult)
async def test_pair_cointegration(request: PairTestRequest) -> CointResult:
    """
    Test cointegration between two assets using Engle-Granger methodology.

    This endpoint:
    1. Fetches historical price data for both assets
    2. Performs cointegration test
    3. Calculates hedge ratio and half-life
    4. Returns comprehensive cointegration metrics

    Args:
        request: PairTestRequest with tickers and date range

    Returns:
        CointResult with cointegration test results and metrics

    Raises:
        HTTPException 400: Invalid tickers or insufficient data
        HTTPException 500: Internal server error during processing
    """
    try:
        logger.info(f"Testing cointegration: {request.ticker_a} vs {request.ticker_b}")

        # Fetch price data for both assets
        prices_df = fetch_prices(
            [request.ticker_a, request.ticker_b],
            request.start_date,
            request.end_date
        )

        if prices_df.empty or request.ticker_a not in prices_df.columns or request.ticker_b not in prices_df.columns:
            raise HTTPException(
                status_code=400,
                detail=f"No data available for one or both tickers in the specified date range"
            )

        # Extract series
        series_a = prices_df[request.ticker_a]
        series_b = prices_df[request.ticker_b]

        # Test cointegration
        result = CointegrationService.test_cointegration(series_a, series_b)

        return CointResult(
            ticker_a=request.ticker_a,
            ticker_b=request.ticker_b,
            **result
        )

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error testing pair cointegration: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/find-pairs", response_model=FindPairsResponse)
async def find_pairs(request: FindPairsRequest) -> FindPairsResponse:
    """
    Find all cointegrated pairs within a group of assets.

    This endpoint:
    1. Generates all unique pairs from the ticker list
    2. Tests each pair for cointegration concurrently
    3. Returns pairs that meet the p-value threshold

    Args:
        request: FindPairsRequest with tickers, date range, and threshold

    Returns:
        FindPairsResponse with list of cointegrated pairs

    Raises:
        HTTPException 400: Invalid tickers or insufficient data
        HTTPException 500: Internal server error during processing
    """
    try:
        logger.info(f"Finding pairs for {len(request.tickers)} tickers")

        # Generate all unique pairs
        pairs_to_test = list(itertools.combinations(request.tickers, 2))
        total_combinations = len(pairs_to_test)

        logger.info(f"Testing {total_combinations} unique pairs")

        # Fetch price data for all tickers at once
        all_prices = fetch_prices(
            request.tickers,
            request.start_date,
            request.end_date
        )

        if all_prices.empty:
            raise HTTPException(
                status_code=400,
                detail="No data available for the specified tickers and date range"
            )
        
        logger.info(f"Fetched price data: {all_prices.shape[0]} rows, {all_prices.shape[1]} columns")
        logger.info(f"Date range: {all_prices.index[0]} to {all_prices.index[-1]}")

        # Test pairs concurrently
        async def test_single_pair(ticker_a: str, ticker_b: str) -> CointegratedPair | None:
            try:
                if ticker_a not in all_prices.columns or ticker_b not in all_prices.columns:
                    logger.warning(f"Skipping pair {ticker_a}/{ticker_b}: data not available")
                    return None

                series_a = all_prices[ticker_a].dropna()
                series_b = all_prices[ticker_b].dropna()

                # Need at least 30 overlapping observations
                if len(series_a) < 30 or len(series_b) < 30:
                    logger.warning(f"Skipping pair {ticker_a}/{ticker_b}: insufficient data")
                    return None

                result = CointegrationService.test_cointegration(series_a, series_b)
                
                logger.info(f"Pair {ticker_a}/{ticker_b}: p-value={result['p_value']:.4f}, cointegrated={result['is_cointegrated']}")

                # Only return if cointegrated at threshold
                if result['p_value'] < request.p_value_threshold:
                    return CointegratedPair(
                        asset_1=ticker_a,
                        asset_2=ticker_b,
                        p_value=result['p_value'],
                        test_statistic=result['test_statistic'],
                        hedge_ratio=result['hedge_ratio'],
                        half_life=result['half_life'],
                        correlation=result['correlation']
                    )
                return None

            except Exception as e:
                logger.error(f"Error testing pair {ticker_a}/{ticker_b}: {e}")
                return None

        # Run tests concurrently
        tasks = [test_single_pair(pair[0], pair[1]) for pair in pairs_to_test]
        results = await asyncio.gather(*tasks)

        # Filter out None values
        cointegrated_pairs = [r for r in results if r is not None]

        # Sort by p-value (most significant first)
        cointegrated_pairs.sort(key=lambda x: x.p_value)

        logger.info(f"Found {len(cointegrated_pairs)} cointegrated pairs")

        return FindPairsResponse(
            pairs=cointegrated_pairs,
            total_combinations_tested=total_combinations,
            cointegrated_count=len(cointegrated_pairs)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding pairs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/spread-analysis", response_model=SpreadAnalysisResponse)
async def analyze_spread(request: SpreadAnalysisRequest) -> SpreadAnalysisResponse:
    """
    Analyze spread dynamics and generate trading signals for a cointegrated pair.

    This endpoint:
    1. Calculates the spread between two assets
    2. Computes rolling z-scores
    3. Generates entry/exit signals based on thresholds
    4. Returns time series data and statistics

    Args:
        request: SpreadAnalysisRequest with pair details and parameters

    Returns:
        SpreadAnalysisResponse with spread data and signals

    Raises:
        HTTPException 400: Invalid tickers or insufficient data
        HTTPException 500: Internal server error during processing
    """
    try:
        logger.info(f"Analyzing spread: {request.ticker_a} vs {request.ticker_b}")

        # Fetch price data
        prices_df = fetch_prices(
            [request.ticker_a, request.ticker_b],
            request.start_date,
            request.end_date
        )

        if prices_df.empty or request.ticker_a not in prices_df.columns or request.ticker_b not in prices_df.columns:
            raise HTTPException(
                status_code=400,
                detail="No data available for one or both tickers"
            )

        series_a = prices_df[request.ticker_a]
        series_b = prices_df[request.ticker_b]

        # Test cointegration to get hedge ratio
        coint_result = CointegrationService.test_cointegration(series_a, series_b)

        # Calculate spread
        spread = CointegrationService.calculate_spread(
            series_a,
            series_b,
            coint_result['hedge_ratio']
        )

        # Calculate z-scores
        zscore = CointegrationService.calculate_zscore(spread, request.window)

        # Generate signals
        signals = CointegrationService.generate_trading_signals(
            zscore,
            request.entry_threshold,
            request.exit_threshold
        )

        # Build response data
        spread_data = []
        for date in spread.index:
            spread_data.append(SpreadPoint(
                date=date.strftime('%Y-%m-%d'),
                spread=float(spread.loc[date]),
                zscore=float(zscore.loc[date]) if not pd.isna(zscore.loc[date]) else 0.0,
                signal=signals.loc[date] if pd.notna(signals.loc[date]) else None
            ))

        # Calculate statistics
        statistics = SpreadStatistics(
            mean=float(spread.mean()),
            std=float(spread.std()),
            min=float(spread.min()),
            max=float(spread.max())
        )

        return SpreadAnalysisResponse(
            ticker_a=request.ticker_a,
            ticker_b=request.ticker_b,
            hedge_ratio=coint_result['hedge_ratio'],
            half_life=coint_result['half_life'],
            spread_data=spread_data,
            statistics=statistics
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing spread: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

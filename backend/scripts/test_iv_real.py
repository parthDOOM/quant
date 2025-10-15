"""
Real-world validation of Implied Volatility Calculator with AAPL options data.

This script:
1. Fetches real AAPL options chain
2. Calculates IV using our Newton-Raphson solver
3. Compares to yfinance's impliedVolatility values
4. Analyzes the volatility surface patterns
5. Validates convergence and accuracy
"""

import sys
import pandas as pd
from app.services.options_data import OptionsDataService
from app.services.implied_volatility import ImpliedVolatilityCalculator

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.float_format', '{:.4f}'.format)


def main():
    print("=" * 80)
    print("REAL WORLD IV CALCULATOR VALIDATION - AAPL OPTIONS")
    print("=" * 80)
    
    ticker = "AAPL"
    print(f"\n📊 Fetching options chain for {ticker}...")
    
    try:
        # Fetch options data
        options_data = OptionsDataService.fetch_options_chain(ticker)
        spot_price = options_data['spot_price']
        risk_free_rate = options_data['risk_free_rate']
        
        print(f"✅ Spot Price: ${spot_price:.2f}")
        print(f"✅ Risk-Free Rate: {risk_free_rate:.2%}")
        print(f"✅ Expiration Dates: {len(options_data['expiration_dates'])}")
        
        # Get first expiration for focused analysis
        calls = options_data['calls']
        puts = options_data['puts']
        
        # Filter to first expiration only for clearer analysis
        first_exp = calls['expiration'].min()
        calls_first = calls[calls['expiration'] == first_exp].copy()
        puts_first = puts[puts['expiration'] == first_exp].copy()
        
        print(f"\n🎯 Analyzing expiration: {first_exp}")
        print(f"   Calls: {len(calls_first)} contracts")
        print(f"   Puts: {len(puts_first)} contracts")
        
        # Calculate IV for calls
        print("\n⚙️ Calculating Implied Volatility for CALLS...")
        calls_with_iv = ImpliedVolatilityCalculator.calculate_iv_for_chain(
            calls_first,
            spot_price,
            risk_free_rate,
            'call'
        )
        
        # Calculate IV for puts
        print("⚙️ Calculating Implied Volatility for PUTS...")
        puts_with_iv = ImpliedVolatilityCalculator.calculate_iv_for_chain(
            puts_first,
            spot_price,
            risk_free_rate,
            'put'
        )
        
        # Analyze results
        print("\n" + "=" * 80)
        print("RESULTS ANALYSIS")
        print("=" * 80)
        
        # Calls analysis
        calls_valid = calls_with_iv[calls_with_iv['calculated_iv'].notna()].copy()
        print(f"\n📈 CALLS - Successfully calculated IV for {len(calls_valid)}/{len(calls_with_iv)} contracts")
        
        if len(calls_valid) > 0:
            # Compare to yfinance IV
            calls_valid['yf_iv'] = calls_valid['impliedVolatility']
            calls_valid['iv_diff'] = (calls_valid['calculated_iv'] - calls_valid['yf_iv']).abs()
            
            print(f"\n   Our IV Stats:")
            print(f"     Mean: {calls_valid['calculated_iv'].mean():.2%}")
            print(f"     Std:  {calls_valid['calculated_iv'].std():.2%}")
            print(f"     Min:  {calls_valid['calculated_iv'].min():.2%}")
            print(f"     Max:  {calls_valid['calculated_iv'].max():.2%}")
            
            print(f"\n   yfinance IV Stats:")
            print(f"     Mean: {calls_valid['yf_iv'].mean():.2%}")
            print(f"     Std:  {calls_valid['yf_iv'].std():.2%}")
            
            print(f"\n   Comparison:")
            print(f"     Mean Absolute Difference: {calls_valid['iv_diff'].mean():.2%}")
            print(f"     Max Difference: {calls_valid['iv_diff'].max():.2%}")
            print(f"     Correlation: {calls_valid['calculated_iv'].corr(calls_valid['yf_iv']):.4f}")
            
            # Sample contracts
            print(f"\n   Sample Call Contracts (ATM region):")
            atm_calls = calls_valid.iloc[(calls_valid['moneyness'] - 1.0).abs().argsort()[:5]]
            print(atm_calls[['strike', 'moneyness', 'mid_price', 'calculated_iv', 'yf_iv', 'iv_diff']].to_string(index=False))
        
        # Puts analysis
        puts_valid = puts_with_iv[puts_with_iv['calculated_iv'].notna()].copy()
        print(f"\n📉 PUTS - Successfully calculated IV for {len(puts_valid)}/{len(puts_with_iv)} contracts")
        
        if len(puts_valid) > 0:
            puts_valid['yf_iv'] = puts_valid['impliedVolatility']
            puts_valid['iv_diff'] = (puts_valid['calculated_iv'] - puts_valid['yf_iv']).abs()
            
            print(f"\n   Our IV Stats:")
            print(f"     Mean: {puts_valid['calculated_iv'].mean():.2%}")
            print(f"     Std:  {puts_valid['calculated_iv'].std():.2%}")
            print(f"     Min:  {puts_valid['calculated_iv'].min():.2%}")
            print(f"     Max:  {puts_valid['calculated_iv'].max():.2%}")
            
            print(f"\n   yfinance IV Stats:")
            print(f"     Mean: {puts_valid['yf_iv'].mean():.2%}")
            print(f"     Std:  {puts_valid['yf_iv'].std():.2%}")
            
            print(f"\n   Comparison:")
            print(f"     Mean Absolute Difference: {puts_valid['iv_diff'].mean():.2%}")
            print(f"     Max Difference: {puts_valid['iv_diff'].max():.2%}")
            print(f"     Correlation: {puts_valid['calculated_iv'].corr(puts_valid['yf_iv']):.4f}")
            
            # Sample contracts
            print(f"\n   Sample Put Contracts (ATM region):")
            atm_puts = puts_valid.iloc[(puts_valid['moneyness'] - 1.0).abs().argsort()[:5]]
            print(atm_puts[['strike', 'moneyness', 'mid_price', 'calculated_iv', 'yf_iv', 'iv_diff']].to_string(index=False))
        
        # Volatility smile/skew analysis
        print("\n" + "=" * 80)
        print("VOLATILITY SURFACE PATTERNS")
        print("=" * 80)
        
        if len(calls_valid) > 0 and len(puts_valid) > 0:
            # ATM volatility
            atm_idx_call = (calls_valid['moneyness'] - 1.0).abs().idxmin()
            atm_idx_put = (puts_valid['moneyness'] - 1.0).abs().idxmin()
            calls_atm = calls_valid.loc[atm_idx_call]
            puts_atm = puts_valid.loc[atm_idx_put]
            
            print(f"\n📍 At-The-Money IV:")
            print(f"   Call ATM IV: {calls_atm['calculated_iv']:.2%} (strike ${calls_atm['strike']:.0f})")
            print(f"   Put ATM IV:  {puts_atm['calculated_iv']:.2%} (strike ${puts_atm['strike']:.0f})")
            
            # OTM analysis
            otm_calls = calls_valid[calls_valid['moneyness'] > 1.05]  # >5% OTM
            otm_puts = puts_valid[puts_valid['moneyness'] < 0.95]  # >5% OTM
            
            if len(otm_calls) > 0 and len(otm_puts) > 0:
                print(f"\n📊 Volatility Skew:")
                print(f"   OTM Call IV (mean): {otm_calls['calculated_iv'].mean():.2%}")
                print(f"   ATM IV (avg):       {(calls_atm['calculated_iv'] + puts_atm['calculated_iv'])/2:.2%}")
                print(f"   OTM Put IV (mean):  {otm_puts['calculated_iv'].mean():.2%}")
                
                skew = otm_puts['calculated_iv'].mean() - otm_calls['calculated_iv'].mean()
                print(f"\n   Put-Call Skew: {skew:.2%}")
                if skew > 0:
                    print("   ✅ Normal negative skew (OTM puts > OTM calls)")
                else:
                    print("   ⚠️ Inverted skew")
        
        # Overall validation
        print("\n" + "=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)
        
        total_contracts = len(calls_with_iv) + len(puts_with_iv)
        successful_ivs = len(calls_valid) + len(puts_valid)
        success_rate = successful_ivs / total_contracts * 100
        
        print(f"\n✅ Successfully calculated IV for {successful_ivs}/{total_contracts} contracts ({success_rate:.1f}%)")
        
        if len(calls_valid) > 0 and len(puts_valid) > 0:
            avg_diff = (calls_valid['iv_diff'].mean() + puts_valid['iv_diff'].mean()) / 2
            avg_corr = (calls_valid['calculated_iv'].corr(calls_valid['yf_iv']) + 
                       puts_valid['calculated_iv'].corr(puts_valid['yf_iv'])) / 2
            
            print(f"✅ Average difference vs yfinance: {avg_diff:.2%}")
            print(f"✅ Average correlation with yfinance: {avg_corr:.4f}")
            
            if avg_diff < 0.02 and avg_corr > 0.95:
                print("\n🎉 EXCELLENT: IV calculations are highly accurate!")
            elif avg_diff < 0.05 and avg_corr > 0.90:
                print("\n✅ GOOD: IV calculations are accurate and reliable!")
            else:
                print("\n⚠️ MODERATE: Some discrepancies detected, review edge cases")
        
        print("\n" + "=" * 80)
        print("✅ Real-world validation complete!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

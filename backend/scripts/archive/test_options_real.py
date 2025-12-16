"""
Manual test script for Options Data Service
Tests with real data from yfinance
"""

from app.services.options_data import OptionsDataService

def test_real_options_data():
    """Test fetching real options data for AAPL"""
    print("=" * 80)
    print("Testing Options Data Service with Real Data (AAPL)")
    print("=" * 80)
    
    try:
        # Fetch options chain
        print("\n1. Fetching options chain for AAPL...")
        options_data = OptionsDataService.fetch_options_chain('AAPL')
        
        print(f"   ✓ Successfully fetched options data")
        print(f"   Spot Price: ${options_data['spot_price']:.2f}")
        print(f"   Risk-Free Rate: {options_data['risk_free_rate']:.1%}")
        print(f"   Number of expiration dates: {len(options_data['expiration_dates'])}")
        
        # Display calls data
        calls_df = options_data['calls']
        print(f"\n2. Calls Data:")
        print(f"   Total contracts: {len(calls_df)}")
        if not calls_df.empty:
            print(f"   Strike range: ${calls_df['strike'].min():.2f} - ${calls_df['strike'].max():.2f}")
            print(f"   Sample contracts:")
            print(calls_df[['strike', 'bid', 'ask', 'mid_price', 'moneyness', 'time_to_expiry', 'volume']].head(5).to_string(index=False))
        
        # Display puts data
        puts_df = options_data['puts']
        print(f"\n3. Puts Data:")
        print(f"   Total contracts: {len(puts_df)}")
        if not puts_df.empty:
            print(f"   Strike range: ${puts_df['strike'].min():.2f} - ${puts_df['strike'].max():.2f}")
            print(f"   Sample contracts:")
            print(puts_df[['strike', 'bid', 'ask', 'mid_price', 'moneyness', 'time_to_expiry', 'volume']].head(5).to_string(index=False))
        
        # Get summary
        print(f"\n4. Options Summary:")
        summary = OptionsDataService.get_options_summary(options_data)
        for key, value in summary.items():
            print(f"   {key}: {value}")
        
        print(f"\n{'='*80}")
        print("✅ SUCCESS: All operations completed successfully!")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"\n{'='*80}")
        print(f"❌ ERROR: {str(e)}")
        print(f"{'='*80}\n")
        raise

if __name__ == "__main__":
    test_real_options_data()

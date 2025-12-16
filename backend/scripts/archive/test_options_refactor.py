"""Test options_data.py refactoring with provider interface."""
import asyncio
from app.services.options_data import OptionsDataService
from app.services.provider_factory import get_options_provider

async def test_options_refactor():
    print("=" * 60)
    print("TESTING OPTIONS DATA REFACTORING")
    print("=" * 60)
    
    provider = get_options_provider()
    ticker = "AAPL"
    
    print(f"\nProvider: {provider.name}")
    print(f"Testing ticker: {ticker}")
    
    # Test 1: Fetch spot price
    print("\n1️⃣ Testing fetch_spot_price...")
    try:
        spot_price = await OptionsDataService.fetch_spot_price(ticker, provider)
        print(f"   ✅ Spot price: ${spot_price:.2f}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 2: Fetch options chain
    print("\n2️⃣ Testing fetch_options_chain...")
    try:
        options_data = await OptionsDataService.fetch_options_chain(ticker, provider)
        
        print(f"   ✅ Options chain fetched successfully!")
        print(f"   Ticker: {options_data['ticker']}")
        print(f"   Spot: ${options_data['spot_price']:.2f}")
        print(f"   Risk-free rate: {options_data['risk_free_rate']:.2%}")
        print(f"   Calls: {len(options_data['calls'])} contracts")
        print(f"   Puts: {len(options_data['puts'])} contracts")
        print(f"   Expirations: {len(options_data['expiration_dates'])} dates")
        
        if options_data['expiration_dates']:
            print(f"   First expiration: {options_data['expiration_dates'][0]}")
            print(f"   Last expiration: {options_data['expiration_dates'][-1]}")
        
        # Show sample calls data
        if not options_data['calls'].empty:
            print(f"\n   Sample Calls (first 3):")
            print(options_data['calls'][['strike', 'bid', 'ask', 'volume', 'expiration']].head(3).to_string(index=False))
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 60)
    print("CONCLUSION")
    print("=" * 60)
    print("✅ Options data service successfully refactored!")
    print("✅ Using provider interface for data fetching")
    print("✅ Both spot price and options chain working")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_options_refactor())

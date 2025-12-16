"""Debug what the provider returns for options."""
import asyncio
from app.services.provider_factory import get_options_provider

async def debug_options():
    provider = get_options_provider()
    ticker = "AAPL"
    
    print(f"Provider: {provider.name}")
    print(f"Testing: {ticker}\n")
    
    try:
        options_data = await provider.get_options_chain(ticker)
        
        print("Keys in response:", list(options_data.keys()))
        print()
        
        if 'calls' in options_data and not options_data['calls'].empty:
            print("Calls DataFrame columns:")
            print(list(options_data['calls'].columns))
            print("\nCalls DataFrame shape:", options_data['calls'].shape)
            print("\nFirst few rows of calls:")
            print(options_data['calls'].head())
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_options())

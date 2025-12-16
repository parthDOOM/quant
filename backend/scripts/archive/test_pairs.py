"""Test script to find cointegrated pairs"""
import yfinance as yf
import pandas as pd
from statsmodels.tsa.stattools import coint

# Test multiple pairs
pairs = [
    ('SPY', 'IVV'),   # S&P 500 ETFs - should be cointegrated
    ('SPY', 'VOO'),   # S&P 500 ETFs
    ('QQQ', 'QQQM'),  # Nasdaq ETFs
    ('VTI', 'ITOT'),  # Total market ETFs
    ('EWA', 'EWC'),   # Australia/Canada ETFs
    ('XLE', 'XOM'),   # Energy sector
    ('GLD', 'SLV'),   # Gold/Silver
    ('KO', 'PEP'),    # Coca-Cola/Pepsi
]

start = '2024-01-01'
end = '2025-10-15'

print("Testing pairs for cointegration...")
print(f"Period: {start} to {end}\n")
print(f"{'Pair':<15} {'P-Value':<12} {'Cointegrated':<15} {'Data Points':<12} {'Correlation'}")
print("-" * 80)

for t1, t2 in pairs:
    try:
        data = yf.download([t1, t2], start=start, end=end, progress=False)
        s1 = data['Close'][t1].dropna()
        s2 = data['Close'][t2].dropna()
        df = pd.DataFrame({t1: s1, t2: s2}).dropna()
        
        if len(df) > 30:
            score, pval, _ = coint(df[t1], df[t2])
            corr = df[t1].corr(df[t2])
            coint_str = "✓ YES" if pval < 0.05 else "✗ NO"
            print(f"{t1}/{t2:<11} {pval:<12.4f} {coint_str:<15} {len(df):<12} {corr:.4f}")
        else:
            print(f"{t1}/{t2:<11} {'INSUFFICIENT DATA'}")
    except Exception as e:
        print(f"{t1}/{t2:<11} ERROR: {str(e)[:40]}")

print("\n\nCointegrated pairs (p < 0.05) that you can use:")
print("=" * 80)
for t1, t2 in pairs:
    try:
        data = yf.download([t1, t2], start=start, end=end, progress=False)
        s1 = data['Close'][t1].dropna()
        s2 = data['Close'][t2].dropna()
        df = pd.DataFrame({t1: s1, t2: s2}).dropna()
        
        if len(df) > 30:
            score, pval, _ = coint(df[t1], df[t2])
            if pval < 0.05:
                print(f"✓ {t1} and {t2} (p-value: {pval:.6f})")
    except:
        pass

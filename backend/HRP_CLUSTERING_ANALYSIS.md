# HRP Clustering - C++ Migration Analysis

## Summary
Implemented C++ HRP clustering functions but discovered they're **slower than scipy/numpy**.

## Implementation Details

### What Was Built
- **correlation_to_distance**: Element-wise matrix transformation with OpenMP
- **single_linkage**: Hierarchical clustering algorithm (single linkage)
- **get_seriation_order**: Tree traversal to extract leaf ordering

### Performance Results
```
50 assets:   1.16x speedup (marginal)
200 assets:  0.00x speedup (slower!)
500 assets:  0.06x speedup (much slower!)
```

### Why C++ Was Slower

#### 1. Matrix Operations
- **Numpy advantage**: Built on MKL/OpenBLAS with SIMD optimizations
- **C++ overhead**: 
  - Data conversion (Python list → C++ vector)
  - OpenMP thread spawning overhead
  - Cache misses from `vector<vector<double>>` layout
- **Result**: Numpy's `np.sqrt(0.5 * (1 - corr))` is faster than C++ equivalent

#### 2. Linkage Algorithm Complexity
- **My implementation**: O(n³) naive algorithm
  - Find min distance: O(n²) scan
  - Repeated n-1 times: O(n³) total
  - For 500 assets: 500² × 499 ≈ 125 million comparisons!

- **Scipy implementation**: O(n²) optimized
  - Uses priority queues / efficient data structures
  - Battle-tested over decades
  - Highly optimized C/Fortran code

#### 3. Data Structure Overhead
```cpp
std::vector<std::vector<double>> distance_matrix;  // Cache-unfriendly
```
- Nested vectors = pointer chasing
- Poor cache locality
- Should use flat array: `vector<double>` of size n×n

## Key Learnings

### When C++ Wins
✅ **Tight loops with branching** (Monte Carlo: 9-11x)
✅ **Iterative numerical methods** (IV Calculator: 850-2000x)
✅ **Custom algorithms** not in standard libraries

### When NumPy/SciPy Wins
❌ **Matrix operations** (BLAS/LAPACK optimizations)
❌ **Graph algorithms** (unless heavily optimized)
❌ **Well-established algorithms** (scipy's linkage, clustering)

### The Python Interop Tax
Converting between Python and C++ has overhead:
- List → vector conversion: O(n) memory copy
- numpy array → C++ vector: Same overhead
- For large data (1000×1000 matrix), this overhead is significant

## Recommendation

**Don't use C++ HRP clustering.** Stick with scipy/numpy because:
1. **Performance**: Scipy is faster and better optimized
2. **Reliability**: Battle-tested over decades
3. **Maintenance**: No need to maintain C++ code
4. **Correctness**: Scipy handles edge cases, numerical stability

## What to Keep

The C++ code is **correct** (matches scipy output exactly), but:
- Not faster than scipy
- Not worth the maintenance burden
- Can be removed or kept as a learning example

## Conclusion

This was a valuable learning experience:
- **Not all algorithms benefit from C++**
- **Profiling before optimization is crucial**
- **Numpy/SciPy are incredibly well-optimized**
- **Focus C++ effort on algorithms where it matters**

**Net Result**: Keep Monte Carlo (9-11x) and IV Calculator (850-2000x), skip HRP clustering.

---

*Note: The implementation is correct and working, just not faster than scipy. This is expected for well-optimized library functions.*

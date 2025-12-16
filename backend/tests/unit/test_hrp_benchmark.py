"""
HRP Clustering Performance Benchmark
Tests C++ vs Python implementation performance
"""
import sys
sys.path.insert(0, 'app/services')

import numpy as np
import time
from scipy.cluster.hierarchy import linkage, leaves_list
from scipy.spatial.distance import squareform
import core_cpp

def generate_random_correlation(n):
    """Generate random correlation matrix"""
    # Generate random covariance matrix
    A = np.random.randn(n, n)
    cov = np.dot(A, A.T)
    
    # Convert to correlation
    D = np.sqrt(np.diag(cov))
    corr = cov / np.outer(D, D)
    
    # Ensure it's exactly symmetric
    corr = (corr + corr.T) / 2
    np.fill_diagonal(corr, 1.0)
    
    return corr

def python_hrp_clustering(corr_matrix):
    """Python implementation using scipy"""
    # Convert to distance
    dist = np.sqrt(0.5 * (1 - corr_matrix))
    
    # Perform clustering
    condensed = squareform(dist)
    link = linkage(condensed, method='single')
    
    # Get seriation order
    order = leaves_list(link)
    
    return dist, link, order

def cpp_hrp_clustering(corr_matrix):
    """C++ implementation"""
    # Convert to list of lists for C++
    corr_list = corr_matrix.tolist()
    
    # Distance calculation
    dist = core_cpp.HRPClustering.correlation_to_distance(corr_list)
    
    # Clustering
    linkage_matrix = core_cpp.HRPClustering.single_linkage(dist)
    
    # Seriation
    n = len(corr_matrix)
    order = core_cpp.HRPClustering.get_seriation_order(linkage_matrix, n)
    
    return dist, linkage_matrix, order

print("=" * 70)
print("HRP CLUSTERING PERFORMANCE BENCHMARK")
print("=" * 70)
print()

# Warm-up test
print("Warm-up: 10x10 correlation matrix")
print("-" * 70)
corr = generate_random_correlation(10)

# Python
start = time.time()
py_dist, py_link, py_order = python_hrp_clustering(corr)
time_py = time.time() - start

# C++
start = time.time()
cpp_dist, cpp_link, cpp_order = cpp_hrp_clustering(corr)
time_cpp = time.time() - start

print(f"Python Time:    {time_py:.4f}s")
print(f"C++ Time:       {time_cpp:.4f}s")
print(f"Speedup:        {time_py / max(time_cpp, 0.0001):.2f}x")

# Verify correctness
dist_match = np.allclose(py_dist, np.array(cpp_dist), atol=1e-10)
link_match = np.allclose(py_link, np.array(cpp_link), atol=1e-10)
order_match = np.array_equal(py_order, cpp_order)

print(f"Distance match: {dist_match}")
print(f"Linkage match:  {link_match}")
print(f"Order match:    {order_match}")
print()

# Test 1: Small portfolio (50 assets)
print("Test 1: 50 assets (small portfolio)")
print("-" * 70)
corr = generate_random_correlation(50)

# Python
start = time.time()
py_dist, py_link, py_order = python_hrp_clustering(corr)
time_py = time.time() - start

# C++
start = time.time()
cpp_dist, cpp_link, cpp_order = cpp_hrp_clustering(corr)
time_cpp = time.time() - start

speedup = time_py / max(time_cpp, 0.0001)
print(f"Python Time:    {time_py:.4f}s")
print(f"C++ Time:       {time_cpp:.4f}s")
print(f"Speedup:        {speedup:.2f}x")
print()

# Test 2: Medium portfolio (200 assets)
print("Test 2: 200 assets (medium portfolio)")
print("-" * 70)
corr = generate_random_correlation(200)

# Python
start = time.time()
py_dist, py_link, py_order = python_hrp_clustering(corr)
time_py = time.time() - start

# C++
start = time.time()
cpp_dist, cpp_link, cpp_order = cpp_hrp_clustering(corr)
time_cpp = time.time() - start

speedup = time_py / max(time_cpp, 0.0001)
print(f"Python Time:    {time_py:.4f}s")
print(f"C++ Time:       {time_cpp:.4f}s")
print(f"Speedup:        {speedup:.2f}x")
print()

# Test 3: Large portfolio (500 assets)
print("Test 3: 500 assets (large portfolio)")
print("-" * 70)
corr = generate_random_correlation(500)

# Python
start = time.time()
py_dist, py_link, py_order = python_hrp_clustering(corr)
time_py = time.time() - start

# C++
start = time.time()
cpp_dist, cpp_link, cpp_order = cpp_hrp_clustering(corr)
time_cpp = time.time() - start

speedup = time_py / max(time_cpp, 0.0001)
print(f"Python Time:    {time_py:.4f}s")
print(f"C++ Time:       {time_cpp:.4f}s")
print(f"Speedup:        {speedup:.2f}x")
print()

print("=" * 70)
print("BENCHMARK COMPLETE")
print("=" * 70)

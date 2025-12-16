#include "hello.h"
#include <random>
#include <cmath>
#include <stdexcept>
#include <omp.h>
#include <algorithm>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#ifndef M_SQRT1_2
#define M_SQRT1_2 0.70710678118654752440
#endif

namespace monte_carlo {
    
    MonteCarloSimulator::MonteCarloSimulator(int num_simulations, int num_days)
        : num_simulations_(num_simulations), num_days_(num_days) {
        if (num_simulations <= 0 || num_days <= 0) {
            throw std::invalid_argument("num_simulations and num_days must be positive");
        }
    }
    
    std::vector<std::vector<std::vector<double>>> MonteCarloSimulator::simulate(
        const std::vector<double>& returns,
        const std::vector<std::vector<double>>& cov_matrix,
        const std::vector<double>& initial_prices
    ) {
        int num_assets = returns.size();
        
        // Validate inputs
        if (num_assets == 0) {
            throw std::invalid_argument("returns vector is empty");
        }
        if (cov_matrix.size() != num_assets || cov_matrix[0].size() != num_assets) {
            throw std::invalid_argument("covariance matrix dimensions don't match returns");
        }
        if (initial_prices.size() != num_assets) {
            throw std::invalid_argument("initial_prices size doesn't match returns");
        }
        
        // Convert covariance matrix to Eigen
        Eigen::MatrixXd cov_eigen(num_assets, num_assets);
        for (int i = 0; i < num_assets; ++i) {
            for (int j = 0; j < num_assets; ++j) {
                cov_eigen(i, j) = cov_matrix[i][j];
            }
        }
        
        // Cholesky decomposition for correlated random numbers
        Eigen::LLT<Eigen::MatrixXd> llt(cov_eigen);
        if (llt.info() != Eigen::Success) {
            throw std::runtime_error("Cholesky decomposition failed - matrix not positive definite");
        }
        Eigen::MatrixXd cholesky = llt.matrixL();
        
        // Initialize result
        std::vector<std::vector<std::vector<double>>> results(
            num_simulations_,
            std::vector<std::vector<double>>(
                num_days_,
                std::vector<double>(num_assets, 0.0)
            )
        );
        
        // Run simulations in parallel
        #pragma omp parallel
        {
            // Each thread gets its own random number generator
            std::random_device rd;
            std::mt19937 gen(rd() + omp_get_thread_num());
            std::normal_distribution<double> norm(0.0, 1.0);
            
            #pragma omp for
            for (int sim = 0; sim < num_simulations_; ++sim) {
                // Set initial prices
                for (int asset = 0; asset < num_assets; ++asset) {
                    results[sim][0][asset] = initial_prices[asset];
                }
                
                // Simulate each day
                for (int day = 1; day < num_days_; ++day) {
                    // Generate independent random numbers
                    Eigen::VectorXd randoms(num_assets);
                    for (int asset = 0; asset < num_assets; ++asset) {
                        randoms(asset) = norm(gen);
                    }
                    
                    // Apply Cholesky to get correlated randoms
                    Eigen::VectorXd correlated = cholesky * randoms;
                    
                    // Update prices using geometric Brownian motion
                    for (int asset = 0; asset < num_assets; ++asset) {
                        double prev_price = results[sim][day - 1][asset];
                        double drift = returns[asset];
                        double shock = correlated(asset);
                        
                        // S_{t+1} = S_t * exp(drift + shock)
                        results[sim][day][asset] = prev_price * std::exp(drift + shock);
                    }
                }
            }
        }
        
        return results;
    }
    
    Eigen::MatrixXd MonteCarloSimulator::generate_correlated_randoms(
        const Eigen::MatrixXd& cholesky_matrix,
        int num_samples
    ) {
        int num_vars = cholesky_matrix.rows();
        Eigen::MatrixXd randoms(num_vars, num_samples);
        
        std::random_device rd;
        std::mt19937 gen(rd());
        std::normal_distribution<double> norm(0.0, 1.0);
        
        for (int i = 0; i < num_vars; ++i) {
            for (int j = 0; j < num_samples; ++j) {
                randoms(i, j) = norm(gen);
            }
        }
        
        return cholesky_matrix * randoms;
    }
    
} // namespace monte_carlo


// ============================================================================
// IMPLIED VOLATILITY IMPLEMENTATION
// ============================================================================

namespace implied_volatility {
    
    // Standard normal CDF approximation (accurate to 7 decimal places)
    double IVCalculator::norm_cdf(double x) {
        return 0.5 * std::erfc(-x * M_SQRT1_2);
    }
    
    // Standard normal PDF
    double IVCalculator::norm_pdf(double x) {
        return std::exp(-0.5 * x * x) / std::sqrt(2.0 * M_PI);
    }
    
    // Calculate d1 and d2 for Black-Scholes
    void IVCalculator::calculate_d1_d2(
        double S, double K, double T, double r, double sigma, double q,
        double& d1, double& d2
    ) {
        double sqrt_T = std::sqrt(T);
        d1 = (std::log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / (sigma * sqrt_T);
        d2 = d1 - sigma * sqrt_T;
    }
    
    // Black-Scholes option pricing
    double IVCalculator::black_scholes_price(
        double S, double K, double T, double r, double sigma,
        bool is_call, double q
    ) {
        if (S <= 0 || K <= 0 || T <= 0 || sigma <= 0) {
            return 0.0;
        }
        
        double d1, d2;
        calculate_d1_d2(S, K, T, r, sigma, q, d1, d2);
        
        if (is_call) {
            return S * std::exp(-q * T) * norm_cdf(d1) - K * std::exp(-r * T) * norm_cdf(d2);
        } else {
            return K * std::exp(-r * T) * norm_cdf(-d2) - S * std::exp(-q * T) * norm_cdf(-d1);
        }
    }
    
    // Vega calculation
    double IVCalculator::vega(
        double S, double K, double T, double r, double sigma, double q
    ) {
        if (T <= 0 || sigma <= 0) {
            return 0.0;
        }
        
        double d1, d2;
        calculate_d1_d2(S, K, T, r, sigma, q, d1, d2);
        
        return S * std::exp(-q * T) * norm_pdf(d1) * std::sqrt(T);
    }
    
    // Newton-Raphson IV solver
    double IVCalculator::calculate_iv(
        double market_price, double S, double K, double T, double r,
        bool is_call, double q, double initial_guess
    ) {
        // Validation
        if (market_price <= 0 || S <= 0 || K <= 0 || T <= 0) {
            return -1.0;  // Invalid input
        }
        
        // Check intrinsic value
        double intrinsic = is_call ? std::max(0.0, S - K) : std::max(0.0, K - S);
        if (market_price < intrinsic * 0.99) {
            return -1.0;  // Below intrinsic value
        }
        
        double sigma = initial_guess;
        
        // Newton-Raphson iterations
        for (int iter = 0; iter < MAX_ITERATIONS; ++iter) {
            double bs_price = black_scholes_price(S, K, T, r, sigma, is_call, q);
            double price_diff = bs_price - market_price;
            
            // Check convergence
            if (std::abs(price_diff) < TOLERANCE) {
                if (sigma >= MIN_VOLATILITY && sigma <= MAX_VOLATILITY) {
                    return sigma;
                } else {
                    return -1.0;  // Out of bounds
                }
            }
            
            // Calculate Vega
            double vega_val = vega(S, K, T, r, sigma, q);
            
            // Avoid division by zero
            if (std::abs(vega_val) < 1e-8) {
                return -1.0;  // Vega too small
            }
            
            // Newton-Raphson update
            double sigma_new = sigma - price_diff / vega_val;
            
            // Enforce bounds
            sigma_new = std::clamp(sigma_new, MIN_VOLATILITY, MAX_VOLATILITY);
            
            // Check for stagnation
            if (std::abs(sigma_new - sigma) < 1e-8) {
                return -1.0;  // Stagnated
            }
            
            sigma = sigma_new;
        }
        
        return -1.0;  // Failed to converge
    }
    
    // Batch IV calculation (vectorized for cache efficiency)
    std::vector<double> IVCalculator::calculate_iv_batch(
        const std::vector<double>& market_prices,
        const std::vector<double>& spots,
        const std::vector<double>& strikes,
        const std::vector<double>& times,
        const std::vector<double>& rates,
        const std::vector<bool>& is_calls,
        const std::vector<double>& divs
    ) {
        size_t n = market_prices.size();
        std::vector<double> ivs(n);
        
        
        // Parallel computation
        #pragma omp parallel for
        for (int i = 0; i < static_cast<int>(n); ++i) {
            ivs[i] = calculate_iv(
                market_prices[i],
                spots[i],
                strikes[i],
                times[i],
                rates[i],
                is_calls[i],
                divs[i]
            );
        }
        
        return ivs;
    }
    
    
} // namespace implied_volatility


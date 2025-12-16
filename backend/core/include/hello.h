#ifndef MONTE_CARLO_H
#define MONTE_CARLO_H

#include <vector>
#include <Eigen/Dense>

namespace monte_carlo {
    
    class MonteCarloSimulator {
    public:
        MonteCarloSimulator(int num_simulations, int num_days);
        
        std::vector<std::vector<std::vector<double>>> simulate(
            const std::vector<double>& returns,
            const std::vector<std::vector<double>>& cov_matrix,
            const std::vector<double>& initial_prices
        );
        
    private:
        int num_simulations_;
        int num_days_;
        
        Eigen::MatrixXd generate_correlated_randoms(
            const Eigen::MatrixXd& cholesky_matrix,
            int num_samples
        );
    };
    
} // namespace monte_carlo


namespace implied_volatility {
    
    /**
     * Black-Scholes-Merton option pricer and IV solver
     * Optimized C++ implementation with vectorization
     */
    class IVCalculator {
    public:
        // Constants
        static constexpr int MAX_ITERATIONS = 100;
        static constexpr double TOLERANCE = 1e-6;
        static constexpr double MIN_VOLATILITY = 0.001;
        static constexpr double MAX_VOLATILITY = 5.0;
        static constexpr double INITIAL_GUESS = 0.25;
        
        /**
         * Calculate Black-Scholes option price
         */
        static double black_scholes_price(
            double S, double K, double T, double r, double sigma,
            bool is_call, double q = 0.0
        );
        
        /**
         * Calculate Vega (∂Price/∂σ)
         */
        static double vega(
            double S, double K, double T, double r, double sigma, double q = 0.0
        );
        
        /**
         * Calculate implied volatility using Newton-Raphson
         * Returns -1.0 if no solution found
         */
        static double calculate_iv(
            double market_price, double S, double K, double T, double r,
            bool is_call, double q = 0.0, double initial_guess = INITIAL_GUESS
        );
        
        /**
         * Batch IV calculation for multiple options
         * Much faster than individual calculations due to cache locality
         */
        static std::vector<double> calculate_iv_batch(
            const std::vector<double>& market_prices,
            const std::vector<double>& spots,
            const std::vector<double>& strikes,
            const std::vector<double>& times,
            const std::vector<double>& rates,
            const std::vector<bool>& is_calls,
            const std::vector<double>& divs
        );
        
    private:
        // Helper functions
        static double norm_cdf(double x);
        static double norm_pdf(double x);
        static void calculate_d1_d2(
            double S, double K, double T, double r, double sigma, double q,
            double& d1, double& d2
        );
    };
    
} // namespace implied_volatility

#endif // MONTE_CARLO_H


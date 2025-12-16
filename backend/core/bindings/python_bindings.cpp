#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "hello.h"

namespace py = pybind11;

PYBIND11_MODULE(core_cpp, m) {
    m.doc() = "Optimized C++ Financial Calculations Module";
    
    // Monte Carlo Simulator
    py::class_<monte_carlo::MonteCarloSimulator>(m, "MonteCarloSimulator")
        .def(py::init<int, int>(),
             py::arg("num_simulations"),
             py::arg("num_days"),
             "Initialize Monte Carlo simulator")
        .def("simulate", &monte_carlo::MonteCarloSimulator::simulate,
             py::arg("returns"),
             py::arg("cov_matrix"),
             py::arg("initial_prices"),
             "Run Monte Carlo simulation");
    
    // IV Calculator
    py::class_<implied_volatility::IVCalculator>(m, "IVCalculator")
        .def(py::init<>())
        .def_static("black_scholes_price",
                   &implied_volatility::IVCalculator::black_scholes_price,
                   py::arg("S"), py::arg("K"), py::arg("T"),
                   py::arg("r"), py::arg("sigma"), py::arg("is_call"),
                   py::arg("q") = 0.0,
                   "Calculate Black-Scholes option price")
        .def_static("vega",
                   &implied_volatility::IVCalculator::vega,
                   py::arg("S"), py::arg("K"), py::arg("T"),
                   py::arg("r"), py::arg("sigma"), py::arg("q") = 0.0,
                   "Calculate Vega")
        .def_static("calculate_iv",
                   &implied_volatility::IVCalculator::calculate_iv,
                   py::arg("market_price"), py::arg("S"), py::arg("K"),
                   py::arg("T"), py::arg("r"), py::arg("is_call"),
                   py::arg("q") = 0.0,
                   py::arg("initial_guess") = 0.25,
                   "Calculate implied volatility (returns -1 if failed)")
        .def_static("calculate_iv_batch",
                   &implied_volatility::IVCalculator::calculate_iv_batch,
                   py::arg("market_prices"), py::arg("spots"),
                   py::arg("strikes"), py::arg("times"),
                   py::arg("rates"), py::arg("is_calls"),
                   py::arg("divs"),
                   "Batch IV calculation for multiple options");
}


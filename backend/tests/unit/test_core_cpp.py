"""Unit tests for C++ core module."""
import sys
sys.path.insert(0, 'backend/app/services')

import pytest
import core_cpp


def test_add():
    """Test C++ add function."""
    assert core_cpp.add(1.0, 2.0) == 3.0
    assert core_cpp.add(-5.5, 3.3) == pytest.approx(-2.2)
    assert core_cpp.add(0, 0) == 0


def test_greet():
    """Test C++ greet function."""
    greeting = core_cpp.greet("Alice")
    assert "Hello from C++" in greeting
    assert "Alice" in greeting


def test_add_large_numbers():
    """Test with large numbers."""
    result = core_cpp.add(1e10, 2e10)
    assert result == pytest.approx(3e10)

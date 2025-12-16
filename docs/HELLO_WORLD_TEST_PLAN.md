# Hello World Test - C++/Python Integration

**Purpose:** Verify the complete build pipeline works before implementing Monte Carlo

**Estimated Time:** 15-20 minutes

---

## What We're Building

A simple C++ function that adds two numbers, exposed to Python via Pybind11.

```
Python → Pybind11 Bindings → C++ Function → Return to Python
```

---

## Directory Structure

```
backend/
├── core/                          # NEW - C++ source code
│   ├── CMakeLists.txt            # Build configuration
│   ├── src/
│   │   └── hello.cpp             # C++ implementation
│   ├── include/
│   │   └── hello.h               # C++ header
│   └── bindings/
│       └── python_bindings.cpp   # Pybind11 bindings
└── build/                         # NEW - CMake build output
```

---

## Step 1: Create Directory Structure (2 minutes)

```powershell
cd g:\quant\backend
mkdir core\src
mkdir core\include
mkdir core\bindings
mkdir build
```

---

## Step 2: Write C++ Header (2 minutes)

**File:** `backend/core/include/hello.h`

```cpp
#ifndef HELLO_H
#define HELLO_H

namespace hello {
    // Simple function to add two numbers
    double add(double a, double b);
    
    // Test function that returns a greeting
    const char* greet(const char* name);
}

#endif // HELLO_H
```

---

## Step 3: Write C++ Implementation (2 minutes)

**File:** `backend/core/src/hello.cpp`

```cpp
#include "hello.h"
#include <string>

namespace hello {
    double add(double a, double b) {
        return a + b;
    }
    
    const char* greet(const char* name) {
        static std::string result;
        result = "Hello from C++, " + std::string(name) + "!";
        return result.c_str();
    }
}
```

---

## Step 4: Write Pybind11 Bindings (3 minutes)

**File:** `backend/core/bindings/python_bindings.cpp`

```cpp
#include <pybind11/pybind11.h>
#include "hello.h"

namespace py = pybind11;

PYBIND11_MODULE(core_cpp, m) {
    m.doc() = "Hello World C++ module with Pybind11";
    
    m.def("add", &hello::add, 
          py::arg("a"), py::arg("b"),
          "Add two numbers");
    
    m.def("greet", &hello::greet,
          py::arg("name"),
          "Greet someone from C++");
}
```

---

## Step 5: Write CMakeLists.txt (5 minutes)

**File:** `backend/core/CMakeLists.txt`

```cmake
cmake_minimum_required(VERSION 3.15)
project(QuantCore)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Python and Pybind11
find_package(Python COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

# Include Eigen (header-only)
set(EIGEN3_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../eigen-3.4.0")
include_directories(${EIGEN3_INCLUDE_DIR})

# Include our headers
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

# Create the Python module
pybind11_add_module(core_cpp
    bindings/python_bindings.cpp
    src/hello.cpp
)

# Link libraries
target_link_libraries(core_cpp PRIVATE)

# Installation
install(TARGETS core_cpp DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/../app/services)
```

---

## Step 6: Configure CMake (3 minutes)

**Important:** Initialize Visual Studio environment first!

```powershell
# Initialize VS environment
& "C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\Tools\Launch-VsDevShell.ps1" -Arch amd64

# Navigate to build directory
cd g:\quant\backend\build

# Configure CMake
cmake -G "Visual Studio 17 2022" -A x64 `
  -DCMAKE_BUILD_TYPE=Release `
  -Dpybind11_DIR="G:\quant\backend\.venv\Lib\site-packages\pybind11\share\cmake\pybind11" `
  ..\core
```

---

## Step 7: Build the Project (2 minutes)

```powershell
# Build in Release mode
cmake --build . --config Release

# Install to Python path
cmake --install . --config Release
```

Expected output:
```
Building Custom Rule...
hello.cpp
python_bindings.cpp
core_cpp.vcxproj -> G:\quant\backend\build\Release\core_cpp.cp310-win_amd64.pyd
Install configuration: "Release"
-- Installing: G:\quant\backend\app\services\core_cpp.cp310-win_amd64.pyd
```

---

## Step 8: Test in Python (3 minutes)

```powershell
cd g:\quant\backend
.\.venv\Scripts\Activate.ps1

python -c "
import sys
sys.path.insert(0, 'app/services')
import core_cpp

# Test add function
result = core_cpp.add(5.5, 3.3)
print(f'5.5 + 3.3 = {result}')
assert abs(result - 8.8) < 1e-10, 'Addition failed!'

# Test greet function
greeting = core_cpp.greet('Developer')
print(greeting)
assert 'Hello from C++' in greeting, 'Greet failed!'

print('\n✅ All tests passed! C++/Python integration works!')
"
```

Expected output:
```
5.5 + 3.3 = 8.8
Hello from C++, Developer!

✅ All tests passed! C++/Python integration works!
```

---

## Step 9: Write Python Unit Test (2 minutes)

**File:** `backend/tests/unit/test_core_cpp.py`

```python
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
```

Run tests:
```powershell
cd g:\quant\backend
pytest tests/unit/test_core_cpp.py -v
```

---

## Troubleshooting

### Issue: "cl: command not found"
**Solution:** Run Visual Studio Developer PowerShell setup:
```powershell
& "C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\Tools\Launch-VsDevShell.ps1" -Arch amd64
```

### Issue: "Could not find pybind11"
**Solution:** Specify pybind11 path explicitly:
```powershell
cmake -Dpybind11_DIR="G:\quant\backend\.venv\Lib\site-packages\pybind11\share\cmake\pybind11" ..\core
```

### Issue: "Cannot find Eigen"
**Solution:** Verify path in CMakeLists.txt:
```cmake
set(EIGEN3_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../eigen-3.4.0")
```

### Issue: "ImportError: DLL load failed"
**Solution:** 
- Ensure you're using the correct Python from venv
- Check that the .pyd file exists in `app/services/`
- Try rebuilding in Release mode (not Debug)

---

## Success Criteria

✅ CMake configures without errors  
✅ C++ code compiles successfully  
✅ `.pyd` file generated in build directory  
✅ Python can import `core_cpp` module  
✅ `core_cpp.add()` returns correct results  
✅ `core_cpp.greet()` returns correct string  
✅ Unit tests pass  

---

## Next Steps After Success

Once Hello World works, we'll implement the Monte Carlo simulator:

1. **Replace** `hello.cpp` with `monte_carlo.cpp`
2. **Add** Eigen matrix operations
3. **Add** OpenMP parallelization
4. **Create** Python service wrapper
5. **Add** FastAPI endpoint
6. **Write** comprehensive tests
7. **Benchmark** C++ vs pure Python (expect 10-100x speedup)

**Estimated time for Monte Carlo:** 4-6 hours

---

## Key Takeaways

This Hello World test verifies:
- ✅ MSVC compiler works
- ✅ CMake build system configured correctly
- ✅ Pybind11 bindings work
- ✅ Python can import C++ modules
- ✅ Data passes correctly between Python ↔ C++
- ✅ Development workflow established

**Once this works, you have a proven template for all future C++ modules!**

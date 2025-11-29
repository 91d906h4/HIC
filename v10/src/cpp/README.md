# HIC C++ VM - Build Instructions

## Prerequisites

- CMake 3.10 or higher
- C++17 compatible compiler (GCC 7+, Clang 5+, MSVC 2017+)
- Python 3.x development headers (optional, for Python module support)

## Building

### Windows (MinGW / g++)

If you have MinGW installed (g++), you can compile directly without CMake:

```powershell
cd src/cpp
g++ -std=c++17 -o hic_vm.exe value.cpp vm.cpp vm_ops.cpp main.cpp
```

### Windows (Visual Studio / CMake)

```powershell
cd src/cpp
mkdir build
cd build
cmake ..
cmake --build . --config Release
```

### Linux/Mac

```bash
cd src/cpp
mkdir build
cd build
cmake ..
make
```

## Running

```bash
# From src/cpp directory
.\hic_vm.exe ..\..\test\complete_demo.asm
```

## Build Options

### Disable Python Support

```bash
cmake .. -DENABLE_PYTHON=OFF
```

### Debug Build

```bash
cmake .. -DCMAKE_BUILD_TYPE=Debug
```

## Testing

Run the complete demo:
```bash
# Compile with Python compiler
cd src
python compiler.py ../test/complete_demo.src

# Run with C++ VM
cd cpp/build
./bin/hic_vm ../../test/complete_demo.asm
```

## Performance Comparison

To compare C++ vs Python VM:

```bash
# Python VM
time python src/vm.py test/complete_demo.asm

# C++ VM
time src/cpp/build/bin/hic_vm test/complete_demo.asm
```

Expected speedup: 10-50x faster

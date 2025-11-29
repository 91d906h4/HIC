# Build and Test Script for C++ VM

## Quick Start

```bash
# 1. Build the C++ VM
cd src/cpp
mkdir build
cd build
cmake ..
cmake --build . --config Release

# 2. Compile a test program
cd ../../..
python src/compiler.py test/simple_test.src

# 3. Run with C++ VM
src/cpp/build/bin/hic_vm test/simple_test.asm

# Or on Windows:
src\cpp\build\bin\Release\hic_vm.exe test\simple_test.asm
```

## Testing Phases

### Phase 1: Core VM (No Python)
```bash
python src/compiler.py test/simple_test.src
src/cpp/build/bin/hic_vm test/simple_test.asm
```

### Phase 2: With Python Modules
```bash
python src/compiler.py test/complete_demo.src
src/cpp/build/bin/hic_vm test/complete_demo.asm
```

## Performance Benchmark

```bash
# Python VM
time python src/vm.py test/simple_test.asm

# C++ VM
time src/cpp/build/bin/hic_vm test/simple_test.asm
```

## Troubleshooting

### Python Not Found
If CMake can't find Python:
```bash
cmake .. -DPython3_ROOT_DIR="C:/Python39"
```

### Build Without Python
```bash
cmake .. -DENABLE_PYTHON=OFF
```

### Windows: Missing DLLs
Copy Python DLL to build directory or add Python to PATH.

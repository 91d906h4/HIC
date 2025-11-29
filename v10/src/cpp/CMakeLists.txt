cmake_minimum_required(VERSION 3.10)
project(HIC_VM)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Source files
set(SOURCES
    value.cpp
    vm.cpp
    vm_ops.cpp
    main.cpp
)

# Add Python bridge if enabled
if(ENABLE_PYTHON)
    list(APPEND SOURCES python_bridge.cpp)
endif()

# Create executable
add_executable(hic_vm ${SOURCES})

# Optional: Python support
option(ENABLE_PYTHON "Enable Python module support" ON)

if(ENABLE_PYTHON)
    find_package(Python3 COMPONENTS Development)
    if(Python3_FOUND)
        target_include_directories(hic_vm PRIVATE ${Python3_INCLUDE_DIRS})
        target_link_libraries(hic_vm ${Python3_LIBRARIES})
        target_compile_definitions(hic_vm PRIVATE PYTHON_SUPPORT)
        message(STATUS "Python support enabled")
    else()
        message(WARNING "Python3 not found, building without Python support")
    endif()
endif()

# Compiler warnings
if(MSVC)
    target_compile_options(hic_vm PRIVATE /W4)
else()
    target_compile_options(hic_vm PRIVATE -Wall -Wextra -pedantic)
endif()

# Output directory
set_target_properties(hic_vm PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)

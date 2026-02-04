# CMake configuration for TankDynamics project
# This is the root CMakeLists.txt that orchestrates the entire build system

# Specify minimum CMake version required and project name/language
# VERSION 3.20 provides FetchContent and modern CMake features
cmake_minimum_required(VERSION 3.20)
project(TankDynamics LANGUAGES CXX)

# ============================================================================
# PROJECT CONFIGURATION
# ============================================================================

# Define the main library target name as a variable for reusability
# This allows easy renaming across the entire CMake configuration
set(CORE_LIB tank_sim_core)

# C++ Standard Configuration
# Set as variable to allow easy customization across projects
# C++17 provides modern features like std::optional, std::variant
set(CMAKE_CXX_STANDARD 17 CACHE STRING "C++ standard version")
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Generate compile_commands.json for clangd and other language servers
# This file is used by clangd to understand project structure, include paths, and compilation flags
# CMake will place it at: build/compile_commands.json
# Create a symlink from project root: ln -sf build/compile_commands.json compile_commands.json
# This allows clangd to find it automatically when looking in the project root
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# ============================================================================
# PYTHON DETECTION
# ============================================================================

# Find Python for pybind11 bindings
# Development.Module is sufficient for building extension modules
find_package(Python3 REQUIRED COMPONENTS Interpreter Development.Module)

# ============================================================================
# DEPENDENCY MANAGEMENT
# ============================================================================

# Include FetchContent module for downloading dependencies from Git repositories
# This allows automatic downloading and building of dependencies without requiring
# pre-installation on the system
include(FetchContent)

# ============================================================================
# EIGEN SPECIAL HANDLING
# ============================================================================
# IMPORTANT: Eigen is fetched manually to prevent test pollution
#
# Problem: Eigen's CMakeLists.txt registers 900+ tests via add_test() when
# processed by add_subdirectory(). These tests pollute our CTest suite even
# though the test executables aren't built.
#
# Solution: Use FetchContent_Populate() instead of FetchContent_MakeAvailable()
# This downloads Eigen but doesn't process its CMakeLists.txt. We manually
# create an INTERFACE IMPORTED target with just the include path.
#
# Why this works:
# - Eigen is header-only, so it only needs include directories (no compilation)
# - We don't need Eigen's CMake targets, build options, or tests
# - Creating INTERFACE IMPORTED gives us a proper CMake target for linking
#
# Trade-off: We lose Eigen's CMake configuration features, but for this project
# we only need the headers, making this approach simpler and cleaner.
#
# See docs/CTEST_FIX.md for detailed explanation.
# ============================================================================

FetchContent_Declare(
    Eigen3
    GIT_REPOSITORY https://gitlab.com/libeigen/eigen.git
    GIT_TAG        3.4.0
)

# Fetch Eigen source without processing its CMakeLists.txt
FetchContent_GetProperties(Eigen3)
if(NOT eigen3_POPULATED)
    FetchContent_Populate(Eigen3)
    # Create INTERFACE IMPORTED target manually (no add_subdirectory!)
    add_library(Eigen3::Eigen INTERFACE IMPORTED GLOBAL)
    target_include_directories(Eigen3::Eigen INTERFACE ${eigen3_SOURCE_DIR})
endif()

# ============================================================================
# GOOGLETEST STANDARD FETCH
# ============================================================================
# GoogleTest is fetched normally because it respects BUILD_TESTING and doesn't
# pollute the test suite when BUILD_TESTING is OFF during FetchContent.

FetchContent_Declare(
    GoogleTest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG        v1.14.0
)

FetchContent_MakeAvailable(GoogleTest)

# ============================================================================
# PYBIND11 FETCH (for Python bindings)
# ============================================================================

FetchContent_Declare(
    pybind11
    GIT_REPOSITORY https://github.com/pybind/pybind11.git
    GIT_TAG        v2.11.1
)
FetchContent_MakeAvailable(pybind11)

# System dependencies - searched for via pkg-config or system paths
# List of required system packages and their find_package() names
set(SYSTEM_DEPS GSL)

# GSL (GNU Scientific Library) - numerical computation library
# Unlike Eigen and GoogleTest, GSL must be installed system-wide
# find_package() searches for pre-installed GSL
# If not found, provide helpful error message with installation instructions for common distros
find_package(GSL REQUIRED)
if(NOT GSL_FOUND)
    message(FATAL_ERROR "GSL not found. Please install it via your system package manager:
    - On Ubuntu: sudo apt-get install libgsl-dev
    - On Arch: sudo pacman -S gsl")
endif()

# ============================================================================
# LIBRARY TARGET DEFINITION
# ============================================================================

# Create the main library target using CORE_LIB variable
# This is now a compiled library (not INTERFACE) since we have implementation files
# Source files are added in src/CMakeLists.txt via target_sources()
add_library(${CORE_LIB})

# Link external libraries to the core library
# PUBLIC keyword means these dependencies are required by both the library and its consumers
target_link_libraries(${CORE_LIB} PUBLIC
    Eigen3::Eigen          # Linear algebra library
    GSL::gsl               # GSL main library
    GSL::gslcblas          # GSL BLAS library (Basic Linear Algebra Subprograms)
)

# Specify include directories for the core library
# BUILD_INTERFACE: used when building this project (includes are in src/ directory)
# INSTALL_INTERFACE: used when this library is installed and used by external projects
# PUBLIC keyword means consumers of the library also get these include paths
target_include_directories(${CORE_LIB} PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src>
    $<INSTALL_INTERFACE:include>
)

# ============================================================================
# SUBDIRECTORIES
# ============================================================================

# Add src/ subdirectory - contains implementation files
# The src/CMakeLists.txt will add actual source files to ${CORE_LIB} library
add_subdirectory(src)

# ============================================================================
# TESTING CONFIGURATION - TIMING IS CRITICAL
# ============================================================================
# IMPORTANT: enable_testing() must be called at this exact point in the build
#
# Why here and not earlier?
# - If called BEFORE FetchContent: Eigen's CMakeLists.txt will register 900+ tests
#   when add_subdirectory() is processed, polluting our test suite
# - By manually fetching Eigen (above), we skip its CMakeLists.txt entirely
# - Calling enable_testing() here ensures only OUR tests are registered
#
# Why here and not later?
# - Must be called BEFORE add_subdirectory(tests/) so the tests/ CMakeLists.txt
#   can use add_test() and gtest_discover_tests()
#
# Result: CTest discovers exactly our 17 tests, nothing more.
# ============================================================================

enable_testing()

# Add tests/ subdirectory - contains unit tests
# The tests/CMakeLists.txt will create test executables
add_subdirectory(tests)

# Add bindings/ subdirectory - contains language bindings (e.g., Python via pybind11)
# Currently empty, will be populated in Phase 2
add_subdirectory(bindings)

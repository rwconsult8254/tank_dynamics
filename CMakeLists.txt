# CMake configuration for TankDynamics project
# This is the root CMakeLists.txt that orchestrates the entire build system

# Specify minimum CMake version required and project name/language
# VERSION 3.20 provides FetchContent and modern CMake features
cmake_minimum_required(VERSION 3.20)
project(TankDynamics LANGUAGES CXX)

# Generate compile_commands.json for clangd and other language servers
# This file is used by clangd to understand project structure, include paths, and compilation flags
# CMake will place it at: build/compile_commands.json
# Create a symlink from project root: ln -sf build/compile_commands.json compile_commands.json
# This allows clangd to find it automatically when looking in the project root
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# C++ Standard Configuration
# Set C++ standard to 17 (required for modern features like std::optional, std::variant)
set(CMAKE_CXX_STANDARD 17)
# Ensure C++17 is required, not just preferred (will fail if compiler doesn't support it)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
# Disable compiler-specific extensions (use standard C++ only, improves portability)
set(CMAKE_CXX_EXTENSIONS OFF)

# ============================================================================
# DEPENDENCY MANAGEMENT
# ============================================================================

# Include FetchContent module for downloading dependencies from Git repositories
# This allows automatic downloading and building of dependencies without requiring
# pre-installation on the system
include(FetchContent)

# Declare Eigen3 dependency - linear algebra library
# Version 3.4.0 provides header-only matrix operations and vector math
FetchContent_Declare(
    Eigen3
    GIT_REPOSITORY https://gitlab.com/libeigen/eigen.git
    GIT_TAG        3.4.0
)

# Declare GoogleTest dependency - unit testing framework
# Version 1.14.0 provides gtest and gmock libraries
FetchContent_Declare(
    GoogleTest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG        v1.14.0
)

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

# Download and make available all FetchContent declared dependencies
# This must be called after all FetchContent_Declare() calls
FetchContent_MakeAvailable(Eigen3 GoogleTest)

# ============================================================================
# LIBRARY TARGET DEFINITION
# ============================================================================

# Create the main library target named "tank_sim_core"
# INTERFACE keyword means this is a header-only library (no source files compiled here)
# Actual implementation files are added in src/CMakeLists.txt via target_sources()
add_library(tank_sim_core INTERFACE)

# Link external libraries to tank_sim_core
# INTERFACE keyword means these dependencies are required by consumers of tank_sim_core
# Any executable or library that links to tank_sim_core will also link to these
target_link_libraries(tank_sim_core INTERFACE
    Eigen3::Eigen          # Linear algebra library
    GSL::gsl               # GSL main library
    GSL::gslcblas          # GSL BLAS library (Basic Linear Algebra Subprograms)
)

# Specify include directories for tank_sim_core
# BUILD_INTERFACE: used when building this project (includes are in src/ directory)
# INSTALL_INTERFACE: used when this library is installed and used by external projects
target_include_directories(tank_sim_core INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src>
    $<INSTALL_INTERFACE:include>
)

# ============================================================================
# SUBDIRECTORIES
# ============================================================================

# Add src/ subdirectory - contains implementation files
# The src/CMakeLists.txt will add actual source files to tank_sim_core library
add_subdirectory(src)

# Add tests/ subdirectory - contains unit tests
# The tests/CMakeLists.txt will create test executables
add_subdirectory(tests)

# Add bindings/ subdirectory - contains language bindings (e.g., Python via pybind11)
# Currently empty, will be populated in Phase 2
add_subdirectory(bindings)

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
# DEPENDENCY MANAGEMENT
# ============================================================================

# Include FetchContent module for downloading dependencies from Git repositories
# This allows automatic downloading and building of dependencies without requiring
# pre-installation on the system
include(FetchContent)

# List of FetchContent dependencies to make available
set(FETCHCONTENT_DEPS Eigen3 GoogleTest)

# Declare Eigen3 dependency - linear algebra library
# Version 3.4.0 provides header-only matrix operations and vector math
# Note: We manually fetch Eigen to prevent its tests from polluting our test suite
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

# Fetch Eigen manually without adding its subdirectory to prevent test pollution
FetchContent_GetProperties(Eigen3)
if(NOT eigen3_POPULATED)
    FetchContent_Populate(Eigen3)
    # Do NOT call add_subdirectory - just make the target available
    add_library(Eigen3::Eigen INTERFACE IMPORTED GLOBAL)
    target_include_directories(Eigen3::Eigen INTERFACE ${eigen3_SOURCE_DIR})
endif()

# Fetch GoogleTest normally (it respects BUILD_TESTING)
FetchContent_MakeAvailable(GoogleTest)

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

# Note: enable_testing() is called AFTER dependencies are fetched
# to prevent Eigen from registering its own tests

# Add src/ subdirectory - contains implementation files
# The src/CMakeLists.txt will add actual source files to ${CORE_LIB} library
add_subdirectory(src)

# Enable testing NOW (after dependencies fetched, before tests/ directory)
# This prevents Eigen tests from being registered while allowing our tests
enable_testing()

# Add tests/ subdirectory - contains unit tests
# The tests/CMakeLists.txt will create test executables
add_subdirectory(tests)

# Add bindings/ subdirectory - contains language bindings (e.g., Python via pybind11)
# Currently empty, will be populated in Phase 2
add_subdirectory(bindings)

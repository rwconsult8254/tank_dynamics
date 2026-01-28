# CMakeLists.txt for src/ directory
# This file adds source files to the tank_sim_core library target
# that was already defined in the root CMakeLists.txt

# Add source files to the tank_sim_core target
# PRIVATE keyword means these files are implementation details, not part of the public interface
# target_sources() is preferred over add_library(lib STATIC file.cpp) because:
#   - The target is already defined in the parent scope (root CMakeLists.txt)
#   - We only need to add source files to the existing target
#   - It's cleaner for multi-level CMake projects with subdirectories
# Note: Using placeholder file initially; will be replaced with tank_model.cpp in Task 2
target_sources(tank_sim_core PRIVATE
    tank_model.cpp
)

# Note: Header files (tank_model.h) are not listed here because:
#   - CMake doesn't require headers to be listed (they're found via #include)
#   - Headers are found via target_include_directories() set in root CMakeLists.txt
#   - Some developers list headers for IDE support, but it's optional

# CMakeLists.txt for bindings/ directory
# This directory contains language bindings for the C++ library

# Python bindings will be added in Phase 2 using pybind11
# pybind11 is a lightweight header-only library that creates Python C++ extension modules
#
# When implementing Python bindings:
# 1. Declare pybind11 as a FetchContent dependency in root CMakeLists.txt
# 2. Create pybind11 module with pybind11_add_module()
# 3. Bind C++ classes and functions to Python
# 4. Link against tank_sim_core library
#
# Example structure (to be added later):
# pybind11_add_module(tank_sim_py tank_sim_py.cpp)
# target_link_libraries(tank_sim_py PRIVATE tank_sim_core)

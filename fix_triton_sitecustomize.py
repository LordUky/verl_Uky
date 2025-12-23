"""
Sitecustomize to fix Triton compilation in vast.ai
This file will be automatically imported by ALL Python processes
"""
import os
import sys

# DO NOT add stubs to LD_LIBRARY_PATH - it breaks CUDA runtime!
# The GCC wrapper (/usr/local/bin/gcc-wrapper) handles compilation-time linking
# No sitecustomize changes needed - just placeholder to prevent errors

#!/usr/bin/env python3
"""Test if sitecustomize works with multiprocessing spawn (Ray's mode)"""
import multiprocessing
import os
import sys

def test_in_worker():
    """Test function that runs in worker process"""
    ld_path = os.environ.get("LD_LIBRARY_PATH", "NOT SET")
    has_stubs = "/usr/local/cuda/lib64/stubs" in ld_path

    # Try to initialize Triton
    try:
        from triton.backends.nvidia.driver import CudaUtils
        triton_ok = True
        error = None
    except Exception as e:
        triton_ok = False
        error = str(e)

    return {
        "LD_LIBRARY_PATH": ld_path,
        "has_stubs": has_stubs,
        "triton_ok": triton_ok,
        "error": error
    }

if __name__ == "__main__":
    # Test with spawn method (same as Ray)
    ctx = multiprocessing.get_context("spawn")
    with ctx.Pool(1) as pool:
        result = pool.apply(test_in_worker)

    print("=== Worker Process Test (spawn mode) ===")
    print(f"LD_LIBRARY_PATH: {result['LD_LIBRARY_PATH'][:100]}...")
    print(f"Has CUDA stubs: {result['has_stubs']}")
    print(f"Triton initialization: {'✓ OK' if result['triton_ok'] else '✗ FAILED'}")
    if result['error']:
        print(f"Error: {result['error'][:200]}")

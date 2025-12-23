"""
Fix Triton compilation issues by patching environment before vLLM loads
Run this BEFORE importing vllm
"""
import os
import sys

# Add CUDA stubs to library path to fix -lcuda linking
cuda_stubs = "/usr/local/cuda/lib64/stubs"
if os.path.exists(cuda_stubs):
    current_ld_path = os.environ.get("LD_LIBRARY_PATH", "")
    if cuda_stubs not in current_ld_path:
        os.environ["LD_LIBRARY_PATH"] = f"{cuda_stubs}:{current_ld_path}"
        print(f"[fix_triton] Added {cuda_stubs} to LD_LIBRARY_PATH")

# Disable Triton completely
os.environ["VLLM_USE_TRITON_FLASH_ATTN"] = "0"
os.environ["VLLM_ATTENTION_BACKEND"] = "TORCH_SDPA"
os.environ["TRITON_CACHE_DIR"] = "/tmp/triton_cache"

print("[fix_triton] Triton workarounds applied")
print(f"[fix_triton] LD_LIBRARY_PATH={os.environ.get('LD_LIBRARY_PATH', '')[:100]}...")

#!/usr/bin/env python3
"""
分阶段测试各个组件，无需运行完整训练
快速定位问题在哪个环节
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("=" * 60)
print("组件测试工具 - 快速定位问题")
print("=" * 60)

# Test 1: Import git_ignore
print("\n[1/6] 测试配置文件...")
try:
    from git_ignore import QWEN_VL_3B_BASE_STR, DATA_OUTPUT_DIR_STR
    print(f"  ✓ 配置文件正常")
    print(f"    模型路径: {QWEN_VL_3B_BASE_STR}")
    print(f"    数据路径: {DATA_OUTPUT_DIR_STR}")
except Exception as e:
    print(f"  ✗ 配置文件错误: {e}")
    sys.exit(1)

# Test 2: Check data files
print("\n[2/6] 测试数据文件...")
import pandas as pd
train_path = os.path.join(DATA_OUTPUT_DIR_STR, "train.parquet")
if os.path.exists(train_path):
    df = pd.read_parquet(train_path)
    print(f"  ✓ 数据文件存在: {len(df)} 样本")
    print(f"    列: {df.columns.tolist()}")
else:
    print(f"  ✗ 数据文件不存在: {train_path}")

# Test 3: Import PyTorch and CUDA
print("\n[3/6] 测试 PyTorch 和 CUDA...")
try:
    import torch
    print(f"  ✓ PyTorch version: {torch.__version__}")
    print(f"  ✓ CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"  ✓ CUDA version: {torch.version.cuda}")
        print(f"  ✓ GPU count: {torch.cuda.device_count()}")
        print(f"  ✓ GPU name: {torch.cuda.get_device_name(0)}")
except Exception as e:
    print(f"  ✗ PyTorch/CUDA 错误: {e}")

# Test 4: Import vLLM
print("\n[4/6] 测试 vLLM...")
try:
    import vllm
    print(f"  ✓ vLLM version: {vllm.__version__}")
except Exception as e:
    print(f"  ✗ vLLM 导入错误: {e}")

# Test 5: Import verl
print("\n[5/6] 测试 verl...")
try:
    import verl
    print(f"  ✓ verl 导入成功")
except Exception as e:
    print(f"  ✗ verl 导入错误: {e}")

# Test 6: Test Ray
print("\n[6/6] 测试 Ray...")
try:
    import ray
    print(f"  ✓ Ray version: {ray.__version__}")
    # Don't actually init ray, just test import
    print(f"  ✓ Ray 导入成功（未初始化）")
except Exception as e:
    print(f"  ✗ Ray 错误: {e}")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
print("\n如果所有测试都通过，可以运行:")
print("  bash examples/grpo_trainer/run_qwen2_5_vl-3b_fake_dataset_DEBUG.sh")

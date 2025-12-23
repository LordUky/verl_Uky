#!/usr/bin/env python3
"""
创建一个超小的测试数据集（只有2-4个样本）
用于快速验证训练流程，无需等待完整数据加载
"""

import pandas as pd
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from git_ignore import DATA_OUTPUT_DIR_STR
    data_dir = DATA_OUTPUT_DIR_STR
except ImportError:
    print("ERROR: Cannot import from git_ignore.py")
    data_dir = "."

# Load original data
train_path = os.path.join(data_dir, "train.parquet")
if not os.path.exists(train_path):
    print(f"ERROR: {train_path} not found!")
    print("Please run data preprocessing first.")
    sys.exit(1)

print(f"Loading data from {train_path}")
df = pd.read_parquet(train_path)

print(f"Original dataset: {len(df)} samples")

# Take only first 2 samples
tiny_df = df.head(2)

# Save to new file
tiny_path = os.path.join(data_dir, "train_TINY.parquet")
tiny_df.to_parquet(tiny_path)

print(f"Created tiny dataset: {tiny_path}")
print(f"Samples: {len(tiny_df)}")
print("\n使用方法:")
print(f"  修改训练脚本中的 data.train_files={tiny_path}")
print(f"  或者运行: bash examples/grpo_trainer/run_qwen2_5_vl-3b_fake_dataset_DEBUG.sh")

#!/bin/bash
# Quick start script for training Qwen2.5-VL-3B on fake VLM dataset
# 一键启动脚本 - 自动完成数据预处理和训练

set -e  # Exit on error

echo "========================================"
echo "Qwen2.5-VL-3B 训练 - 快速启动脚本"
echo "========================================"
echo ""

# Get project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Load paths from git_ignore.py
if [ -f "$PROJECT_ROOT/git_ignore.py" ]; then
    JSON_PATH=$(python3 -c "import sys; sys.path.insert(0, '$PROJECT_ROOT'); from git_ignore import FAKE_DATASET_JSON_STR; print(FAKE_DATASET_JSON_STR)")
    DATA_DIR=$(python3 -c "import sys; sys.path.insert(0, '$PROJECT_ROOT'); from git_ignore import DATA_OUTPUT_DIR_STR; print(DATA_OUTPUT_DIR_STR)")
else
    echo "ERROR: git_ignore.py not found."
    echo "Please run: cp git_ignore.py.example git_ignore.py"
    echo "Then edit git_ignore.py with your actual paths."
    exit 1
fi

ENGINE=${1:-vllm}  # Default to vllm, can pass sglang as argument

echo "Configuration loaded from git_ignore.py:"
echo "  JSON_PATH: $JSON_PATH"
echo "  DATA_DIR: $DATA_DIR"
echo ""

# Step 1: Check if data preprocessing is needed
echo "步骤 1/3: 检查数据..."
if [ -f "$DATA_DIR/train.parquet" ] && [ -f "$DATA_DIR/test.parquet" ]; then
    echo "✓ 数据已存在，跳过预处理"
    echo "  训练集: $DATA_DIR/train.parquet"
    echo "  测试集: $DATA_DIR/test.parquet"

    read -p "是否重新生成数据? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "正在重新生成数据..."
        python examples/data_preprocess/fake_dataset_vlm.py \
            --input_json $JSON_PATH \
            --local_save_dir $DATA_DIR \
            --train_ratio 0.9
    fi
else
    echo "✗ 数据不存在，开始预处理..."
    python examples/data_preprocess/fake_dataset_vlm.py \
        --input_json $JSON_PATH \
        --local_save_dir $DATA_DIR \
        --train_ratio 0.9
fi

echo ""

# Step 2: Validate data
echo "步骤 2/3: 验证数据..."
python -c "
import pandas as pd
import os

data_dir = os.path.expanduser('$DATA_DIR')
train_path = os.path.join(data_dir, 'train.parquet')
test_path = os.path.join(data_dir, 'test.parquet')

if not os.path.exists(train_path):
    print(f'✗ 错误: 训练数据不存在: {train_path}')
    exit(1)

if not os.path.exists(test_path):
    print(f'✗ 错误: 测试数据不存在: {test_path}')
    exit(1)

train_df = pd.read_parquet(train_path)
test_df = pd.read_parquet(test_path)

print(f'✓ 数据验证成功')
print(f'  训练样本数: {len(train_df)}')
print(f'  测试样本数: {len(test_df)}')

# Check required columns
required_cols = ['prompt', 'images', 'reward_model', 'ability']
for col in required_cols:
    if col not in train_df.columns:
        print(f'✗ 错误: 缺少必需列: {col}')
        exit(1)

print(f'✓ 数据格式正确')
print(f'  列: {train_df.columns.tolist()}')
"

if [ $? -ne 0 ]; then
    echo "✗ 数据验证失败，请检查数据格式"
    exit 1
fi

echo ""

# Step 3: Start training
echo "步骤 3/3: 启动训练..."
echo "  引擎: $ENGINE"
echo "  模型: Qwen2.5-VL-3B-Instruct"
echo ""

# Ask for confirmation
read -p "准备开始训练，是否继续? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo "开始训练..."
    echo "提示: 可以用 Ctrl+C 停止训练"
    echo ""

    bash examples/grpo_trainer/run_qwen2_5_vl-3b_fake_dataset.sh $ENGINE
else
    echo "取消训练"
    echo ""
    echo "如需手动启动训练，运行:"
    echo "  bash examples/grpo_trainer/run_qwen2_5_vl-3b_fake_dataset.sh $ENGINE"
fi

echo ""
echo "========================================"
echo "完成!"
echo "========================================"

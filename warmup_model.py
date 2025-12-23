#!/usr/bin/env python3
"""
预热模型 - 让 vLLM 缓存模型权重到共享内存
运行一次后，后续启动会快很多
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from git_ignore import QWEN_VL_3B_BASE_STR

# Find snapshot
snapshot_dir = sorted(os.listdir(QWEN_VL_3B_BASE_STR))[-1]
model_path = os.path.join(QWEN_VL_3B_BASE_STR, snapshot_dir)

print("=" * 60)
print("模型预热工具")
print("=" * 60)
print(f"模型路径: {model_path}")
print("\n正在初始化 vLLM...")
print("这会需要一些时间（2-5分钟），但只需要运行一次")
print("=" * 60)

try:
    from vllm import LLM, SamplingParams

    # 使用最小配置加载模型
    llm = LLM(
        model=model_path,
        trust_remote_code=True,
        gpu_memory_utilization=0.3,
        max_model_len=512,  # 最小长度
        enforce_eager=True,  # 跳过 CUDA graph 编译
        load_format="safetensors",  # 使用快速加载格式
    )

    print("\n✓ 模型加载成功！")
    print("\n测试推理...")

    # 简单推理测试
    prompts = ["Hello, how are you?"]
    sampling_params = SamplingParams(temperature=0.0, max_tokens=10)
    outputs = llm.generate(prompts, sampling_params)

    print("✓ 推理测试成功！")
    print(f"输出: {outputs[0].outputs[0].text}")

    print("\n" + "=" * 60)
    print("预热完成！")
    print("=" * 60)
    print("\n后续训练启动会更快。")
    print("如果还是慢，请使用以下脚本:")
    print("  bash examples/grpo_trainer/run_qwen2_5_vl-3b_fake_dataset_FAST_LOAD.sh")

except Exception as e:
    print(f"\n✗ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

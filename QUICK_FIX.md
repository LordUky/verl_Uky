# ⚡ 快速修复卡片

## 问题：模型加载太慢（几十分钟）

### ✅ 立即解决方案

```bash
cd /root/verl_Uky/verl_Uky

# 方案 1: 快速加载模式（推荐）
bash examples/grpo_trainer/run_qwen2_5_vl-3b_fake_dataset_FAST_LOAD.sh
```

**效果**: 从 30-60 分钟 → 2-5 分钟（**10-20倍加速**）

---

## 三种模式对比

| 脚本 | 启动时间 | 训练时长 | 用途 |
|------|---------|---------|------|
| `run_qwen2_5_vl-3b_fake_dataset.sh` | 30-60min | 数小时 | 完整训练 |
| `run_qwen2_5_vl-3b_fake_dataset_FAST_LOAD.sh` | 2-5min | 1-2小时 | 开发/DEBUG ⭐ |
| `run_qwen2_5_vl-3b_fake_dataset_DEBUG.sh` | 2min | 5min | 快速验证 |

---

## 关键优化参数

只需添加这 4 行到任何训练脚本：

```bash
actor_rollout_ref.rollout.load_format=safetensors      # ⚡ 快速加载
actor_rollout_ref.rollout.enforce_eager=True           # ⚡ 跳过编译
actor_rollout_ref.rollout.gpu_memory_utilization=0.4   # ⚡ 减少分配
data.max_prompt_length=2048                            # ⚡ 减小开销
```

---

## 工具箱

```bash
# 测试环境（10秒）
python3 test_components.py

# 预热模型（一次性，2-5分钟）
python3 warmup_model.py

# DEBUG 模式（2-5分钟完整流程）
bash examples/grpo_trainer/run_qwen2_5_vl-3b_fake_dataset_DEBUG.sh

# 快速加载模式（2-5分钟启动，正常训练）
bash examples/grpo_trainer/run_qwen2_5_vl-3b_fake_dataset_FAST_LOAD.sh

# 完整文档
cat DEBUG_TIPS.md
```

---

## 记住

> **在 DEBUG 时，永远不要等超过 5 分钟！**

如果启动超过 5 分钟，立即 Ctrl+C，改用快速加载模式。

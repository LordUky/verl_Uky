# 🚀 调试技巧 - 快速验证训练流程

每次 debug 都要等很久？试试这些技巧！

## 📋 快速索引

1. [超快验证](#1-超快验证-30秒) - 30秒内知道代码能否跑
2. [分阶段测试](#2-分阶段测试) - 快速定位问题
3. [减少等待时间](#3-减少等待时间) - 优化配置
4. [加速模型加载](#4-加速模型加载-关键) - 从几十分钟降到2-5分钟 ⭐
5. [错误处理](#5-常见错误速查)

---

## 1️⃣ 超快验证 (30秒)

### 方法 A: 测试组件（最快）
```bash
# 只测试导入和配置，不启动训练
python3 test_components.py
```
**优点**:
- ⚡ 5-10秒完成
- 🎯 快速发现配置/环境问题
- 📊 显示系统状态

### 方法 B: DEBUG模式训练
```bash
# 极小数据集 + 1个epoch，2-3分钟完成
bash examples/grpo_trainer/run_qwen2_5_vl-3b_fake_dataset_DEBUG.sh
```
**优点**:
- ⚡ 比正常训练快 10-20 倍
- ✅ 验证完整训练流程
- 🔍 快速发现运行时错误

**配置差异对比**:
| 参数 | 正常模式 | DEBUG模式 | 加速比 |
|------|---------|----------|--------|
| batch_size | 4 | 1 | 4x |
| max_prompt_length | 10240 | 512 | 20x |
| max_response_length | 512 | 64 | 8x |
| total_epochs | 20 | 1 | 20x |
| 预估总时间 | 数小时 | 2-5分钟 | ~50x |

---

## 2️⃣ 分阶段测试

按顺序测试各个环节，快速定位问题：

### Step 1: 环境检查 (5秒)
```bash
python3 test_components.py
```

### Step 2: 数据检查 (10秒)
```bash
python3 -c "
import pandas as pd
import sys
sys.path.insert(0, '.')
from git_ignore import DATA_OUTPUT_DIR_STR
df = pd.read_parquet(f'{DATA_OUTPUT_DIR_STR}/train.parquet')
print(f'数据样本数: {len(df)}')
print(f'列: {df.columns.tolist()}')
print(df.head(1))
"
```

### Step 3: 模型加载测试 (30秒)
```bash
python3 -c "
import torch
from transformers import AutoTokenizer, AutoProcessor
import sys
sys.path.insert(0, '.')
from git_ignore import QWEN_VL_3B_BASE_STR
import os

snapshot_dir = sorted(os.listdir(QWEN_VL_3B_BASE_STR))[-1]
model_path = os.path.join(QWEN_VL_3B_BASE_STR, snapshot_dir)

print(f'加载模型: {model_path}')
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)
print('✓ 模型加载成功')
"
```

### Step 4: vLLM 引擎测试 (1分钟)
```bash
# 测试 vLLM 能否启动（不运行训练）
python3 -c "
from vllm import LLM, SamplingParams
import sys
sys.path.insert(0, '.')
from git_ignore import QWEN_VL_3B_BASE_STR
import os

snapshot_dir = sorted(os.listdir(QWEN_VL_3B_BASE_STR))[-1]
model_path = os.path.join(QWEN_VL_3B_BASE_STR, snapshot_dir)

print('测试 vLLM 初始化...')
llm = LLM(
    model=model_path,
    trust_remote_code=True,
    gpu_memory_utilization=0.3,
    max_model_len=512,
    enforce_eager=True
)
print('✓ vLLM 初始化成功')
"
```

### Step 5: 完整训练 (DEBUG模式 2-5分钟)
```bash
bash examples/grpo_trainer/run_qwen2_5_vl-3b_fake_dataset_DEBUG.sh
```

---

## 3️⃣ 减少等待时间

### 技巧 1: 使用 tmux/screen 后台运行
```bash
# 安装 tmux（如果还没有）
apt-get install tmux -y

# 创建会话
tmux new -s training

# 运行训练
bash examples/grpo_trainer/run_qwen2_5_vl-3b_fake_dataset.sh

# 分离会话: Ctrl+B 然后按 D
# 重新连接: tmux attach -t training
```

### 技巧 2: 提前编译 Triton（一次性成本）
```bash
# 预编译 Triton kernels，避免每次训练都编译
export TRITON_CACHE_DIR=/tmp/triton_cache
mkdir -p /tmp/triton_cache

# 第一次运行后，Triton kernels 会被缓存
# 后续运行会快很多
```

### 技巧 3: 使用 Ray Dashboard 监控
```bash
# 启动训练时，Ray 会显示 dashboard URL
# 例如: http://127.0.0.1:8265
# 在浏览器打开可以实时监控进度
```

### 技巧 4: 只测试特定组件
```bash
# 只测试 rollout（不训练）
# 修改配置: trainer.total_epochs=0

# 只测试 reward 计算
# 单独运行 reward model
```

---

## 4️⃣ 加速模型加载 (关键) ⭐

**问题**: 模型加载太慢（几十分钟），还没到训练就卡住了？

### 🎯 根本原因

verl 的默认配置会强制使用 `load_format=auto`，导致每次都要：
1. 从磁盘读取 7GB 模型权重
2. 反序列化模型
3. 传输到 GPU
4. 编译 CUDA kernels

**这在 DEBUG 时完全不必要！**

### ⚡ 解决方案

#### 方案 A: 使用快速加载脚本（推荐）
```bash
# 使用 safetensors 格式 + 优化配置
bash examples/grpo_trainer/run_qwen2_5_vl-3b_fake_dataset_FAST_LOAD.sh
```

**关键优化**:
- `load_format=safetensors` - 使用快速格式（比 auto 快 5-10倍）
- `enforce_eager=True` - 跳过 CUDA graph 编译（节省 5-10 分钟）
- `gpu_memory_utilization=0.4` - 减少内存分配时间
- 减小 `max_prompt_length` 和 `batch_size` - 减少初始化开销

**预计效果**:
```
原来: 30-60 分钟加载
现在: 2-5 分钟加载
加速: 10-20倍
```

#### 方案 B: 预热模型（一次性）
```bash
# 第一次运行，预热模型
python3 warmup_model.py

# 后续训练会自动使用缓存
```

**优点**:
- 只需运行一次
- 后续启动更快
- 适合长期开发

#### 方案 C: DEBUG 模式（最快验证）
```bash
# 极小配置，2-5分钟完成整个流程
bash examples/grpo_trainer/run_qwen2_5_vl-3b_fake_dataset_DEBUG.sh
```

### 📊 加载时间对比

| 配置 | 模型加载 | CUDA编译 | 总启动时间 | 适用场景 |
|------|---------|---------|-----------|---------|
| 默认 (auto) | 20-30min | 10-20min | 30-60min | 生产环境 |
| 快速加载 (safetensors) | 2-5min | 0min | 2-5min | DEBUG/开发 |
| DEBUG 模式 | 2min | 0min | 2min | 快速验证 |
| 预热后 | 1-2min | 0min | 1-2min | 频繁测试 |

### 🔧 手动优化配置

如果要自定义脚本，添加这些参数：

```bash
python3 -m verl.trainer.main_ppo \
    actor_rollout_ref.rollout.load_format=safetensors \  # 关键！
    actor_rollout_ref.rollout.enforce_eager=True \       # 跳过编译
    actor_rollout_ref.rollout.gpu_memory_utilization=0.4 \  # 减少分配时间
    data.max_prompt_length=2048 \                        # 减小长度
    data.train_batch_size=2 \                            # 减小batch
    ... # 其他配置
```

### 💡 专业提示

1. **DEBUG 时永远用 safetensors** - 不要用 auto
2. **启用 enforce_eager** - CUDA graph 编译在 DEBUG 时是浪费时间
3. **减小 max_model_len** - 初始化时会根据这个分配内存
4. **监控加载进度** - 用 `htop` 看 CPU/内存使用，判断卡在哪里

---

## 5️⃣ 常见错误速查

### 错误 1: Triton 编译失败
**症状**: `subprocess.CalledProcessError: Command '['/usr/bin/gcc'...`

**快速修复**:
```bash
# 已在 run_qwen2_5_vl-3b_fake_dataset_DEBUG.sh 中添加
export VLLM_USE_TRITON_FLASH_ATTN=0
export VLLM_ATTENTION_BACKEND=FLASH_ATTN  # 注意：XFORMERS 不是有效值！
```

### 错误 2: OOM (Out of Memory)
**症状**: `CUDA out of memory`

**快速修复**:
```bash
# 减小 batch size 和 max_length
data.train_batch_size=1
data.max_prompt_length=512
actor_rollout_ref.rollout.gpu_memory_utilization=0.2
```

### 错误 3: Ray 启动慢
**症状**: 等待 Ray worker 注册超时

**快速修复**:
```bash
export RAY_num_prestart_python_workers=1
export RAY_worker_register_timeout_seconds=600
```

### 错误 4: 数据加载慢
**症状**: 卡在数据加载阶段

**快速修复**:
```bash
# 创建超小数据集
python3 create_tiny_dataset.py

# 修改脚本使用 train_TINY.parquet
```

---

## 5️⃣ 调试工作流推荐

### 🎯 第一次运行
1. `python3 test_components.py` (10秒)
2. `bash examples/grpo_trainer/run_qwen2_5_vl-3b_fake_dataset_DEBUG.sh` (2-5分钟)
3. 如果成功 → 运行完整训练
4. 如果失败 → 看错误日志，根据上面的错误速查修复

### 🔧 修改代码后验证
1. `python3 test_components.py` - 确保导入正常 (10秒)
2. 运行 DEBUG 模式 (2-5分钟)
3. 成功后再用完整配置

### 🐛 遇到新错误
1. 复制完整错误信息
2. 查看错误速查表
3. 如果是新错误，用 DEBUG 模式复现（更快）
4. 修复后，再次用 DEBUG 模式验证

---

## 6️⃣ 性能对比

| 场景 | 传统方式 | 使用技巧 | 节省时间 |
|------|---------|---------|---------|
| 验证环境配置 | 启动完整训练 (5-10分钟) | `test_components.py` (10秒) | 30-60x |
| 测试代码修改 | 完整训练一个epoch (30-60分钟) | DEBUG模式 (2-5分钟) | 10-15x |
| 调试新错误 | 反复完整启动 (每次10分钟) | DEBUG模式复现 (2分钟) | 5x |
| 找出问题点 | 试错法 (数小时) | 分阶段测试 (15分钟) | 10-20x |

---

## 📚 相关文件

- `test_components.py` - 组件测试工具
- `create_tiny_dataset.py` - 创建超小测试数据集
- `examples/grpo_trainer/run_qwen2_5_vl-3b_fake_dataset_DEBUG.sh` - DEBUG 模式训练脚本
- `examples/grpo_trainer/run_qwen2_5_vl-3b_fake_dataset.sh` - 完整训练脚本

---

## 💡 专业提示

1. **永远先用 DEBUG 模式** - 验证代码能跑通，再用完整配置
2. **使用 tmux/screen** - 长时间训练不怕断开连接
3. **善用分阶段测试** - 快速定位问题在哪个环节
4. **保存工作配置** - 找到能跑的配置后，保存下来
5. **监控 GPU 使用** - `watch -n 1 nvidia-smi` 实时查看

---

## 🎓 总结

**调试黄金法则**:
> 花 2 分钟验证，好过花 2 小时等待失败

**推荐流程**:
```
环境测试(10s) → DEBUG训练(2min) → 完整训练(数小时)
     ↓ 失败              ↓ 失败              ↓ 监控
  修复环境          分阶段定位           tmux后台运行
```

记住：**快速失败，快速迭代！**

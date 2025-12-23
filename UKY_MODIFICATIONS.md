# Uky 修改记录

本文档记录了所有标记为 `# Uky` 的修改，用于在不同集群之间迁移时快速恢复配置。

## 修改文件清单

### 1. 核心代码修改 (Core Code)

#### `/root/verl_Uky/verl/workers/rollout/vllm_rollout/vllm_async_server.py`
**行号**: 355-356
**修改原因**: vLLM v1 API 变更，`disable_log_requests` 改为 `enable_log_requests`
**修改内容**:
```python
# disable_log_requests=engine_args.disable_log_requests, # Uky
enable_log_requests=engine_args.enable_log_requests, # Uky
```

#### `/root/verl_Uky/verl/workers/rollout/vllm_rollout/vllm_rollout_spmd.py`
**行号**: 29-36
**修改原因**: 修复 vast.ai 等环境中的 Triton 编译问题（`-lcuda` 链接错误）
**修改内容**:
```python
# Uky: Fix Triton compilation issues BEFORE any vLLM imports
# This is for vast.ai and similar environments where libcuda.so is not in standard paths
import os
cuda_stubs = "/usr/local/cuda/lib64/stubs"
if os.path.exists(cuda_stubs):
    current_ld_path = os.environ.get("LD_LIBRARY_PATH", "")
    if cuda_stubs not in current_ld_path:
        os.environ["LD_LIBRARY_PATH"] = f"{cuda_stubs}:{current_ld_path}"
```

---

### 2. 训练脚本 (Training Scripts)

所有三个脚本都在: `/root/verl_Uky/examples/grpo_trainer/`

#### `run_qwen2_5_vl-3b_fake_dataset.sh`
**用途**: 标准训练配置（20 epochs）
**关键修改**:
```bash
# 环境变量设置 (Lines 40-46)
export TRITON_CACHE_DIR=/tmp/triton_cache  # Uky
export VLLM_USE_TRITON_FLASH_ATTN=0  # Uky - Disable Triton flash attention
# export VLLM_ATTENTION_BACKEND=TORCH_SDPA  # Uky - TORCH_SDPA not implemented in vLLM 0.12.0
export VLLM_ATTENTION_BACKEND=FLASH_ATTN  # Uky - Use CUDA FlashAttention (not Triton version)
export VLLM_WORKER_USE_RAY=1  # Uky - Force Ray worker mode
export LD_LIBRARY_PATH=/usr/local/cuda/lib64/stubs:$LD_LIBRARY_PATH  # Uky
```

**训练参数**:
- `data.train_batch_size=4`
- `data.max_prompt_length=10240`
- `data.max_response_length=512`
- `trainer.total_epochs=20`
- `actor_rollout_ref.rollout.gpu_memory_utilization=0.3`
- `actor_rollout_ref.rollout.enforce_eager=False`

#### `run_qwen2_5_vl-3b_fake_dataset_DEBUG.sh`
**用途**: 快速验证配置（1 epoch，极小数据量，2-5分钟运行）
**关键差异**:
```bash
# 极小化配置用于快速测试
data.train_batch_size=1
data.max_prompt_length=512
data.max_response_length=64
trainer.total_epochs=1
trainer.logger='["console"]'  # 只输出到控制台，不用 wandb
trainer.save_freq=999  # 不保存中间checkpoint
trainer.test_freq=999
```

#### `run_qwen2_5_vl-3b_fake_dataset_FAST_LOAD.sh`
**用途**: 快速加载模型（预计将加载时间从30-60分钟减少到2-5分钟）
**关键优化**:
```bash
# 额外的加速环境变量 (Lines 48-50)
export VLLM_WORKER_MULTIPROC_METHOD=spawn  # Uky - 使用 spawn 而不是 fork，减少内存复制
export TOKENIZERS_PARALLELISM=false  # Uky - 禁用 tokenizer 并行，避免死锁

# 加速训练参数 (Lines 90-92)
actor_rollout_ref.rollout.enforce_eager=True  # 跳过 CUDA graph 编译
actor_rollout_ref.rollout.load_format=safetensors  # 使用快速加载格式
actor_rollout_ref.rollout.gpu_memory_utilization=0.4  # 增加可用内存
```

---

### 3. 辅助工具 (Utility Scripts)

#### `/root/verl_Uky/test_components.py`
**用途**: 10秒内快速验证环境配置是否正确
**测试内容**:
- PyTorch + CUDA 可用性
- 数据文件是否存在
- vLLM 导入测试
- verl 导入测试
- Ray 基础功能测试

#### `/root/verl_Uky/warmup_model.py`
**用途**: 一次性预热模型，将权重加载到系统缓存
**加速原理**: 后续加载会从页面缓存读取，而不是从磁盘

#### `/root/verl_Uky/create_tiny_dataset.py`
**用途**: 创建仅2个样本的超小数据集用于快速测试
**输出**: `$DATA_OUTPUT_DIR/train_tiny.parquet`

#### `/root/verl_Uky/fix_triton.py`
**用途**: 独立的 Triton 修复模块（备用方案，当前未使用）
**说明**: 当前直接在 `vllm_rollout_spmd.py` 中应用修复

---

### 4. 文档 (Documentation)

#### `/root/verl_Uky/DEBUG_TIPS.md`
完整的调试指南，包含:
- 快速验证工具使用方法
- 模型加载优化技巧
- 常见错误解决方案
- 调试工作流程建议

#### `/root/verl_Uky/QUICK_FIX.md`
快速参考卡，包含:
- 最常见错误的即时修复方法
- 环境变量速查表

---

## 迁移到新集群时的操作清单

1. **复制整个代码库到新集群**
   ```bash
   rsync -avz /root/verl_Uky/ new_cluster:/path/to/verl_Uky/
   ```

2. **验证核心修改是否存在**
   ```bash
   cd /path/to/verl_Uky
   grep -n "# Uky" verl/workers/rollout/vllm_rollout/vllm_async_server.py
   grep -n "# Uky" verl/workers/rollout/vllm_rollout/vllm_rollout_spmd.py
   ```

3. **配置路径**
   ```bash
   cp git_ignore.py.example git_ignore.py
   # 编辑 git_ignore.py 设置新集群的路径
   ```

4. **快速验证环境**
   ```bash
   python3 test_components.py
   ```

5. **运行 DEBUG 脚本验证**
   ```bash
   bash examples/grpo_trainer/run_qwen2_5_vl-3b_fake_dataset_DEBUG.sh
   ```

---

## 已解决的问题

### 问题 1: vLLM API 兼容性
- **错误**: `AttributeError: 'AsyncEngineArgs' object has no attribute 'disable_log_requests'`
- **根因**: vLLM v1 API 变更
- **解决**: 修改 `vllm_async_server.py` 使用新 API

### 问题 2: Triton 编译失败
- **错误**: `cannot find -lcuda`
- **根因**: vast.ai 等容器环境中 libcuda.so 不在标准路径
- **解决**: 在 `vllm_rollout_spmd.py` 中动态添加 CUDA stubs 到 LD_LIBRARY_PATH

### 问题 3: TORCH_SDPA backend 不可用
- **错误**: `ValueError: Backend TORCH_SDPA must be registered before use`
- **根因**: vLLM 0.12.0 的 TORCH_SDPA backend 枚举存在但未实现
- **解决**: 改用 FLASH_ATTN backend（CUDA 实现，非 Triton 版本）

### 问题 4: 模型加载缓慢
- **症状**: 30-60分钟才能开始训练
- **根因**: 使用 `load_format=auto` 导致慢速磁盘 I/O
- **解决**: 使用 `load_format=safetensors` + `enforce_eager=True`

### 问题 5: 调试周期长
- **症状**: 每次验证修复都需要30-60分钟
- **解决**:
  - 创建 DEBUG 脚本（极小配置）
  - 创建 test_components.py（10秒验证）
  - 创建 tiny 数据集（2个样本）

---

## 环境变量速查表

### 必需的环境变量 (在所有训练脚本中)
```bash
# Ray 配置
export RAY_num_prestart_python_workers=1
export RAY_worker_register_timeout_seconds=600

# 线程限制（防止 pthread_create 失败）
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1

# Triton 修复（针对 vast.ai）
export TRITON_CACHE_DIR=/tmp/triton_cache
export VLLM_USE_TRITON_FLASH_ATTN=0
export VLLM_ATTENTION_BACKEND=FLASH_ATTN  # 注意：vLLM 0.12.0 不支持 TORCH_SDPA
export VLLM_WORKER_USE_RAY=1
export LD_LIBRARY_PATH=/usr/local/cuda/lib64/stubs:$LD_LIBRARY_PATH
```

### 额外的加速环境变量 (FAST_LOAD 版本)
```bash
export VLLM_WORKER_MULTIPROC_METHOD=spawn
export TOKENIZERS_PARALLELISM=false
```

---

## 重要提示

1. **所有修改都已标记**: 搜索 `# Uky` 即可找到所有自定义修改
2. **Python 代码修复优先于环境变量**: Ray worker 不继承所有环境变量，所以 Triton 修复直接写在 Python 代码中
3. **保留注释的旧代码**: 所有被替换的代码都保留为注释，便于理解和回滚
4. **便携性优先**: 所有修复都考虑了在不同集群上运行的需求
5. **目录结构**: 确保工作在 `/root/verl_Uky/` 而不是嵌套的 `/root/verl_Uky/verl_Uky/`

---

最后更新: 2025-12-22

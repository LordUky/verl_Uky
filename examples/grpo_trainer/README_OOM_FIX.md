# Ray OOM 问题解决方案

## 问题分析

您遇到的OOM错误是 **Ray系统内存（RAM）耗尽**，而不是GPU显存问题。错误信息显示：

```
10 Workers (tasks / actors) killed due to memory pressure (OOM)
```

这表明Ray的内存监控器检测到系统RAM使用过高，主动杀死了workers来释放内存。

### 根本原因

1. **Ray Object Store内存过大**：Ray默认会使用较大比例的系统内存作为object store
2. **Worker并发度过高**：多个workers同时加载模型和数据，消耗大量内存
3. **数据加载策略**：长序列（max_prompt_length=10240）导致每个batch内存占用巨大
4. **模型参数未offload**：模型参数和优化器状态都在内存中，未卸载到CPU

## 解决方案对比

### 方案1：`run_qwen2_5_vl-3b_fake_dataset_ray_optimized.sh` (推荐)

**最全面的修复**，同时解决Ray内存和训练配置问题。

#### 关键优化：

##### 1. Ray内存控制（最重要）
```bash
# 提高内存阈值，避免过早杀死workers
export RAY_memory_usage_threshold=0.98

# 限制Ray object store为30GB（总内存188GB）
export RAY_object_store_memory=$((30 * 1024 * 1024 * 1024))
```

##### 2. 序列长度大幅减少
```bash
data.max_prompt_length=2048      # 从10240降低到2048
data.max_response_length=256     # 从512降低到256
data.filter_overlong_prompts=True
```

##### 3. FSDP全面卸载
```bash
actor_rollout_ref.actor.fsdp_config.param_offload=True
actor_rollout_ref.actor.fsdp_config.optimizer_offload=True
actor_rollout_ref.ref.fsdp_config.param_offload=True
actor_rollout_ref.ref.fsdp_config.optimizer_offload=True
```

##### 4. 批次大小最小化
```bash
data.train_batch_size=1
actor_rollout_ref.actor.ppo_mini_batch_size=1
actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=1
```

##### 5. GPU内存保守配置
```bash
actor_rollout_ref.rollout.gpu_memory_utilization=0.5
actor_rollout_ref.rollout.enable_chunked_prefill=True
```

#### 使用方法：
```bash
cd /root/verl_Uky/examples/grpo_trainer
./run_qwen2_5_vl-3b_fake_dataset_ray_optimized.sh
```

### 方案2：`run_qwen2_5_vl-3b_fake_dataset_optimized.sh`

专注于训练参数优化，但缺少Ray内存控制。适合Ray内存问题不严重的情况。

## 渐进式调试策略

如果方案1仍然OOM，按以下顺序逐步调整：

### Level 1: 进一步降低Ray内存
```bash
export RAY_object_store_memory=$((20 * 1024 * 1024 * 1024))  # 降到20GB
```

### Level 2: 更激进的序列长度限制
```bash
data.max_prompt_length=1024
data.max_response_length=128
```

### Level 3: 启用Eager模式（禁用CUDA Graph）
```bash
actor_rollout_ref.rollout.enforce_eager=True
```

### Level 4: 降低GPU内存利用率
```bash
actor_rollout_ref.rollout.gpu_memory_utilization=0.3
```

### Level 5: 禁用Ray内存监控（最后手段，慎用）
```bash
export RAY_memory_monitor_refresh_ms=0
```

## 实时监控

### 监控系统内存
在另一个终端运行：
```bash
watch -n 1 "free -h && echo '---' && ps aux --sort=-%mem | head -10"
```

### 监控GPU内存
```bash
watch -n 1 nvidia-smi
```

### 查看Ray日志
```bash
# 查看Ray节点日志
ray logs raylet.out -ip 172.17.0.3

# 或查看所有Ray日志
ls -lh /tmp/ray/session_latest/logs/
```

## 硬件配置说明

当前环境：
- **GPU**: NVIDIA RTX A6000 (46GB VRAM)
- **RAM**: 188GB
- **交换空间**: 8GB

这个配置理论上足够运行3B模型，OOM主要是Ray内存管理和配置不当导致的。

## 性能 vs 内存权衡

| 参数 | 内存优先 | 性能优先 | 平衡 |
|------|----------|----------|------|
| `max_prompt_length` | 1024 | 4096 | 2048 |
| `train_batch_size` | 1 | 4 | 2 |
| `gpu_memory_utilization` | 0.3 | 0.7 | 0.5 |
| `param_offload` | True | False | True |
| `optimizer_offload` | True | False | True |
| `RAY_object_store_memory` | 20GB | 50GB | 30GB |

推荐先使用"内存优先"配置确保能运行，然后逐步向"平衡"或"性能优先"调整。

## 常见问题

### Q: 为什么GPU显存充足还会OOM？
A: 您遇到的是系统RAM的OOM，不是GPU显存OOM。Ray workers在CPU上加载数据、管理对象时消耗大量系统内存。

### Q: 可以完全禁用Ray内存监控吗？
A: 技术上可以（`RAY_memory_monitor_refresh_ms=0`），但不推荐。这可能导致系统完全卡死而不是优雅地杀死workers。

### Q: 为什么要限制object_store_memory？
A: Ray的object store默认会使用大量系统内存。限制它可以为Python进程、模型加载、数据处理预留足够的RAM。

### Q: 如何知道设置是否生效？
A: 运行时检查：
```bash
python3 -c "import ray; ray.init(); print(ray.cluster_resources())"
```

## 预期效果

使用Ray优化脚本后，您应该看到：
- ✅ 不再出现"Workers killed due to memory pressure"错误
- ✅ 训练能够稳定运行
- ✅ 系统RAM使用保持在安全范围（< 85%）
- ⚠️ 训练速度可能会慢一些（因为启用了offloading）

训练速度的降低是可以接受的权衡，优先保证稳定性。待稳定后可以逐步调整参数提升性能。

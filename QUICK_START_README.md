# 🚀 快速开始 - Qwen2.5-VL-3B 训练

本目录包含了训练 Qwen2.5-VL-3B-Instruct 模型所需的所有文件。

## 📦 文件清单

### 核心文件

| 文件 | 说明 | 位置 |
|------|------|------|
| **quick_start_fake_vlm.sh** | 一键启动脚本 | 根目录 |
| **FAKE_VLM_TRAINING_GUIDE.md** | 详细使用指南 | 根目录 |
| **fake_dataset_vlm.py** | 数据预处理脚本 | `examples/data_preprocess/` |
| **mcq_vlm.py** | MCQ 奖励函数 | `verl/utils/reward_score/` |
| **run_qwen2_5_vl-3b_fake_dataset.sh** | 训练脚本 | `examples/grpo_trainer/` |
| **test_mcq_reward.py** | 奖励函数测试 | 根目录 |

## ⚡ 最快速开始 (推荐)

只需一个命令：

```bash
cd /gpfs/projects/p32509/userdata/zheyu/verl_Uky

# 使用 vLLM 引擎
bash quick_start_fake_vlm.sh vllm

# 或使用 SGLang 引擎 (更快)
bash quick_start_fake_vlm.sh sglang
```

这个脚本会自动：
1. ✅ 检查并预处理数据
2. ✅ 验证数据格式
3. ✅ 启动训练

## 📝 分步执行

如果你想手动控制每一步：

### 步骤 1: 数据预处理

```bash
python examples/data_preprocess/fake_dataset_vlm.py \
    --input_json /home/vgc7798/projects_p32509/userdata/zheyu/world_model_vlm/benchmark/prompt/fake_dataset.json \
    --local_save_dir ~/data/fake_vlm_dataset \
    --train_ratio 0.9
```

### 步骤 2: 测试奖励函数 (可选)

```bash
python test_mcq_reward.py
```

### 步骤 3: 开始训练

```bash
bash examples/grpo_trainer/run_qwen2_5_vl-3b_fake_dataset.sh vllm
```

## 🎓 详细教程

查看 **[FAKE_VLM_TRAINING_GUIDE.md](FAKE_VLM_TRAINING_GUIDE.md)** 获取：
- 完整的配置说明
- 常见问题解答
- 性能调优建议
- 自定义配置方法

## 🔍 文件详解

### 1. 数据预处理脚本 (`fake_dataset_vlm.py`)

**功能**:
- 读取 JSON 格式的数据集
- 提取图像路径和问题
- 转换为 parquet 格式
- 分割训练集/测试集

**输入格式**:
```json
{
  "id_0": {
    "Question": "Based on the image...<image>/path/to/image.jpg</image>",
    "Reasoning": "...",
    "Choices": ["A. ...", "B. ...", "C. ...", "D. ..."],
    "category": "..."
  }
}
```

**输出**:
- `~/data/fake_vlm_dataset/train.parquet`
- `~/data/fake_vlm_dataset/test.parquet`

### 2. 奖励函数 (`mcq_vlm.py`)

**功能**:
- 从模型输出提取答案 (A/B/C/D)
- 与正确答案比对
- 返回奖励分数 (1.0 或 0.0)

**支持的输出格式**:
- "The answer is A"
- "Answer: B"
- "I choose C"
- 单独的 "A"

### 3. 训练脚本 (`run_qwen2_5_vl-3b_fake_dataset.sh`)

**关键参数**:
```bash
# 数据配置
train_batch_size=256
max_prompt_length=1024
max_response_length=512

# 模型配置
learning_rate=1e-6
gradient_checkpointing=True

# 训练配置
total_epochs=20
n_gpus_per_node=8
tensor_model_parallel_size=1
```

## 🛠️ 自定义配置

### 修改数据集路径

编辑 `fake_dataset_vlm.py`:
```python
parser.add_argument(
    "--input_json",
    default="/你的/数据/路径.json",  # 改这里
    ...
)
```

### 修改模型路径

编辑 `run_qwen2_5_vl-3b_fake_dataset.sh`:
```bash
MODEL_PATH="/你的/模型/路径"  # 改这里
```

### 调整超参数

**减小显存占用**:
```bash
# 在 run_qwen2_5_vl-3b_fake_dataset.sh 中修改
data.train_batch_size=128  # 减小批次
actor_rollout_ref.rollout.n=3  # 减少采样数
```

**调整学习率**:
```bash
actor_rollout_ref.actor.optim.lr=5e-7  # 改为更小的学习率
```

**使用更少 GPU**:
```bash
trainer.n_gpus_per_node=4  # 从 8 改为 4
```

## 🧪 测试工具

### 测试奖励函数

```bash
python test_mcq_reward.py
```

这会运行：
- ✅ 答案提取测试
- ✅ 奖励计算测试
- ✅ 边界情况测试
- ✅ 交互式测试模式

### 验证数据格式

```bash
python -c "
import pandas as pd
df = pd.read_parquet('~/data/fake_vlm_dataset/train.parquet')
print('样本数:', len(df))
print('列名:', df.columns.tolist())
print('第一个样本:', df.iloc[0])
"
```

## 📊 监控训练

### WandB (推荐)

训练会自动记录到 WandB:
- 项目名: `verl_grpo_fake_vlm`
- 实验名: `qwen2_5_vl_3b_spatial_reasoning`

```bash
# 首次使用需要登录
wandb login
```

### 本地日志

```bash
# 查看训练日志
tail -f ~/verl_experiments/qwen2_5_vl_3b_spatial_reasoning/train.log
```

## 🎯 训练结果

训练完成后，检查点保存在:
```
~/verl_experiments/qwen2_5_vl_3b_spatial_reasoning/
├── checkpoint-10/
├── checkpoint-20/
└── checkpoint-final/
```

## ⚠️ 常见问题

### 问题 1: 找不到图像

**症状**: `Warning: Image not found`

**解决**:
```bash
# 检查图像路径
ls /home/vgc7798/zheyu_b1222/example.jpeg

# 如果不存在，更新 JSON 中的路径
```

### 问题 2: 显存不足

**症状**: `CUDA out of memory`

**解决方案**:
1. 减小 batch size (改 `train_batch_size=128`)
2. 启用 offloading (改 `param_offload=True`)
3. 减少采样数 (改 `rollout.n=3`)

### 问题 3: 模型加载失败

**症状**: `Model not found`

**解决**:
```bash
# 检查模型目录
ls -la /home/vgc7798/canyu_models/models--Qwen--Qwen2.5-VL-3B-Instruct/snapshots/

# 脚本会自动找到最新的 snapshot
```

## 🔗 相关资源

- **verl 官方文档**: https://verl.readthedocs.io/
- **Qwen2.5-VL 模型**: https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct
- **GitHub Issues**: https://github.com/volcengine/verl/issues

## 💡 提示

1. **首次运行**: 建议先用小数据集测试
2. **显存优化**: 如果 OOM，优先减小 batch size
3. **速度优化**: SGLang 通常比 vLLM 快 20-30%
4. **监控**: 使用 WandB 实时监控训练过程
5. **保存频率**: 根据数据集大小调整 `save_freq`

## 📧 获取帮助

如果遇到问题：
1. 查看 [FAKE_VLM_TRAINING_GUIDE.md](FAKE_VLM_TRAINING_GUIDE.md)
2. 运行 `python test_mcq_reward.py` 测试组件
3. 检查日志文件
4. 提交 GitHub Issue

---

**开始训练吧! 🎉**

```bash
cd /gpfs/projects/p32509/userdata/zheyu/verl_Uky
bash quick_start_fake_vlm.sh
```

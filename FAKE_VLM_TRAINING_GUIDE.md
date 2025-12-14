# Qwen2.5-VL-3B 训练指南 - 使用假数据集

本指南将手把手教你如何使用 verl 框架训练 Qwen2.5-VL-3B-Instruct 模型，基于你的虚假数据集。

## 📋 前置条件

- **模型路径**: `/home/vgc7798/canyu_models/models--Qwen--Qwen2.5-VL-3B-Instruct`
- **数据集路径**: `/home/vgc7798/projects_p32509/userdata/zheyu/world_model_vlm/benchmark/prompt/fake_dataset.json`
- **verl 仓库**: `/gpfs/projects/p32509/userdata/zheyu/verl_Uky`

## 🚀 快速开始 (3 步完成)

### 第 1 步: 预处理数据

首先，我们需要将你的 JSON 数据转换为 verl 支持的 parquet 格式。

```bash
cd /gpfs/projects/p32509/userdata/zheyu/verl_Uky

# 运行数据预处理脚本
python examples/data_preprocess/fake_dataset_vlm.py \
    --input_json /home/vgc7798/projects_p32509/userdata/zheyu/world_model_vlm/benchmark/prompt/fake_dataset.json \
    --local_save_dir ~/data/fake_vlm_dataset \
    --train_ratio 0.9
```

**这一步做了什么?**
- 读取你的 JSON 数据集
- 提取图像路径和问题
- 格式化为多选题 (MCQ) 格式
- 分割为训练集和测试集 (90%/10%)
- 保存为 parquet 文件

**输出位置**: `~/data/fake_vlm_dataset/`
- `train.parquet` - 训练数据
- `test.parquet` - 测试数据

### 第 2 步: 验证数据

检查数据是否正确生成:

```bash
python -c "
import pandas as pd
df = pd.read_parquet('~/data/fake_vlm_dataset/train.parquet')
print(f'训练样本数: {len(df)}')
print(f'列名: {df.columns.tolist()}')
print(f'第一个样本:')
print(df.iloc[0])
"
```

### 第 3 步: 开始训练

现在可以启动训练了！

```bash
cd /gpfs/projects/p32509/userdata/zheyu/verl_Uky

# 使用 vLLM 引擎训练
bash examples/grpo_trainer/run_qwen2_5_vl-3b_fake_dataset.sh vllm

# 或者使用 SGLang 引擎 (更快)
bash examples/grpo_trainer/run_qwen2_5_vl-3b_fake_dataset.sh sglang
```

## 📁 创建的文件说明

### 1. 数据预处理脚本
**位置**: `examples/data_preprocess/fake_dataset_vlm.py`

**功能**:
- 解析你的 JSON 格式数据
- 提取图像路径 (从 `<image>path</image>` 标签)
- 处理多选题格式
- 生成训练和测试集

**关键参数**:
- `--input_json`: 输入 JSON 文件路径
- `--local_save_dir`: 输出目录
- `--train_ratio`: 训练集比例 (默认 0.9)

### 2. Reward Function (奖励函数)
**位置**: `verl/utils/reward_score/mcq_vlm.py`

**功能**:
- 从模型输出中提取答案 (A/B/C/D)
- 与正确答案比较
- 返回奖励分数 (1.0 = 正确, 0.0 = 错误)

**支持的答案格式**:
- "The answer is A"
- "Answer: B"
- "选择 C"
- 单独的字母 "A"

### 3. 训练脚本
**位置**: `examples/grpo_trainer/run_qwen2_5_vl-3b_fake_dataset.sh`

**关键配置**:
```bash
# 模型配置
MODEL_PATH: Qwen2.5-VL-3B-Instruct 路径
ENGINE: vllm 或 sglang

# 训练超参数
learning_rate: 1e-6
batch_size: 256
epochs: 20
n_samples_per_prompt: 5  (每个 prompt 生成 5 个回答)

# GPU 配置
n_gpus_per_node: 8
nnodes: 1
```

## 🔧 自定义配置

### 调整批次大小 (如果显存不足)

编辑 `run_qwen2_5_vl-3b_fake_dataset.sh`:

```bash
# 减小批次大小
data.train_batch_size=128  # 从 256 改为 128
actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=4  # 从 8 改为 4
```

### 修改学习率

```bash
actor_rollout_ref.actor.optim.lr=5e-7  # 从 1e-6 改为 5e-7
```

### 更改训练轮数

```bash
trainer.total_epochs=30  # 从 20 改为 30
```

### 使用更少 GPU

```bash
trainer.n_gpus_per_node=4  # 从 8 改为 4
```

## 📊 监控训练

训练过程会自动记录到 WandB:

```bash
# 查看训练日志
wandb login  # 首次需要登录

# 项目名称: verl_grpo_fake_vlm
# 实验名称: qwen2_5_vl_3b_spatial_reasoning
```

或者查看本地日志:

```bash
# 训练输出在终端实时显示
# 模型检查点保存在: ~/verl_experiments/
```

## 🐛 常见问题

### 问题 1: 找不到图像文件

**错误**: `Warning: Image not found: /path/to/image.jpeg`

**解决**:
确保 JSON 中的图像路径是绝对路径且文件存在:
```bash
# 检查图像是否存在
ls /home/vgc7798/zheyu_b1222/example.jpeg
```

### 问题 2: 显存不足 (OOM)

**解决方案 1**: 减小批次大小
```bash
data.train_batch_size=128  # 减半
actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=4
```

**解决方案 2**: 启用显存优化
```bash
actor_rollout_ref.actor.fsdp_config.param_offload=True
actor_rollout_ref.actor.fsdp_config.optimizer_offload=True
```

**解决方案 3**: 减少采样数
```bash
actor_rollout_ref.rollout.n=3  # 从 5 改为 3
```

### 问题 3: 数据格式错误

**检查数据格式**:
```python
import pandas as pd
df = pd.read_parquet('~/data/fake_vlm_dataset/train.parquet')

# 检查必需的列
required_cols = ['prompt', 'images', 'reward_model', 'ability']
for col in required_cols:
    assert col in df.columns, f"缺少列: {col}"

print("数据格式正确!")
```

### 问题 4: 模型路径错误

**检查模型路径**:
```bash
# 找到正确的 snapshot 目录
ls -la /home/vgc7798/canyu_models/models--Qwen--Qwen2.5-VL-3B-Instruct/snapshots/

# 脚本会自动选择最新的 snapshot
```

## 🎯 验证训练结果

训练完成后，模型会保存在:
```bash
~/verl_experiments/qwen2_5_vl_3b_spatial_reasoning/
```

### 测试训练后的模型

```python
from transformers import Qwen2VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from PIL import Image

# 加载训练后的模型
model_path = "~/verl_experiments/qwen2_5_vl_3b_spatial_reasoning/checkpoint-final"
model = Qwen2VLForConditionalGeneration.from_pretrained(model_path)
processor = AutoProcessor.from_pretrained(model_path)

# 测试
image = Image.open("/home/vgc7798/zheyu_b1222/example.jpeg")
question = "Based on the image, which view represents the resulting state?\n\nChoices:\nA. [Option A]\nB. [Option B]\nC. [Option C]\nD. [Option D]"

inputs = processor(text=question, images=image, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=100)
answer = processor.decode(outputs[0], skip_special_tokens=True)

print(f"Model answer: {answer}")
```

## 📈 性能调优建议

### 1. 针对你的数据集大小

你的数据集如果很大 (>10000 样本):
```bash
trainer.total_epochs=10  # 减少轮数
data.train_batch_size=512  # 增大批次
```

数据集较小 (<1000 样本):
```bash
trainer.total_epochs=30  # 增加轮数
data.train_batch_size=128  # 减小批次，避免过拟合
```

### 2. 使用 SGLang (推荐)

SGLang 通常比 vLLM 快 20-30%:
```bash
bash examples/grpo_trainer/run_qwen2_5_vl-3b_fake_dataset.sh sglang
```

### 3. 多节点训练

如果有多个节点:
```bash
trainer.nnodes=2  # 使用 2 个节点
trainer.n_gpus_per_node=8
```

## 📚 下一步

训练完成后，你可以:

1. **评估模型**: 在测试集上评估准确率
2. **微调 Reward Function**: 调整 `mcq_vlm.py` 中的奖励逻辑
3. **尝试其他算法**: 将 `grpo` 改为 `ppo`
4. **继续训练**: 从 checkpoint 继续训练

## 🆘 获取帮助

- **verl 文档**: https://verl.readthedocs.io/
- **GitHub Issues**: https://github.com/volcengine/verl/issues
- **示例代码**: `/gpfs/projects/p32509/userdata/zheyu/verl_Uky/examples/`

---

**祝训练顺利! 🎉**

如有问题，请检查:
1. 数据预处理是否成功
2. 图像路径是否正确
3. GPU 显存是否充足
4. 模型路径是否正确

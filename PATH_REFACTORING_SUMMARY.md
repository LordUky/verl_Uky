# 路径重构总结 / Path Refactoring Summary

## 概述 / Overview

本次重构将项目中所有硬编码的绝对路径统一管理到 `git_ignore.py` 配置文件中，使项目可以轻松部署到不同环境，无需手动修改多个文件中的路径。

This refactoring centralizes all hardcoded absolute paths into a `git_ignore.py` configuration file, making it easy to deploy the project across different environments without manually changing paths in multiple files.

## 变更文件 / Changed Files

### 新增文件 / New Files

1. **[git_ignore.py](git_ignore.py)** - 环境特定配置文件（不提交到git）
   - Environment-specific configuration (NOT committed to git)

2. **[git_ignore.py.example](git_ignore.py.example)** - 配置模板文件（提交到git）
   - Configuration template (committed to git)

3. **[PATH_CONFIG_README.md](PATH_CONFIG_README.md)** - 详细使用说明
   - Detailed usage guide

### 修改的Python文件 / Modified Python Files

1. **[examples/data_preprocess/fake_dataset_vlm.py](examples/data_preprocess/fake_dataset_vlm.py)**
   - 原路径: `/home/vgc7798/projects_p32509/userdata/zheyu/world_model_vlm/benchmark/prompt/fake_dataset.json`
   - 改为: `from git_ignore import FAKE_DATASET_JSON_STR`

2. **[print_data_info.py](print_data_info.py)**
   - 原路径: `/home/vgc7798/projects_p32509/userdata/zheyu/verl_Uky`
   - 改为: `from git_ignore import DATA_OUTPUT_DIR`

3. **[test_mcq_reward.py](test_mcq_reward.py)**
   - 原路径: `/gpfs/projects/p32509/userdata/zheyu/verl_Uky`
   - 改为: 动态检测项目根目录

4. **[examples/sglang_multiturn/search_r1_like/local_dense_retriever/retrieval_server.py](examples/sglang_multiturn/search_r1_like/local_dense_retriever/retrieval_server.py)**
   - 原路径: `/home/peterjin/mnt/index/wiki-18/e5_Flat.index`
   - 原路径: `/home/peterjin/mnt/data/retrieval-corpus/wiki-18.jsonl`
   - 改为: `from git_ignore import RETRIEVAL_INDEX_PATH_STR, RETRIEVAL_CORPUS_PATH_STR`

### 修改的Shell脚本 / Modified Shell Scripts

1. **[examples/grpo_trainer/run_qwen2_5_vl-3b_fake_dataset.sh](examples/grpo_trainer/run_qwen2_5_vl-3b_fake_dataset.sh)**
   - 原路径: `/home/vgc7798/canyu_models/models--Qwen--Qwen2.5-VL-3B-Instruct/snapshots`
   - 原路径: `/home/vgc7798/projects_p32509/userdata/zheyu/verl_Uky`
   - 改为: 从 `git_ignore.py` 动态读取

2. **[quick_start_fake_vlm.sh](quick_start_fake_vlm.sh)**
   - 原路径: `/home/vgc7798/projects_p32509/userdata/zheyu/world_model_vlm/benchmark/prompt/fake_dataset.json`
   - 改为: 从 `git_ignore.py` 动态读取

### 修改的配置文件 / Modified Config Files

1. **[.gitignore](.gitignore)**
   - 添加: `git_ignore.py` (排除环境特定配置)

## 主要改进 / Key Improvements

### 1. 集中管理 / Centralized Management
- ✅ 所有路径配置集中在一个文件中
- ✅ All path configurations in one file

### 2. 环境隔离 / Environment Isolation
- ✅ `git_ignore.py` 不提交到git，每个环境独立配置
- ✅ `git_ignore.py` not committed, each environment has its own config

### 3. 易于部署 / Easy Deployment
```bash
git pull
cp git_ignore.py.example git_ignore.py
nano git_ignore.py  # 编辑路径 / Edit paths
python git_ignore.py  # 验证 / Verify
```

### 4. 向后兼容 / Backward Compatible
- ✅ 如果缺少 `git_ignore.py`，脚本会显示友好的错误信息
- ✅ Graceful error messages if `git_ignore.py` is missing

### 5. 类型安全 / Type Safety
- ✅ Python中使用 `pathlib.Path` 对象
- ✅ Use `pathlib.Path` objects in Python
- ✅ 提供字符串版本用于Shell脚本
- ✅ String versions provided for shell scripts

## 配置的路径变量 / Configured Path Variables

### 基础路径 / Base Paths
- `PROJECT_ROOT` - 项目根目录（自动检测）/ Project root (auto-detected)
- `USER_DATA_BASE` - 用户数据基础目录 / User data base directory
- `MODEL_BASE` - 模型基础目录 / Model base directory

### 数据路径 / Data Paths
- `FAKE_DATASET_JSON` - 假数据集JSON文件 / Fake dataset JSON file
- `DATA_OUTPUT_DIR` - 输出数据目录 / Output data directory

### 模型路径 / Model Paths
- `QWEN_VL_3B_BASE` - Qwen2.5-VL-3B模型目录 / Qwen model directory
- `get_latest_qwen_snapshot()` - 获取最新模型快照 / Get latest model snapshot

### 检索路径 / Retrieval Paths
- `RETRIEVAL_INDEX_PATH` - 检索索引路径 / Retrieval index path
- `RETRIEVAL_CORPUS_PATH` - 检索语料库路径 / Retrieval corpus path

## 使用示例 / Usage Examples

### Python代码 / Python Code

```python
# 导入路径配置
from git_ignore import FAKE_DATASET_JSON_STR, DATA_OUTPUT_DIR

# 使用配置的路径
with open(FAKE_DATASET_JSON_STR, 'r') as f:
    data = json.load(f)
```

### Shell脚本 / Shell Script

```bash
# 从Python配置读取路径
JSON_PATH=$(python3 -c "from git_ignore import FAKE_DATASET_JSON_STR; print(FAKE_DATASET_JSON_STR)")

# 使用路径
python preprocess.py --input_json "$JSON_PATH"
```

## 部署工作流 / Deployment Workflow

### 场景1: 推送到Git / Scenario 1: Push to Git

```bash
# git_ignore.py 自动被排除
git add .
git commit -m "Add new feature"
git push
```

### 场景2: 在新环境部署 / Scenario 2: Deploy to New Environment

```bash
# 1. 拉取代码
git pull

# 2. 配置环境
cp git_ignore.py.example git_ignore.py
nano git_ignore.py  # 修改为你的路径

# 3. 验证配置
python git_ignore.py

# 4. 开始使用！
./quick_start_fake_vlm.sh
```

## 测试 / Testing

运行以下命令验证配置：

```bash
# 验证路径配置
python git_ignore.py

# 测试数据预处理
python examples/data_preprocess/fake_dataset_vlm.py --help

# 测试训练脚本
bash examples/grpo_trainer/run_qwen2_5_vl-3b_fake_dataset.sh --help
```

## 注意事项 / Notes

1. **首次使用** / First Time Use
   - 必须先创建 `git_ignore.py`：`cp git_ignore.py.example git_ignore.py`
   - Must create `git_ignore.py` first: `cp git_ignore.py.example git_ignore.py`

2. **路径验证** / Path Validation
   - 运行 `python git_ignore.py` 检查配置
   - Run `python git_ignore.py` to verify config

3. **错误处理** / Error Handling
   - 所有脚本都有友好的错误提示
   - All scripts have friendly error messages
   - 缺少配置文件时会提示用户创建
   - Users are prompted to create config if missing

## 迁移前后对比 / Before vs After

### 迁移前 / Before
```python
# 每个文件都有硬编码路径
default="/home/vgc7798/projects/.../fake_dataset.json"
```
- ❌ 部署到新环境需要修改多个文件
- ❌ 容易遗漏某些路径
- ❌ 难以维护

### 迁移后 / After
```python
# 统一从配置文件导入
from git_ignore import FAKE_DATASET_JSON_STR
default=FAKE_DATASET_JSON_STR
```
- ✅ 只需配置一个文件
- ✅ 不会遗漏路径
- ✅ 易于维护和更新

## 未来扩展 / Future Extensions

如果需要添加新的环境特定路径：

1. 在 `git_ignore.py.example` 中添加新变量
2. 在 `git_ignore.py` 中添加实际路径
3. 在需要的文件中导入使用

示例：
```python
# 在 git_ignore.py 中添加
NEW_DATA_PATH = Path("/path/to/new/data")
NEW_DATA_PATH_STR = str(NEW_DATA_PATH)

# 在脚本中使用
from git_ignore import NEW_DATA_PATH_STR
```

## 完成状态 / Completion Status

- ✅ 创建配置文件系统
- ✅ 更新所有Python脚本
- ✅ 更新所有Shell脚本
- ✅ 更新 .gitignore
- ✅ 创建使用文档
- ✅ 创建总结文档

## 相关文档 / Related Documentation

- [PATH_CONFIG_README.md](PATH_CONFIG_README.md) - 详细使用指南
- [git_ignore.py.example](git_ignore.py.example) - 配置模板

---

**重构完成！现在可以轻松地在不同环境间部署项目了！** 🎉

**Refactoring Complete! Easy deployment across environments now!** 🎉

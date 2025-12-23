# VERL 项目迁移完整指南 / Complete Migration Guide

## 📦 迁移到新系统的完整步骤

### 第一步：准备工作

1. **复制整个项目文件夹**
   ```bash
   # 将 verl_Uky 文件夹完整复制到新系统
   scp -r verl_Uky user@new-host:/path/to/destination/
   ```

2. **确认系统要求**
   - **最低 RAM**: 128GB（推荐 256GB，用于 3B 模型训练）
   - **GPU**: NVIDIA GPU with CUDA support
   - **CUDA**: 12.x
   - **Python**: 3.12
   - **编译器**: GCC 11+

---

### 第二步：安装系统依赖（GCC Wrapper）

**关键步骤**：这个 GCC wrapper 解决了 vLLM 在 Ray 子进程中编译 CUDA 工具时的链接错误。

```bash
# 在新系统上创建 GCC wrapper
sudo bash -c 'cat > /usr/local/bin/gcc-wrapper << '\''EOF'\''
#!/bin/bash
# GCC wrapper to automatically add CUDA stubs library path
# This fixes vLLM compilation issues in Ray workers

args=("$@")
if [[ " ${args[@]} " =~ " -lcuda " ]]; then
    new_args=()
    for arg in "${args[@]}"; do
        if [[ "$arg" == "-lcuda" ]]; then
            new_args+=("-L/usr/local/cuda/lib64/stubs")
        fi
        new_args+=("$arg")
    done
    exec /usr/bin/gcc "${new_args[@]}"
else
    exec /usr/bin/gcc "$@"
fi
EOF'

# 赋予执行权限
sudo chmod +x /usr/local/bin/gcc-wrapper

# 验证安装
/usr/local/bin/gcc-wrapper --version
```

**为什么需要这个？**
- vLLM 在初始化时会在 Ray 子进程中动态编译 CUDA 工具
- 标准 GCC 找不到 `libcuda.so`（只有 stub 版本可用于编译）
- 这个 wrapper 自动添加 `-L/usr/local/cuda/lib64/stubs` 参数

---

### 第三步：配置项目路径

1. **复制配置模板**
   ```bash
   cd /path/to/verl_Uky
   cp git_ignore.py.example git_ignore.py
   ```

2. **编辑配置文件**
   ```bash
   nano git_ignore.py
   ```

   修改这两个变量：
   ```python
   # 修改为你的实际路径
   USER_DATA_BASE = Path("/your/data/path")
   MODEL_BASE = Path("/your/models/path")
   ```

3. **验证配置**
   ```bash
   python git_ignore.py
   ```

   应该输出类似：
   ```
   ✓ Configuration valid
   ✓ Data path: /your/data/path
   ✓ Model path: /your/models/path
   ```

---

### 第四步：验证环境

1. **检查 CUDA**
   ```bash
   python3 -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0))"
   ```

   预期输出：
   ```
   CUDA available: True
   GPU: NVIDIA RTX A6000 (或你的 GPU 型号)
   ```

2. **检查 GCC wrapper**
   ```bash
   source /path/to/verl_Uky/.vllm_env
   echo "CC=$CC"
   $CC --version
   ```

   预期输出应包含 `/usr/local/bin/gcc-wrapper`

3. **测试编译**
   ```bash
   source /path/to/verl_Uky/.vllm_env
   echo 'int main() { return 0; }' | $CC -x c - -o /tmp/test -lcuda
   echo "Test result: $?"
   rm /tmp/test
   ```

   预期输出：`Test result: 0`

---

### 第五步：运行训练

```bash
cd /path/to/verl_Uky/examples/grpo_trainer
./run_qwen2_5_vl-3b_fake_dataset.sh
```

---

## 🔍 故障排查

### 问题 1: `-lcuda: No such file or directory`

**症状**: GCC 链接错误，找不到 libcuda

**原因**: GCC wrapper 未安装或未生效

**解决**:
1. 检查 wrapper 是否存在：`ls -l /usr/local/bin/gcc-wrapper`
2. 检查环境变量：`echo $CC`
3. 重新安装 wrapper（见第二步）

### 问题 2: `CUDA driver is a stub library`

**症状**: PyTorch 警告 CUDA 驱动是 stub 库

**原因**: `LD_LIBRARY_PATH` 中包含了 stubs 路径

**解决**:
1. 检查：`echo $LD_LIBRARY_PATH`
2. 确保 stubs **不在** `LD_LIBRARY_PATH` 中
3. 只有 `CC` 环境变量应指向 wrapper

### 问题 3: Ray OOM (Out of Memory)

**症状**: Ray 杀掉 workers，显示内存不足

**原因**:
- 容器内存限制太小（< 128GB）
- Batch size 太大

**解决**:
1. 检查可用内存：`free -h`
2. 检查容器限制：`cat /sys/fs/cgroup/memory/memory.limit_in_bytes`
3. 如果容器 < 128GB，考虑：
   - 重新租用更大内存的实例
   - 减少 `train_batch_size` 和 `ppo_mini_batch_size`
   - 启用 CPU offload（会降低训练速度）

### 问题 4: `git_ignore.py not found`

**症状**: 脚本报错找不到配置文件

**解决**:
```bash
cp git_ignore.py.example git_ignore.py
nano git_ignore.py  # 配置路径
```

---

## 📋 完整检查清单

在新系统上部署前，确认：

- [ ] 系统有至少 128GB RAM
- [ ] CUDA 和 GPU 驱动已安装
- [ ] 已复制完整的 `verl_Uky` 文件夹
- [ ] 已安装 GCC wrapper 到 `/usr/local/bin/gcc-wrapper`
- [ ] 已创建并配置 `git_ignore.py`
- [ ] 运行 `python git_ignore.py` 无错误
- [ ] 运行 CUDA 测试成功
- [ ] 运行 GCC wrapper 测试成功

---

## 🎯 快速迁移命令（一键复制）

```bash
# 1. 在旧系统上打包
cd /path/to
tar czf verl_backup.tar.gz verl_Uky/

# 2. 传输到新系统
scp verl_backup.tar.gz user@new-host:/path/to/

# 3. 在新系统上解压
cd /path/to
tar xzf verl_backup.tar.gz

# 4. 安装 GCC wrapper（需要 sudo）
sudo bash -c 'cat > /usr/local/bin/gcc-wrapper << '\''EOF'\''
#!/bin/bash
args=("$@")
if [[ " ${args[@]} " =~ " -lcuda " ]]; then
    new_args=()
    for arg in "${args[@]}"; do
        if [[ "$arg" == "-lcuda" ]]; then
            new_args+=("-L/usr/local/cuda/lib64/stubs")
        fi
        new_args+=("$arg")
    done
    exec /usr/bin/gcc "${new_args[@]}"
else
    exec /usr/bin/gcc "$@"
fi
EOF'
sudo chmod +x /usr/local/bin/gcc-wrapper

# 5. 配置路径
cd verl_Uky
cp git_ignore.py.example git_ignore.py
nano git_ignore.py  # 手动编辑路径

# 6. 验证
python git_ignore.py
source .vllm_env
echo "CC=$CC"

# 7. 开始训练！
cd examples/grpo_trainer
./run_qwen2_5_vl-3b_fake_dataset.sh
```

---

## 📚 相关文档

- `.vllm_env_README.md` - vLLM 环境变量详细说明
- `PATH_MIGRATION_NOTE.txt` - 路径配置系统说明
- `QUICK_SETUP_GUIDE.md` - 快速设置指南

---

## 💡 提示

1. **内存要求**：3B 模型训练需要 ~80-120GB RAM（取决于 batch size 和配置）
2. **GPU 显存**：至少 24GB（推荐 48GB）
3. **GCC wrapper** 是可移植的，只需要在系统级安装一次
4. **环境变量** 由 `.vllm_env` 自动管理，无需手动设置

---

**如有问题，请查看故障排查部分或提交 issue！** 🚀

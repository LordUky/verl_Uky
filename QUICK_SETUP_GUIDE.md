# 快速设置指南 / Quick Setup Guide

## 🚀 新环境部署（3步完成）/ Deploy in New Environment (3 Steps)

### 步骤 1: 拉取代码 / Step 1: Pull Code
```bash
git pull
```

### 步骤 2: 配置路径 / Step 2: Configure Paths
```bash
# 复制配置模板
cp git_ignore.py.example git_ignore.py

# 编辑你的路径（修改这两个变量即可）
nano git_ignore.py
```

在 `git_ignore.py` 中修改：
```python
# 修改这两行为你的实际路径
USER_DATA_BASE = Path("/your/userdata/path")
MODEL_BASE = Path("/your/models/path")
```

### 步骤 3: 验证并开始 / Step 3: Verify and Start
```bash
# 验证配置
python git_ignore.py

# 开始训练！
./quick_start_fake_vlm.sh
```

---

## 📋 常见路径配置示例 / Common Path Examples

### 示例 1: GPFS环境
```python
USER_DATA_BASE = Path("/gpfs/projects/p32509/userdata/your_username")
MODEL_BASE = Path("/home/your_username/models")
```

### 示例 2: 本地环境
```python
USER_DATA_BASE = Path("/home/your_username/projects")
MODEL_BASE = Path("/home/your_username/models")
```

### 示例 3: 共享集群
```python
USER_DATA_BASE = Path("/scratch/your_username/data")
MODEL_BASE = Path("/shared/models")
```

---

## ❓ 常见问题 / FAQ

### Q: 出现 "git_ignore.py not found" 错误
**A:** 运行 `cp git_ignore.py.example git_ignore.py`

### Q: 如何查看当前配置？
**A:** 运行 `python git_ignore.py`

### Q: 如何更新路径？
**A:** 编辑 `git_ignore.py` 文件

### Q: git_ignore.py 会被提交吗？
**A:** 不会！它在 .gitignore 中被排除

### Q: 如何在shell脚本中使用配置？
**A:** 参考 [quick_start_fake_vlm.sh](quick_start_fake_vlm.sh) 示例

---

## 📚 详细文档 / Detailed Documentation

- [PATH_CONFIG_README.md](PATH_CONFIG_README.md) - 完整使用指南
- [PATH_REFACTORING_SUMMARY.md](PATH_REFACTORING_SUMMARY.md) - 重构详情

---

## ✅ 检查清单 / Checklist

在新环境中部署时，确保：

- [ ] `git pull` 拉取最新代码
- [ ] `cp git_ignore.py.example git_ignore.py` 创建配置
- [ ] 编辑 `git_ignore.py` 中的 `USER_DATA_BASE` 和 `MODEL_BASE`
- [ ] `python git_ignore.py` 验证配置（无错误）
- [ ] 测试运行脚本

---

## 🎯 一行命令设置 / One-Line Setup

```bash
git pull && cp git_ignore.py.example git_ignore.py && echo "现在编辑 git_ignore.py 文件配置你的路径！"
```

---

**就这么简单！/ That's it!** 🎉

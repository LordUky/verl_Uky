#!/usr/bin/env python3
"""打印前8条数据的详细信息"""

import pandas as pd
import os
import re
import sys
from pathlib import Path

# Import project paths
try:
    from git_ignore import DATA_OUTPUT_DIR
    data_dir = DATA_OUTPUT_DIR
except ImportError:
    print("WARNING: git_ignore.py not found. Please copy git_ignore.py.example to git_ignore.py and configure your paths.")
    # Fallback to project root
    data_dir = Path(__file__).parent
train_file = data_dir / "train.parquet"

print("=" * 80)
print("多模态数据验证 - 前8条数据详情")
print("=" * 80)
print(f"\n数据文件: {train_file}")
print(f"文件大小: {train_file.stat().st_size / 1024:.2f} KB\n")

df = pd.read_parquet(train_file)
print(f"✓ 成功加载 {len(df)} 条数据\n")

# 显示前8条数据
num_samples = min(8, len(df))

for idx in range(num_samples):
    sample = df.iloc[idx]

    print("=" * 80)
    print(f"样本 {idx + 1}/{num_samples}")
    print("=" * 80)

    # 基本信息
    extra_info = sample['extra_info']
    print(f"\n【ID】: {extra_info['id']}")
    print(f"【类别】: {extra_info.get('category', 'N/A')}")
    print(f"【格式】: {extra_info.get('format', 'N/A')}")

    # Prompt 内容
    prompt = sample['prompt'][0]
    print(f"\n【Prompt】:")
    print("-" * 80)
    content = prompt['content']
    # 高亮 <image> 标签
    highlighted = content.replace('<image>', ' 🖼️<image>🖼️ ')
    print(highlighted)
    print("-" * 80)

    # 图片信息
    images = sample['images']
    print(f"\n【图片】 (共 {len(images)} 张):")
    for i, img_path in enumerate(images):
        exists = "✓" if os.path.exists(img_path) else "❌"
        # 只显示文件名，路径太长了
        filename = Path(img_path).name
        print(f"  {exists} [{i+1}] .../{filename}")

    # 奖励信息
    reward_model = sample['reward_model']
    print(f"\n【答案】: {reward_model.get('ground_truth')}")
    print(f"【评分】: {reward_model.get('style')}")
    print(f"【选项数】: {reward_model.get('num_choices')}")

    # 验证
    image_tag_count = content.count('<image>')
    image_count = len(images)
    match = "✓" if image_tag_count == image_count else "❌"
    print(f"\n【验证】: {match} <image>标签数({image_tag_count}) == 图片数({image_count})")

    print("\n")

print("=" * 80)
print("数据统计")
print("=" * 80)

# 统计信息
image_counts = df['images'].apply(len)
answers = df['reward_model'].apply(lambda x: x.get('ground_truth'))
image_tag_counts = df.apply(lambda row: row['prompt'][0]['content'].count('<image>'), axis=1)

print(f"\n总样本数: {len(df)}")
print(f"\n图片数量分布:")
print(f"  最小: {image_counts.min()}")
print(f"  最大: {image_counts.max()}")
print(f"  平均: {image_counts.mean():.2f}")

print(f"\n答案分布:")
for ans, count in answers.value_counts().items():
    print(f"  {ans}: {count} ({count/len(df)*100:.1f}%)")

print(f"\n<image>标签统计:")
print(f"  最小: {image_tag_counts.min()}")
print(f"  最大: {image_tag_counts.max()}")
print(f"  平均: {image_tag_counts.mean():.2f}")

# 检查数据完整性
all_image_paths = set()
for images in df['images']:
    all_image_paths.update(images)

missing_images = [img for img in all_image_paths if not os.path.exists(img)]
mismatch_count = sum(1 for _, row in df.iterrows()
                    if row['prompt'][0]['content'].count('<image>') != len(row['images']))

print(f"\n唯一图片数: {len(all_image_paths)}")
print(f"缺失图片: {len(missing_images)}")
print(f"标签-图片不匹配样本: {mismatch_count}")

print("\n" + "=" * 80)
if missing_images == [] and mismatch_count == 0:
    print("✅ 所有检查通过！数据格式正确，可以开始训练。")
else:
    print("⚠️  发现问题，请检查数据。")
print("=" * 80)

print("\n\n" + "=" * 80)
print("verl 数据处理流程示例 (样本1)")
print("=" * 80)

sample = df.iloc[0]
content = sample['prompt'][0]['content']
images = sample['images']

print("\n【步骤1】原始 Prompt:")
print(f"  {content[:100]}...")

print("\n【步骤2】verl 将 <image> 分割为多模态格式:")
segments = re.split("(<image>)", content)
segments = [item for item in segments if item != ""]

content_list = []
for segment in segments:
    if segment == "<image>":
        content_list.append({"type": "image"})
    else:
        content_list.append({"type": "text", "text": segment})

print(f"  转换为 {len(content_list)} 个元素:")
for i, item in enumerate(content_list[:8]):
    if item['type'] == 'image':
        print(f"    [{i}] IMAGE")
    else:
        text = item['text'][:30].replace('\n', ' ')
        print(f"    [{i}] TEXT: '{text}...'")

print(f"\n【步骤3】加载图片 (共{len(images)}张):")
for i, img in enumerate(images):
    print(f"  [{i}] {Path(img).name}")

print(f"\n【步骤4】获取答案: {sample['reward_model']['ground_truth']}")

print("\n" + "=" * 80)

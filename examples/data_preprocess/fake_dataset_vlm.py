# Copyright 2024 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Preprocess the fake VLM dataset to parquet format for spatial reasoning tasks
"""

import argparse
import json
import os
import re
import sys
from typing import List, Dict, Any

import pandas as pd

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

try:
    from git_ignore import FAKE_DATASET_JSON_STR
except ImportError:
    print("WARNING: git_ignore.py not found. Please copy git_ignore.py.example to git_ignore.py and configure your paths.")
    FAKE_DATASET_JSON_STR = None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_json",
        default=FAKE_DATASET_JSON_STR,
        help="Path to the input JSON file"
    )
    parser.add_argument(
        "--local_save_dir",
        default=".",
        help="The save directory for the preprocessed dataset."
    )
    parser.add_argument(
        "--train_ratio",
        type=float,
        default=1.0,
        help="Ratio of training data (default: 1.0)"
    )

    args = parser.parse_args()

    # Load JSON data
    print(f"Loading data from {args.input_json}")
    with open(args.input_json, 'r') as f:
        raw_data = json.load(f)

    print(f"Loaded {len(raw_data)} samples")

    data_source = "fake_vlm_dataset"

    # Function to extract image paths from text and replace with <image> placeholder
    def extract_and_replace_images(text: str) -> tuple[str, List[str]]:
        """
        Extract image paths from <image>path</image> tags and replace with <image> placeholder.
        Returns: (processed_text, image_paths)
        """
        pattern = r'<image>(.*?)</image>'
        image_paths = re.findall(pattern, text)
        # Replace <image>path</image> with just <image>
        processed_text = re.sub(pattern, '<image>', text)
        return processed_text, image_paths

    # Process each data item
    processed_data = list()
    for key, item in raw_data.items():
        question = item.get("Question", "")
        reasoning = item.get("Reasoning", "")
        choices = item.get("Choices", [])
        category = item.get("category", "")
        format_type = item.get("format", "MCQ")
        answer = item.get("Answer", "A")  # Get Answer field from JSON

        # Extract image paths from question and keep <image> placeholder
        question_text, question_images = extract_and_replace_images(question)

        # Collect all images
        all_images = list()
        all_images.extend(question_images)

        # Format choices
        choice_texts = list()
        if format_type == "MCQ" and choices:
            for i, choice in enumerate(choices):
                if isinstance(choice, str) and '<image>' in choice:
                    # Image-based choice
                    choice_text, choice_images = extract_and_replace_images(choice)
                    all_images.extend(choice_images)
                    choice_texts.append(f"{chr(65+i)}. {choice_text}")
                else:
                    # Text-based choice
                    choice_texts.append(f"{chr(65+i)}. {choice}")

        # Verify images exist
        valid_images = list()
        for img_path in all_images:
            if os.path.exists(img_path):
                valid_images.append(img_path)
            else:
                print(f"Warning: Image not found: {img_path}")

        # Construct prompt - keep <image> placeholders
        if choice_texts:
            prompt_text = f"{question_text}\n\nChoices:\n" + "\n".join(choice_texts) + "\n\nPlease select the correct answer."
        else:
            prompt_text = question_text

        # Use the Answer from JSON
        ground_truth = answer.strip().upper() if answer else "A"

        # Convert image paths to dict format expected by qwen_vl_utils.fetch_image
        images_dict_format = [{"image": img_path} for img_path in valid_images]

        data_item = {
            "data_source": data_source,
            "prompt": [
                {
                    "role": "user",
                    "content": prompt_text,
                }
            ],
            "images": images_dict_format,
            "ability": "spatial_reasoning",
            "reward_model": {
                "style": "rule",
                "ground_truth": ground_truth,
                "num_choices": len(choices)
            },
            "extra_info": {
                "id": key,
                "category": category,
                "format": format_type,
                "reasoning": reasoning,
                "num_images": len(valid_images),
            },
        }

        processed_data.append(data_item)

    print(f"Processed {len(processed_data)} samples")

    # Split into train and test
    num_train = int(len(processed_data) * args.train_ratio)
    train_data = processed_data[:num_train]
    test_data = processed_data[num_train:]

    print(f"Train samples: {len(train_data)}")
    print(f"Test samples: {len(test_data)}")

    # Convert to DataFrame
    train_df = pd.DataFrame(train_data)
    test_df = pd.DataFrame(test_data)

    # Create output directory
    local_save_dir = os.path.expanduser(args.local_save_dir)
    os.makedirs(local_save_dir, exist_ok=True)

    # Save to parquet
    train_path = os.path.join(local_save_dir, "train.parquet")
    test_path = os.path.join(local_save_dir, "test.parquet")

    train_df.to_parquet(train_path)
    test_df.to_parquet(test_path)

    print(f"\nDataset saved to:")
    print(f"  Train: {train_path}")
    print(f"  Test: {test_path}")

    # Print a sample
    if len(train_data) > 0:
        print("\n=== Sample Data ===")
        sample = train_data[0]
        print(f"ID: {sample['extra_info']['id']}")
        print(f"Prompt: {sample['prompt'][0]['content'][:200]}...")
        print(f"Images: {len(sample['images'])} images")
        print(f"Ground truth: {sample['reward_model']['ground_truth']}")

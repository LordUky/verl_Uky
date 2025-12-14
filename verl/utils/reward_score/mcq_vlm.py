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
Reward function for Multiple Choice Question (MCQ) evaluation for VLM spatial reasoning tasks
"""
import re
from typing import Union


def extract_answer(predict_str: str) -> str:
    """
    Extract the answer from model's prediction.
    Looks for patterns like:
    - "The answer is A"
    - "Answer: B"
    - "选择 C"
    - Just "A" or "B" etc.
    """
    predict_str = predict_str.strip()

    # Pattern 1: Look for "answer is X" or "Answer: X"
    pattern1 = re.compile(r'(?:answer\s+is|answer:)\s*([A-Za-z])', re.IGNORECASE)
    match = pattern1.search(predict_str)
    if match:
        return match.group(1).upper()

    # Pattern 2: Look for standalone letter at the end
    pattern2 = re.compile(r'\b([A-Za-z])\b\s*$')
    match = pattern2.search(predict_str)
    if match:
        return match.group(1).upper()

    # Pattern 3: Look for first capital letter option
    pattern3 = re.compile(r'\b([A-D])\b')
    match = pattern3.search(predict_str)
    if match:
        return match.group(1).upper()

    # If no pattern matches, return the first letter if it's short enough
    if len(predict_str) <= 3:
        for char in predict_str:
            if char.upper() in ['A', 'B', 'C', 'D']:
                return char.upper()

    return ""


def compute_score(predict_str: str, ground_truth: str, **kwargs) -> float:
    """
    Compute reward score for MCQ.

    Args:
        predict_str: Model's prediction string
        ground_truth: Correct answer (e.g., "A", "B", "C", "D")
        **kwargs: Additional arguments (e.g., num_choices)

    Returns:
        1.0 if correct, 0.0 if incorrect
    """
    # Extract answer from prediction
    predicted_answer = extract_answer(predict_str)

    # Normalize ground truth
    ground_truth = ground_truth.strip().upper()

    # Compare
    if predicted_answer == ground_truth:
        return 1.0
    else:
        return 0.0


def compute_score_with_format(
    predict_str: str,
    ground_truth: str,
    format_score_weight: float = 0.1,
    **kwargs
) -> float:
    """
    Compute reward score with format checking.

    Args:
        predict_str: Model's prediction string
        ground_truth: Correct answer
        format_score_weight: Weight for format score (default: 0.1)
        **kwargs: Additional arguments

    Returns:
        Weighted sum of accuracy and format score
    """
    # Accuracy score
    acc_score = compute_score(predict_str, ground_truth, **kwargs)

    # Format score: check if the response is well-formatted
    format_score = 0.0

    # Check if response contains reasoning or explanation
    if len(predict_str) > 10:  # Has some explanation
        format_score += 0.5

    # Check if response explicitly states the answer
    if re.search(r'(?:answer|选择)', predict_str, re.IGNORECASE):
        format_score += 0.5

    # Combine scores
    final_score = (1.0 - format_score_weight) * acc_score + format_score_weight * format_score

    return final_score

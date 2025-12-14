#!/usr/bin/env python3
"""
Test script for MCQ VLM reward function
测试 MCQ 奖励函数
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from verl.utils.reward_score.mcq_vlm import compute_score, extract_answer

def test_extract_answer():
    """测试答案提取函数"""
    print("=" * 60)
    print("测试答案提取函数")
    print("=" * 60)

    test_cases = [
        ("The answer is A", "A"),
        ("Answer: B", "B"),
        ("I think the correct choice is C", "C"),
        ("Based on the analysis, I choose D", "D"),
        ("选择 A", "A"),
        ("正确答案是 B", "B"),
        ("A", "A"),
        ("The answer is A.", "A"),
        ("After careful consideration, the answer is B because...", "B"),
        ("Let me think step by step:\n1. ...\n2. ...\nTherefore, the answer is C", "C"),
    ]

    passed = 0
    failed = 0

    for i, (input_text, expected) in enumerate(test_cases, 1):
        result = extract_answer(input_text)
        status = "✓" if result == expected else "✗"

        if result == expected:
            passed += 1
        else:
            failed += 1

        print(f"{status} 测试 {i}: 输入='{input_text[:50]}...'")
        print(f"   期望='{expected}', 得到='{result}'")

    print(f"\n总结: {passed} 通过, {failed} 失败")
    print()


def test_compute_score():
    """测试奖励计算函数"""
    print("=" * 60)
    print("测试奖励计算函数")
    print("=" * 60)

    test_cases = [
        ("The answer is A", "A", 1.0),
        ("The answer is B", "A", 0.0),
        ("Answer: C", "C", 1.0),
        ("I choose D", "D", 1.0),
        ("The correct answer is A", "B", 0.0),
        ("A", "A", 1.0),
        ("B", "A", 0.0),
    ]

    passed = 0
    failed = 0

    for i, (predict, ground_truth, expected_score) in enumerate(test_cases, 1):
        score = compute_score(predict, ground_truth)
        status = "✓" if abs(score - expected_score) < 0.01 else "✗"

        if abs(score - expected_score) < 0.01:
            passed += 1
        else:
            failed += 1

        print(f"{status} 测试 {i}:")
        print(f"   预测='{predict}'")
        print(f"   真值='{ground_truth}'")
        print(f"   期望分数={expected_score}, 得到分数={score}")

    print(f"\n总结: {passed} 通过, {failed} 失败")
    print()


def test_edge_cases():
    """测试边界情况"""
    print("=" * 60)
    print("测试边界情况")
    print("=" * 60)

    edge_cases = [
        ("", "A", "空字符串"),
        ("No answer provided", "A", "没有答案"),
        ("X Y Z", "A", "无效选项"),
        ("ABCD", "A", "多个字母"),
        ("The answer could be A or B", "A", "模糊答案"),
    ]

    for i, (predict, ground_truth, description) in enumerate(edge_cases, 1):
        extracted = extract_answer(predict)
        score = compute_score(predict, ground_truth)

        print(f"测试 {i}: {description}")
        print(f"   输入: '{predict}'")
        print(f"   提取: '{extracted}'")
        print(f"   分数: {score}")
        print()


def interactive_test():
    """交互式测试"""
    print("=" * 60)
    print("交互式测试 (输入 'quit' 退出)")
    print("=" * 60)

    while True:
        print()
        predict = input("输入模型预测 (或 'quit' 退出): ").strip()
        if predict.lower() == 'quit':
            break

        ground_truth = input("输入正确答案 (A/B/C/D): ").strip().upper()
        if not ground_truth:
            ground_truth = "A"

        extracted = extract_answer(predict)
        score = compute_score(predict, ground_truth)

        print(f"\n结果:")
        print(f"  提取的答案: {extracted if extracted else '(未提取到)'}")
        print(f"  正确答案: {ground_truth}")
        print(f"  是否正确: {'是' if score > 0.5 else '否'}")
        print(f"  奖励分数: {score}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("MCQ VLM Reward Function 测试")
    print("=" * 60 + "\n")

    # Run all tests
    test_extract_answer()
    test_compute_score()
    test_edge_cases()

    # Interactive mode
    choice = input("是否进入交互式测试? (y/N): ").strip().lower()
    if choice == 'y':
        interactive_test()

    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60 + "\n")

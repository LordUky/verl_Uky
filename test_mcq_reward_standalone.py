#!/usr/bin/env python3
"""
Standalone test script for MCQ VLM reward function
独立测试脚本 - 不需要导入 verl
"""

import re


def extract_answer(predict_str: str) -> str:
    """
    Extract the answer from model's prediction.
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
    """
    predicted_answer = extract_answer(predict_str)
    ground_truth = ground_truth.strip().upper()

    if predicted_answer == ground_truth:
        return 1.0
    else:
        return 0.0


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

        display_text = input_text[:50] + "..." if len(input_text) > 50 else input_text
        print(f"{status} 测试 {i}: 输入='{display_text}'")
        print(f"   期望='{expected}', 得到='{result}'")

    print(f"\n总结: {passed} 通过, {failed} 失败")
    print()
    return passed, failed


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
    return passed, failed


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
    total_passed = 0
    total_failed = 0

    passed, failed = test_extract_answer()
    total_passed += passed
    total_failed += failed

    passed, failed = test_compute_score()
    total_passed += passed
    total_failed += failed

    test_edge_cases()

    # Summary
    print("=" * 60)
    print(f"总测试结果: {total_passed} 通过, {total_failed} 失败")
    print("=" * 60)

    if total_failed == 0:
        print("✓ 所有测试通过! 奖励函数工作正常。")
    else:
        print(f"✗ 有 {total_failed} 个测试失败，请检查。")

    # Interactive mode
    print()
    choice = input("是否进入交互式测试? (y/N): ").strip().lower()
    if choice == 'y':
        interactive_test()

    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60 + "\n")

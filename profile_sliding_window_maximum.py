"""使用 profile 对 sliding_window_maximum 进行性能分析。

运行方式:
    python profile_sliding_window_maximum.py              # 默认运行大规模测试，数组长度 n=100000，窗口大小 k=500
    python profile_sliding_window_maximum.py medium       # 中规模性能分析，数组长度 n=10000，窗口大小 k=100
    python profile_sliding_window_maximum.py large        # 大规模性能分析，数组长度 n=100000，窗口大小 k=500
    python profile_sliding_window_maximum.py wide         # 宽窗口边界测试，数组长度 n=10000，窗口大小 k=9999，接近数组长度
    python profile_sliding_window_maximum.py file         # 完整流程测试，含文件读入与求解，数组长度 n=100000，窗口大小 k=500
"""

import os
import profile
import sys

from sliding_window_maximum import (
    FileInputReader,
    MaxSlidingWindowStrategy,
    sliding_window,
)


def _run(nums, k):
    """统一调用待测核心函数。"""
    return sliding_window(nums, k, MaxSlidingWindowStrategy())


def profile_medium():
    """中规模：n=10000, k=100。"""
    return _run(list(range(10000)), 100)


def profile_large():
    """大规模：n=100000, k=500。"""
    return _run(list(range(100000)), 500)


def profile_wide_window():
    """边界情形：窗口接近数组长度，n=10000, k=9999。"""
    return _run(list(range(10000)), 9999)


def profile_from_file():
    """完整流程：写入临时输入文件，再 profile 读文件 + 求解（n=100000, k=500）。"""
    array_size = 100000
    window_size = 500
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, "_profile_input.txt")

    with open(input_path, "w", encoding="utf-8") as file:
        file.write(" ".join(str(value) for value in range(array_size)))
        file.write(f"\n{window_size}\n")

    try:
        nums, k = FileInputReader(input_path).read()
        return sliding_window(nums, k, MaxSlidingWindowStrategy())
    finally:
        os.remove(input_path)


TEST_CASES = {
    "medium": "profile_medium()",
    "large": "profile_large()",
    "wide": "profile_wide_window()",
    "file": "profile_from_file()",
}


if __name__ == "__main__":
    if len(sys.argv) > 1:
        case = sys.argv[1].lower()
        if case not in TEST_CASES:
            names = ", ".join(TEST_CASES)
            print(f"未知测试规模: {case}，可选: {names}", file=sys.stderr)
            sys.exit(1)
        profile.run(TEST_CASES[case])
    else:
        profile.run("profile_large()")

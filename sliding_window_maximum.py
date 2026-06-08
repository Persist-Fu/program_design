"""求取滑动窗口最大值模块。
"""

from abc import ABC, abstractmethod
import collections
import sys


class InputError(Exception):
    """输入数据缺失、格式错误或无法读取文件。"""


class InputReader(ABC):
    """输入读取抽象；扩展新来源时新增子类，无需修改求解逻辑。"""

    @abstractmethod
    def read(self):
        """返回 (nums, k) 元组。"""

    @abstractmethod
    def describe_source(self):
        """返回输入来源描述字符串。"""


class FileInputReader(InputReader):
    """从固定格式文本文件读取数组与窗口大小 k。
    文件格式：第一行为空格分隔的整数数组，第二行为窗口大小 k。
    """

    def __init__(self, file_path):
        """绑定待读取的文件路径。

        Args:
            file_path: 输入文件路径。
        """
        self._file_path = file_path

    def read(self):
        """从文件中读取数组与滑动窗口大小。

        Returns:
            tuple[list[int], int]: 整数数组 nums 与窗口大小 k。

        Raises:
            InputError: 文件不存在、无法读取、行数不足或内容不是合法整数。
        """
        try:
            # 使用 utf-8-sig 以兼容带 BOM 的 UTF-8 文件，避免首行解析失败。
            with open(self._file_path, encoding="utf-8-sig") as file:
                lines = file.read().strip().splitlines()
        except FileNotFoundError as exc:
            raise InputError(f"找不到输入文件: {self._file_path}") from exc
        except OSError as exc:
            raise InputError(f"无法读取文件: {self._file_path} ({exc})") from exc

        if not lines:
            raise InputError("输入文件为空")

        # 固定两行格式，降低解析歧义。
        if len(lines) < 2:
            raise InputError("输入文件至少需要两行：数组行与窗口大小 k")

        parts = lines[0].split()
        if not parts:
            raise InputError("第一行数组不能为空")
        try:
            nums = [int(value) for value in parts]
        except ValueError as exc:
            raise InputError("第一行须为空格分隔的整数") from exc

        try:
            k = int(lines[1].strip())
        except ValueError as exc:
            raise InputError("第二行须为整数 k") from exc
        if k < 0:
            raise InputError(f"窗口大小 k 不能为负数，当前为 {k}")

        return nums, k

    def describe_source(self):
        """返回 ``file:<路径>`` 形式描述。"""
        return f"file:{self._file_path}"


class SlidingWindowStrategy(ABC):
    """窗口右移时的统计策略。"""

    @abstractmethod
    def initialize(self, nums, k):
        """绑定 nums、k 并初始化内部状态。"""

    @abstractmethod
    def update_window(self, index, value):
        """窗口右端移到 index，纳入 nums[index] 并更新结构。"""

    @abstractmethod
    def get_window_statistic(self):
        """返回当前完整窗口的统计值。"""


class MaxSlidingWindowStrategy(SlidingWindowStrategy):
    """滑动窗口最大值策略（单调递减双端队列存下标）。"""

    def __init__(self):
        self._nums = None
        self._k = 0
        # 选用单调双端队列而非暴力扫描：暴力法每个窗口 O(k)，总复杂度 O(n*k)；
        # 单调队列在入队、出队时均摊 O(1)，整体 O(n)，适合 k 较大或 n 较长的场景。
        self._candidate_indices = collections.deque()

    def initialize(self, nums, k):
        """绑定数组与窗口大小，并清空候选下标队列。

        Args:
            nums: 整数列表。
            k: 窗口大小。
        """
        self._nums = nums
        self._k = k
        self._candidate_indices.clear()

    def update_window(self, index, value):
        """将窗口右端扩展到 index，维护单调递减候选队列。

        Args:
            index: 当前处理的数组下标。
            value: nums[index] 的值。
        """
        # 队首存储的是当前窗口最大值的候选下标；窗口右移后需剔除已滑出左边界的下标（index - k），否则会把过期元素误当作最大值。
        while self._candidate_indices and self._candidate_indices[0] <= index - self._k:
            self._candidate_indices.popleft()

        # 维护单调递减性：若新元素不小于队尾对应值，则队尾元素在本窗口及后续窗口中都不可能成为最大值，可安全弹出。
        # “弹出”的是下标而非数值本身，且每个下标最多入队、出队各一次。
        while (
            self._candidate_indices
            and self._nums[self._candidate_indices[-1]] <= value
        ):
            self._candidate_indices.pop()

        self._candidate_indices.append(index)

    def get_window_statistic(self):
        """返回当前窗口最大值（队首候选下标对应元素）。
        Returns:
            int: 当前完整窗口中的最大值。
        Raises:
            IndexError: 在窗口尚未形成或队列为空时调用。
        """
        return self._nums[self._candidate_indices[0]]


def _validate_nums_k(nums, k):
    """校验 nums、k 的类型与 k 的取值。

    Args:
        nums: 待校验的数组。
        k: 待校验的窗口大小。
    Raises:
        TypeError: nums 不是 list，或元素/k 类型不合法。
        ValueError: k 为负数。
    """
    if not isinstance(nums, list):
        raise TypeError("nums 须为 list")
    if not all(isinstance(x, int) and not isinstance(x, bool) for x in nums):
        raise TypeError("nums 中所有元素必须为 int")
    if not isinstance(k, int) or isinstance(k, bool):
        raise TypeError("k 须为 int")
    if k < 0:
        raise ValueError(f"k 不能为负数，当前为 {k}")


def sliding_window(nums, k, strategy):
    """按给定策略计算滑动窗口统计结果序列。
    本函数只负责统一的窗口右移流程（校验参数、遍历下标、在窗口完整时收集结果），
    具体“窗口内统计什么、如何维护内部结构”由 strategy 决定。

    Args:
        nums: 整数列表。
        k: 窗口大小。
        strategy: SlidingWindowStrategy 的具体实现实例。例如传入 MaxSlidingWindowStrategy() 即计算滑动
            窗口最大值；更换为其它子类可扩展不同统计方式，而无需修改本函数。
    Returns:
        每个完整窗口的统计值组成的列表。
    """
    _validate_nums_k(nums, k)

    # k<=0 或空数组时无完整窗口，直接返回空列表，避免策略层无意义初始化。
    if not nums or k <= 0:
        return []
    # k==1 时每个元素自成一个窗口，结果就是原数组，无需维护 deque。
    if k == 1:
        return nums[:]

    # 策略模式：本函数固定“如何滑动”，strategy 决定“窗口内统计什么”，便于扩展。
    strategy.initialize(nums, k)
    result = []
    for index, value in enumerate(nums):
        strategy.update_window(index, value)
        # 前 k-1 个位置尚未形成完整窗口，从 index == k-1 起队首即为当前窗口最大值。
        if index >= k - 1:
            result.append(strategy.get_window_statistic())

    return result

def main():
    """从文件读取输入，按策略求解并打印结果。
    用法:
        python sliding_window_maximum.py <输入文件路径>
    """
    if len(sys.argv) < 2:
        print(
            "用法: python sliding_window_maximum.py <输入文件路径>",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        nums, k = FileInputReader(sys.argv[1]).read()
        result = sliding_window(nums, k, MaxSlidingWindowStrategy())
    except InputError as exc:
        print(f"输入错误: {exc}", file=sys.stderr)
        sys.exit(1)
    except (TypeError, ValueError) as exc:
        print(f"参数错误: {exc}", file=sys.stderr)
        sys.exit(1)

    print(result)


if __name__ == "__main__":
    main()

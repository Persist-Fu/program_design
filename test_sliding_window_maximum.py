"""使用 unittest 实现设计的黑盒与白盒测试用例。

运行方式:
    python -m unittest test_sliding_window_maximum.py -v
"""

import os
import tempfile
import unittest

from sliding_window_maximum import (
    FileInputReader,
    InputError,
    MaxSlidingWindowStrategy,
    _validate_nums_k,
    sliding_window,
)

NOMINAL_8 = [1, 2, 3, 4, 5, 6, 7, 8]
CLASSIC_NUMS = [1, 3, -1, -3, 5, 3, 6, 7]
CLASSIC_EXPECTED = [3, 3, 5, 5, 6, 7]


class SlidingWindowTestMixin:
    """sliding_window 测试公共 setup。"""

    def setUp(self):
        self.strategy = MaxSlidingWindowStrategy()


class FileReaderTestMixin:
    """FileInputReader 测试公共 setup。"""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

    def _write_input_file(self, content):
        file_path = os.path.join(self.temp_dir.name, "input.txt")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        return file_path


class TestBlackBoxSlidingWindow(SlidingWindowTestMixin, unittest.TestCase):
    """黑盒表 tab:blackbox-sliding-window，BB-SW-1～13。"""

    def test_bb_sw_01_empty_array(self):
        """BB-SW-1：B-V1，nums=[]，k=3。"""
        self.assertEqual(sliding_window([], 3, self.strategy), [])

    def test_bb_sw_02_k_zero(self):
        """BB-SW-2：B-V2，k=0。"""
        self.assertEqual(sliding_window([1, 2, 3], 0, self.strategy), [])

    def test_bb_sw_03_k_larger_than_n(self):
        """BB-SW-3：B-V3，k>n。"""
        self.assertEqual(sliding_window([1, 2], 5, self.strategy), [])

    def test_bb_sw_04_valid_window(self):
        """BB-SW-4：B-V4，1≤k≤n。"""
        self.assertEqual(
            sliding_window(CLASSIC_NUMS, 3, self.strategy), CLASSIC_EXPECTED
        )

    def test_bb_sw_05_k_negative(self):
        """BB-SW-5：B-I1，k<0。"""
        with self.assertRaises(ValueError):
            sliding_window([1, 2, 3], -1, self.strategy)

    def test_bb_sw_06_k_not_int(self):
        """BB-SW-6：B-I2，k 类型非法。"""
        with self.assertRaises(TypeError):
            sliding_window([1, 2, 3], 3.1, self.strategy)

    def test_bb_sw_07_boundary_k_zero_nom(self):
        """BB-SW-7：边界 k=0，n=n_nom。"""
        self.assertEqual(sliding_window(NOMINAL_8, 0, self.strategy), [])

    def test_bb_sw_08_boundary_k_one_nom(self):
        """BB-SW-8：边界 k=1（min+），n=n_nom。"""
        self.assertEqual(sliding_window(NOMINAL_8, 1, self.strategy), NOMINAL_8)

    def test_bb_sw_09_boundary_k_four_nom(self):
        """BB-SW-9：边界 k=4（nom），n=n_nom。"""
        self.assertEqual(
            sliding_window(NOMINAL_8, 4, self.strategy), [4, 5, 6, 7, 8]
        )

    def test_bb_sw_10_boundary_k_seven_nom(self):
        """BB-SW-10：边界 k=7（max-），n=n_nom。"""
        self.assertEqual(sliding_window(NOMINAL_8, 7, self.strategy), [7, 8])

    def test_bb_sw_11_boundary_k_eight_nom(self):
        """BB-SW-11：边界 k=8（max），n=n_nom。"""
        self.assertEqual(sliding_window(NOMINAL_8, 8, self.strategy), [8])

    def test_bb_sw_12_robust_k_nine_nom(self):
        """BB-SW-12：健壮性 k=9（max+），n=n_nom。"""
        self.assertEqual(sliding_window(NOMINAL_8, 9, self.strategy), [])

    def test_bb_sw_13_robust_k_minus_two_nom(self):
        """BB-SW-13：健壮性 k=-2（min-），n=n_nom。"""
        with self.assertRaises(ValueError):
            sliding_window(NOMINAL_8, -2, self.strategy)


class TestBlackBoxFileInputReader(FileReaderTestMixin, unittest.TestCase):
    """黑盒表 tab:blackbox-file-reader，BB-FR-1～9。"""

    def test_bb_fr_01_valid_two_lines(self):
        """BB-FR-1：A-V1 合法两行。"""
        path = self._write_input_file("1 2 3 4 5 6\n3\n")
        nums, k = FileInputReader(path).read()
        self.assertEqual(nums, [1, 2, 3, 4, 5, 6])
        self.assertEqual(k, 3)

    def test_bb_fr_02_file_not_found(self):
        """BB-FR-2：A-I1 文件不存在。"""
        with self.assertRaises(InputError):
            FileInputReader("nonexistent_file.txt").read()

    def test_bb_fr_03_empty_file(self):
        """BB-FR-3：A-I2 空文件。"""
        path = self._write_input_file("")
        with self.assertRaises(InputError):
            FileInputReader(path).read()

    def test_bb_fr_04_non_integer_array(self):
        """BB-FR-4：A-I3 第一行非整数。"""
        path = self._write_input_file("1 a 3\n2\n")
        with self.assertRaises(InputError):
            FileInputReader(path).read()

    def test_bb_fr_05_non_integer_k(self):
        """BB-FR-5：A-I4 第二行非整数。"""
        path = self._write_input_file("1 2 3\nk\n")
        with self.assertRaises(InputError):
            FileInputReader(path).read()

    def test_bb_fr_06_negative_k(self):
        """BB-FR-6：A-I5，$k=-1$。"""
        path = self._write_input_file("1 2 3\n-1\n")
        with self.assertRaises(InputError):
            FileInputReader(path).read()

    def test_bb_fr_07_insufficient_lines(self):
        """BB-FR-7：行数 $=1$。"""
        path = self._write_input_file("1 2 3\n")
        with self.assertRaises(InputError):
            FileInputReader(path).read()

    def test_bb_fr_08_min_valid_lines(self):
        """BB-FR-8：行数 $=2$ 最小合法。"""
        path = self._write_input_file("1\n1\n")
        nums, k = FileInputReader(path).read()
        self.assertEqual(nums, [1])
        self.assertEqual(k, 1)

    def test_bb_fr_09_robust_k_minus_one_n4(self):
        """BB-FR-9：健壮性 $k=-1$（min$-$），$n=4$。"""
        path = self._write_input_file("1 2 3 4\n-1\n")
        with self.assertRaises(InputError):
            FileInputReader(path).read()


class TestWhiteBoxFileInputReader(FileReaderTestMixin, unittest.TestCase):
    """白盒表 tab:whitebox-file-reader，W-F1～F7。"""

    def test_w_f01_success(self):
        """W-F1：基本路径 P1；条件组合（成功分支）。"""
        path = self._write_input_file("1 2 3 4 5 6\n3\n")
        nums, k = FileInputReader(path).read()
        self.assertEqual(nums, [1, 2, 3, 4, 5, 6])
        self.assertEqual(k, 3)

    def test_w_f02_file_not_found(self):
        """W-F2：基本路径 P2；条件组合（文件不可读）。"""
        with self.assertRaises(InputError):
            FileInputReader("nonexistent_file.txt").read()

    def test_w_f03_empty_file(self):
        """W-F3：基本路径 P3；条件组合（空文件）。"""
        path = self._write_input_file("")
        with self.assertRaises(InputError):
            FileInputReader(path).read()

    def test_w_f04_insufficient_lines(self):
        """W-F4：基本路径 P4；条件组合（行数不足）。"""
        path = self._write_input_file("1 2 3\n")
        with self.assertRaises(InputError):
            FileInputReader(path).read()

    def test_w_f05_invalid_array_line(self):
        """W-F5：基本路径 P5；条件组合（第一行非法）。"""
        path = self._write_input_file("1 a 3\n2\n")
        with self.assertRaises(InputError):
            FileInputReader(path).read()

    def test_w_f06_invalid_k_line(self):
        """W-F6：基本路径 P6；条件组合（第二行非法）。"""
        path = self._write_input_file("1 2 3\nk\n")
        with self.assertRaises(InputError):
            FileInputReader(path).read()

    def test_w_f07_negative_k(self):
        """W-F7：基本路径 P7；条件组合（k<0）。"""
        path = self._write_input_file("1 2 3\n-1\n")
        with self.assertRaises(InputError):
            FileInputReader(path).read()


class TestWhiteBoxSlidingWindow(SlidingWindowTestMixin, unittest.TestCase):
    """白盒表 tab:whitebox-sliding-window，W-S1～S19。"""

    def test_w_s01_empty_and_k_zero(self):
        """W-S1：CC-1（判断1，C1T,C2T）。"""
        self.assertEqual(sliding_window([], 0, self.strategy), [])

    def test_w_s02_empty_k_positive(self):
        """W-S2：基本路径 sliding P1；CC-2；循环测试（简单循环 0 次）。"""
        self.assertEqual(sliding_window([], 3, self.strategy), [])

    def test_w_s03_nonempty_k_zero(self):
        """W-S3：基本路径 P1；CC-3；CC-19（判断V4）。"""
        self.assertEqual(sliding_window([1, 2, 3], 0, self.strategy), [])

    def test_w_s04_k_one(self):
        """W-S4：基本路径 sliding P2。"""
        self.assertEqual(sliding_window([5, 2, 8], 1, self.strategy), [5, 2, 8])

    def test_w_s05_loop_no_collect(self):
        """W-S5：基本路径 sliding P3。"""
        self.assertEqual(sliding_window([1, 2], 3, self.strategy), [])

    def test_w_s06_normal_collect(self):
        """W-S6：基本路径 sliding P4；CC-7,15,17（validate 通过）。"""
        self.assertEqual(
            sliding_window(CLASSIC_NUMS, 3, self.strategy), CLASSIC_EXPECTED
        )

    def test_w_s07_k_not_int(self):
        """W-S7：validate P4；基本路径 P5；CC-5（判断V3）。"""
        with self.assertRaises(TypeError):
            sliding_window([1, 2, 3], 3.0, self.strategy)

    def test_w_s08_k_negative(self):
        """W-S8：validate P5；CC-18（判断V4）。"""
        with self.assertRaises(ValueError):
            sliding_window([1, 2, 3], -1, self.strategy)

    def test_w_s09_nums_not_list(self):
        """W-S9：validate P2；CC-14（判断V1）。"""
        with self.assertRaises(TypeError):
            sliding_window((1, 2, 3), 3, self.strategy)

    def test_w_s10_element_invalid(self):
        """W-S10：validate P3；CC-16（判断V2）。"""
        with self.assertRaises(TypeError):
            sliding_window([1, 2.5, 3], 3, self.strategy)

    def test_w_s11_k_is_bool(self):
        """W-S11：CC-6（判断V3，k 为 bool）。"""
        with self.assertRaises(TypeError):
            _validate_nums_k([1, 2, 3], True)

    def test_w_s12_nonempty_k_valid(self):
        """W-S12：CC-4（判断1，双假）。"""
        self.assertEqual(sliding_window([1, 2, 3], 2, self.strategy), [2, 3])

    def test_w_s13_deque_empty_on_first_update(self):
        """W-S13：CC-8,13；循环测试（嵌套 while 不进入）。"""
        strategy = MaxSlidingWindowStrategy()
        strategy.initialize([5], 1)
        strategy.update_window(0, 5)
        self.assertEqual(strategy.get_window_statistic(), 5)

    def test_w_s14_no_head_expiry(self):
        """W-S14：CC-9,11；循环测试（m=4 次；嵌套 while 无队首过期）。"""
        self.assertEqual(
            sliding_window([1, 2, 3, 4], 2, self.strategy), [2, 3, 4]
        )

    def test_w_s15_head_expiry_and_pop(self):
        """W-S15：CC-10,12；循环测试（嵌套 while 过期+pop）。"""
        self.assertEqual(sliding_window([3, 1, 2], 2, self.strategy), [3, 2])

    def test_w_s16_loop_twice(self):
        """W-S16：循环测试（简单循环 2 次迭代）。"""
        self.assertEqual(sliding_window([1, 2], 2, self.strategy), [2])

    def test_w_s17_loop_n_eight(self):
        """W-S17：循环测试（简单循环 n=8 次）。"""
        self.assertEqual(
            sliding_window(NOMINAL_8, 2, self.strategy),
            [2, 3, 4, 5, 6, 7, 8],
        )

    def test_w_s18_loop_n_minus_one(self):
        """W-S18：循环测试（简单循环 n-1=7 次）。"""
        self.assertEqual(
            sliding_window([1, 2, 3, 4, 5, 6, 7], 2, self.strategy),
            [2, 3, 4, 5, 6, 7],
        )

    def test_w_s19_loop_n_plus_one(self):
        """W-S19：循环测试（简单循环 n+1=9 次）。"""
        self.assertEqual(
            sliding_window([1, 2, 3, 4, 5, 6, 7, 8, 9], 2, self.strategy),
            [2, 3, 4, 5, 6, 7, 8, 9],
        )


class TestIntegration(FileReaderTestMixin, unittest.TestCase):
    """读文件与求解联调。"""

    def test_read_and_solve(self):
        path = self._write_input_file("1 2 3 4 5 6\n3\n")
        nums, k = FileInputReader(path).read()
        result = sliding_window(nums, k, MaxSlidingWindowStrategy())
        self.assertEqual(result, [3, 4, 5, 6])


if __name__ == "__main__":
    unittest.main()

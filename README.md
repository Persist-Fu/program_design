# 滑动窗口最大值 — 源代码部分说明

本目录为课程实验主程序及配套脚本。请在**本目录下**运行各命令。

## Python 文件说明

| 文件 | 作用 |
|------|------|
| `sliding_window_maximum.py` | **主程序**。实现文件读入（`FileInputReader`）、滑动窗口策略（`MaxSlidingWindowStrategy`）、驱动函数 `sliding_window` 与命令行入口 `main`。 |
| `test_sliding_window_maximum.py` | **单元测试**。用 `unittest` 实现黑盒、白盒及读文件联调共 57 条用例，与实验报告中的用例表编号对应。 |
| `profile_sliding_window_maximum.py` | **性能分析**。用标准库 `profile` 对核心求解及完整读文件流程做耗时统计。 |

## 运行方式

### 主程序（需指定输入文件）

```bash
python sliding_window_maximum.py 测试数据\classic.txt
```

输入文件格式：第一行为空格分隔的整数数组，第二行为窗口大小 `k`。

### 单元测试

```bash
python -m unittest test_sliding_window_maximum.py -v
```

### 性能分析

```bash
python profile_sliding_window_maximum.py          # 默认 large
python profile_sliding_window_maximum.py medium   # n=10000, k=100
python profile_sliding_window_maximum.py large    # n=100000, k=500
python profile_sliding_window_maximum.py wide     # n=10000, k=9999
python profile_sliding_window_maximum.py file     # 含临时文件读入
```

## 关于测试数据

### `测试数据/` 目录

存放供手动运行主程序使用的示例 `.txt` 文件（如 `classic.txt`、`small.txt` 等）。

### `unittest` 与 `profile` 无需手动准备数据文件

- **`test_sliding_window_maximum.py`**：测试数据写在代码里，或通过 `tempfile` 临时生成输入文件，测完自动清理；不需要事先在 `测试数据/` 下准备文件。
- **`profile_sliding_window_maximum.py`**：`medium` / `large` / `wide` 在内存中用 `list(range(n))` 构造数据；`file` 模式会在本目录临时生成 `_profile_input.txt`，运行结束后自动删除。同样不需要手动维护测试文件。

只有使用 `python sliding_window_maximum.py <文件路径>` 这种方式时，才需要自行准备或使用 `测试数据/` 中的示例文件。

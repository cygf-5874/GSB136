归一化要自己写，不能依赖现成的 Unicode 表。unicodenfc 是 Python 3 的 NFC 归一化库（仅标准库，unittest），自检走 `scripts/check.sh`（`check/` 是固定验收程序，别改），既有用例走 `python tests/run.py`。

`src/nfc.py` 现在只有签名，方法体全抛 `NotImplementedError`；归一化表在 `src/tables.py` 里已经给全。

任务：按 README「对外契约」的 9 条实现 `nfc`、`NFCStream` 与 `nfc_stream`，让既有用例转绿、固定件全过。

验收：
- python -m py_compile src/nfc.py 退出码 0；
- python tests/run.py 全绿；
- bash scripts/check.sh 退出码 0，8 个场景全过（decomp 2 + reorder 2 + compose 2 + idem 1 + stream 1）。

约束：
1. 不改 `check/`、不改 `src/tables.py`；可以新增模块。
2. 对外函数/方法名与签名已定死，不要改；`tests/run.py` 里的用例一条都不许删或改。
3. 只许用 Python 标准库，不许引入任何第三方依赖。
4. 不许 import unicodedata —— 归一化必须走仓库自带的表。
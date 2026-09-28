# unicodenfc

Python 3 的 **NFC 归一化**库（覆盖范围内的拉丁字母与组合记号）。归一化逻辑要自己写，
**不允许**依赖 `unicodedata`；所需数据表随仓库给出。

- 语言/依赖：Python 3（标准库，`unittest`），**无第三方依赖**。
- 入口：`src/nfc.py`（库代码）；数据表 `src/tables.py`（**已给全，勿改**）。
- 自检：`bash scripts/check.sh`（`check/` 是固定验收程序，**勿改**）。
- 既有用例：`python tests/run.py`（unittest）。

## 用法

```bash
python tests/run.py                 # 既有用例
bash scripts/check.sh               # 固定验收（加 -list / --only <组名> 可过滤）
```

对外接口（`src/nfc.py`，签名已定死）：

- `nfc(text: str) -> str`：整串归一化。
- `NFCStream`：增量归一化器；`feed(chunk) -> str` 返回已确定的前缀，`finish() -> str` 返回剩余。
- `nfc_stream(chunks) -> str`：把若干块拼起来做归一化。

## 覆盖范围

归一化表只覆盖下面这些码点；**范围之外的码点原样保留**（不做任何改动，也不抛错）：

- 规范分解键：`U+00C0`–`U+024F` 与 `U+1E00`–`U+1EFF`（拉丁字母及其扩展）；
- 规范组合对：由上述码点的一步规范分解导出（首元素为非组合字符）；
- 结合类：`U+0300`–`U+036F`。

`src/tables.py` 提供三张表：`CANONICAL_DECOMPOSITION`（码点 → 完全规范分解的码点元组）、
`CANONICAL_COMPOSITION`（`(起始码点, 后续码点)` → 组合结果码点）、
`COMBINING_CLASS`（码点 → 非零结合类）。

## 对外契约

1. 覆盖范围如上；对覆盖范围内的 Latin-1 / 拉丁扩展字母与 `U+0300`–`U+036F` 组合记号给出正确的
   NFC 结果，范围之外的码点**原样保留**。
2. **不得 `import unicodedata`**（也不得调用它）；归一化所需数据一律取自 `src/tables.py`。
3. 处理顺序固定为**规范分解 → 规范重排（按结合类，稳定排序）→ 规范组合**，三步顺序不可调换；
   也必须先对整串分解完成后再统一重排，不能边扫边组合。
4. 分块喂入与整串等价：`NFCStream` 依次 `feed` 的返回值再接 `finish`，拼接结果等于对整串做一次
   `nfc`（组合序列可能跨块）。同时 `feed` 必须**尽早**吐出前缀，不许整串缓存到 `finish`——
   对不含组合记号的输入，`feed` 的返回值必须非空。
5. 未覆盖码点原样保留、**不抛错**；`'\x00'`、CJK、ASCII 符号等都要能原样通过。
6. 幂等：对任意输入 `nfc(nfc(x)) == nfc(x)`。
7. 按**码点**处理，不把输入 `encode()`/`decode()` 成 bytes。
8. 空串与纯 ASCII 是恒等（返回原串）。
9. 纯函数：同一输入多次调用结果相同，不依赖任何全局可变状态。

## 目录

```
src/nfc.py          库代码（本次要实现，方法体当前全抛 NotImplementedError）
src/tables.py       归一化数据表（已给全，勿改）
tests/run.py        既有用例（unittest，当前全红）
check/check.py      固定验收程序（8 个场景，勿改）
scripts/check.sh    自检入口
```
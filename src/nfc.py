"""unicodenfc —— 自实现的 NFC 归一化（覆盖范围内的拉丁字母与组合记号）。

对外接口与覆盖范围见 README「对外契约」一节。
本模块**不得**导入 ``unicodedata``；归一化所需的表在 ``src/tables.py`` 里给定。
"""

import tables


def nfc(text):
    """返回 ``text`` 在覆盖范围内的 NFC 归一化结果。

    - ``text``：``str``，按**码点**处理，不 encode/decode 成 bytes。
    - 返回值：``str``，与 ``text`` 等价的 NFC 形式。
    """
    raise NotImplementedError


class NFCStream:
    """分块喂入的增量归一化器：把 ``feed`` 的返回值依次拼接，再接 ``finish``，
    必须等于对整串做一次 :func:`nfc`。"""

    def __init__(self):
        raise NotImplementedError

    def feed(self, chunk):
        """喂入一段文本，返回**已经确定不会再改变**的前缀（可能为空串）。

        组合序列可能跨块，因此尾部未定部分要留在内部状态里；但也不许整串缓存到
        ``finish``——对不含组合记号的输入，``feed`` 必须尽早吐出前缀。
        """
        raise NotImplementedError

    def finish(self):
        """结束喂入，返回仍然保留在内部状态里的剩余部分。"""
        raise NotImplementedError


def nfc_stream(chunks):
    """把可迭代对象 ``chunks`` 里的若干块按顺序拼起来做 NFC。

    等价于 ``nfc(''.join(chunks))``，但内部允许逐块处理。
    """
    raise NotImplementedError
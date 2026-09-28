"""unicodenfc 既有用例（unittest）。

起点：`src/nfc.py` 的方法体全抛 `NotImplementedError`，本文件当前**全红**。
注意：本文件只覆盖少量基本形状，不对固定件的全部场景下断言。**勿改本文件。**
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))

import nfc as lib  # noqa: E402


class NfcTests(unittest.TestCase):
    def test_ascii_identity(self):
        self.assertEqual(lib.nfc("Hello, world!"), "Hello, world!")

    def test_empty_string(self):
        self.assertEqual(lib.nfc(""), "")

    def test_combining_sequence_composes(self):
        self.assertEqual(lib.nfc("e\u0301"), "\u00e9")

    def test_precomposed_stays(self):
        self.assertEqual(lib.nfc("\u00e9"), "\u00e9")

    def test_latin1_letter_with_mark(self):
        self.assertEqual(lib.nfc("A\u030a"), "\u00c5")

    def test_uncovered_codepoint_passthrough(self):
        self.assertEqual(lib.nfc("\u4e2d\u6587"), "\u4e2d\u6587")

    def test_idempotent(self):
        once = lib.nfc("a\u0301\u0323")
        self.assertEqual(lib.nfc(once), once)

    def test_stream_equivalence(self):
        chunks = ["c\u0327", "\u0301"]
        self.assertEqual(lib.nfc_stream(chunks), lib.nfc("".join(chunks)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
#!/usr/bin/env python3
"""unicodenfc 固定验收程序（固定件）。

用法（在仓库根目录）：
  python check/check.py            跑全部场景
  python check/check.py -list      列出全部 `组/名`
  python check/check.py --only <组> 只跑某一组

输出：逐场景 `PASS <组>/<名>` 或 `FAIL <组>/<名>  期望=… 实际=…`，
结尾 `结果：通过 x/N`；全过 exit 0，否则 exit 1；失败不早退。
判据只描述对外可见性质（取值与是否抛错），不使用墙钟 / 随机源。
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, os.pardir, "src"))

import nfc as lib  # noqa: E402


def cps(text):
    return [hex(ord(c)) for c in text]


def show(value):
    if isinstance(value, str):
        text = repr(value)
        if any(ord(c) > 0x7F for c in value):
            text += " " + str(cps(value))
    else:
        text = repr(value)
    return text if len(text) <= 220 else text[:220] + "…"


def expect_equal(expected, actual, label):
    if expected != actual:
        raise AssertionError("%s：期望=%s 实际=%s" % (label, show(expected), show(actual)))


def expect_true(cond, label, actual):
    if not cond:
        raise AssertionError("%s：实际=%s" % (label, show(actual)))


# 覆盖范围内规范稳定的预组合字符（NFC 下应保持自身）。
STABLE = [
    "\u00e9", "\u00c5", "\u1e09", "\u022a", "\u01de", "\u1e08", "\u1e26",
    "\u1ea1", "\u1e63", "\u1e0d", "\u00f1", "\u0100", "\u011e", "\u1e3e",
    "\u0141", "\u00c6", "\u0152", "\u1e97",
]

# 分块喂入的样本：(整串, 切分方式)
SPLITS = [
    ("a\u0301b\u0302c", ["a\u0301", "b\u0302", "c"]),
    ("\u00e9e\u0301", ["\u00e9", "e\u0301"]),
    ("c\u0327\u0301", ["c\u0327", "\u0301"]),
    ("\u1e0b\u0323", ["\u1e0b", "\u0323"]),
    ("\u0301abc", ["\u0301", "ab", "c"]),
    ("\u00c5", ["A", "\u030a"]),
    ("\u4e2d\u6587abc", ["\u4e2d", "\u6587", "abc"]),
]


def sc_decomp_stable():
    for ch in STABLE:
        expect_equal(ch, lib.nfc(ch), "nfc(%s)" % show(ch))


def sc_decomp_expand():
    expect_equal("\u1ea1\u0301", lib.nfc("a\u0301\u0323"), "nfc('a'+acute+dotbelow)")
    expect_equal("\u1e0d\u0307", lib.nfc("\u1e0b\u0323"), "nfc('\\u1e0b'+dotbelow)")
    expect_equal("\u022a", lib.nfc("O\u0308\u0304"), "nfc('O'+diaeresis+macron)")
    expect_equal("\u0301a", lib.nfc("\u0301a"), "nfc(leading acute + 'a')")


def sc_reorder_class():
    expect_equal("\u1ea1\u0301", lib.nfc("a\u0301\u0323"),
                 "dotbelow(220) 排在 acute(230) 前")
    expect_equal("q\u0323\u0307", lib.nfc("q\u0307\u0323"),
                 "dotbelow 与 dotabove 按结合类重排")
    expect_equal("\u00c1\u0300", lib.nfc("A\u0301\u0300"),
                 "同结合类保持输入顺序后再组合")


def sc_reorder_leading():
    expect_equal("\u0334\u0329m", lib.nfc("\u0329\u0334m"),
                 "无前导 starter 的连续组合记号按结合类重排")
    expect_equal("\u0301a", lib.nfc("\u0301a"), "单个前导组合记号原样")


def sc_compose_pair():
    expect_equal("\u00e9", lib.nfc("e\u0301"), "e+acute 组合")
    expect_equal("\u00c5", lib.nfc("A\u030a"), "A+ring 组合")
    expect_equal("\u1e08", lib.nfc("C\u0327\u0301"), "C+cedilla+acute 连续组合")
    expect_equal("\u00f1", lib.nfc("n\u0303"), "n+tilde 组合")
    expect_equal("\u1e26\u0300", lib.nfc("H\u0308\u0300"), "H+diaeresis 组合后残余 grave")


def sc_compose_uncovered():
    expect_equal("\u4e2d\u6587", lib.nfc("\u4e2d\u6587"), "CJK 原样保留")
    expect_equal("@", lib.nfc("@"), "ASCII 符号原样保留")
    expect_equal("\x00", lib.nfc("\x00"), "NUL 原样保留")
    expect_equal("a\u0483", lib.nfc("a\u0483"), "覆盖范围外的组合记号原样保留")
    expect_equal("[\u00e9\u4e2d]", lib.nfc("[\u00e9\u4e2d]"), "覆盖与未覆盖混排")


def sc_idem():
    for s in ["e\u0301", "\u00e9e\u0301", "a\u0301\u0323", "\u1e0b\u0323",
              "\u0329\u0334m", "\u4e2d", ""]:
        once = lib.nfc(s)
        expect_equal(once, lib.nfc(once), "幂等 nfc(nfc(%s))" % show(s))


def sc_stream():
    st = lib.NFCStream()
    head = st.feed("abcdef")
    expect_true(head != "", "对纯 ASCII 长串 feed 必须尽早吐出前缀", head)
    tail = st.finish()
    expect_equal("abcdef", head + tail, "ascii 分块拼接")

    for text, chunks in SPLITS:
        expect_equal(lib.nfc(text), lib.nfc_stream(chunks),
                     "nfc_stream 等价：%s" % show(text))
        st = lib.NFCStream()
        parts = [st.feed(c) for c in chunks]
        parts.append(st.finish())
        expect_equal(lib.nfc(text), "".join(parts),
                     "NFCStream 分块拼接等价：%s" % show(text))


SCENARIOS = [
    ("decomp", "precomposed-stable", "预组合字符在 NFC 下保持自身", sc_decomp_stable),
    ("decomp", "expand-and-recompose", "先完全分解再重新组合", sc_decomp_expand),
    ("reorder", "class-order", "按结合类重排", sc_reorder_class),
    ("reorder", "leading-marks", "无前导 starter 的组合记号重排", sc_reorder_leading),
    ("compose", "base-plus-mark", "起始码点与后续记号组合", sc_compose_pair),
    ("compose", "uncovered-passthrough", "未覆盖码点原样保留不抛错", sc_compose_uncovered),
    ("idem", "stable", "nfc 幂等", sc_idem),
    ("stream", "chunk-equivalence", "分块喂入与整串等价", sc_stream),
]


def main(argv):
    list_only = "-list" in argv or "--list" in argv
    only = None
    if "--only" in argv:
        idx = argv.index("--only")
        if idx + 1 >= len(argv):
            sys.stderr.write("--only 缺少取值\n")
            return 2
        only = argv[idx + 1]

    if list_only:
        for group, name, _expect, _run in SCENARIOS:
            sys.stdout.write("%s/%s\n" % (group, name))
        return 0

    passed = 0
    ran = 0
    for group, name, expect, run in SCENARIOS:
        if only is not None and group != only:
            continue
        ran += 1
        label = "%s/%s" % (group, name)
        try:
            run()
            passed += 1
            sys.stdout.write("PASS %s\n" % label)
        except Exception as exc:  # noqa: BLE001
            detail = "%s: %s" % (type(exc).__name__, exc)
            sys.stdout.write("FAIL %s  期望=%s 实际=%s\n" % (label, expect, show(detail)))

    if ran == 0:
        sys.stdout.write("结果：通过 0/0（没有匹配的场景：--only %s）\n" % only)
        return 1

    sys.stdout.write("结果：通过 %d/%d\n" % (passed, ran))
    return 0 if passed == ran else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
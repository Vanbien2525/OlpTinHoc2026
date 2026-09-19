#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BỘ CHẤM — Luyện ICPC, Buổi 14 (bản Python), 10 bài A..J

Cách dùng nhanh (xem HUONG_DAN.md để đọc đầy đủ):
    python cham.py A                  chấm bài A bằng file bai01.py trong thư mục hiện tại
    python cham.py A my_code.py       chấm bài A bằng file bất kỳ
    python cham.py bai03.py           tự nhận ra bài C từ tên file
    python cham.py --all --dir bai_nop/    chấm cả 10 bài (bai01.py .. bai10.py)
    python cham.py --list             liệt kê 10 bài, giới hạn, tên file mặc định
    python cham.py --selftest         tự kiểm tra bộ chấm bằng các bài mẫu đúng/sai

Kết luận chuẩn: AC, WA, TLE, RE, MLE (ý nghĩa ở HUONG_DAN.md).
Sai định dạng vào/ra được kết luận là WA và ghi rõ "SAI ĐỊNH DẠNG".
Yêu cầu: Python >= 3.9. Chỉ dùng thư viện chuẩn.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import random
import string
from collections import Counter, deque
from dataclasses import dataclass, field
from fractions import Fraction

MB = 1024 * 1024
IS_WIN = os.name == "nt"
OUT_CAP = 64 * MB          # output lớn hơn mức này thì dừng chương trình
AS_SLACK_MB = 256          # (Linux) lưới an toàn: giới hạn địa chỉ ảo = ML + 256 MB
POLL = 0.001               # chu kỳ kiểm tra tiến trình (giây)

# ════════════════════════════════════════════════════════════════════
#  MÀU SẮC / IN ẤN
# ════════════════════════════════════════════════════════════════════
USE_COLOR = False
VCOL = {"AC": "1;32", "WA": "1;31", "TLE": "1;35", "RE": "1;31", "MLE": "1;36"}
VDESC = {
    "AC": "Đúng hoàn toàn (kết quả và định dạng)",
    "WA": "Sai kết quả hoặc sai định dạng vào/ra",
    "TLE": "Quá thời gian",
    "RE": "Lỗi khi chạy",
    "MLE": "Quá bộ nhớ",
}


def paint(s, code):
    return "\033[%sm%s\033[0m" % (code, s) if USE_COLOR else s


def dim(s):
    return paint(s, "2")


def vtag(v):
    return paint(v, VCOL.get(v, "0"))


# ════════════════════════════════════════════════════════════════════
#  KIỂU DỮ LIỆU
# ════════════════════════════════════════════════════════════════════
@dataclass
class Test:
    label: str
    kind: str            # "đơn giản" | "biên" | "tệ nhất"
    inp: bytes
    exp: bytes
    meta: dict = field(default_factory=dict)


@dataclass
class Problem:
    letter: str
    title: str
    tl: float            # giây
    ml: int              # MB
    fmt: str             # mô tả định dạng kết quả theo đề
    gen: object
    validate: object
    check: object = None

    @property
    def num(self):
        return ord(self.letter) - 64

    @property
    def filename(self):
        return "bai%02d.py" % self.num


@dataclass
class RunResult:
    elapsed: float = 0.0
    code: int = 0
    tle: bool = False
    ole: bool = False
    mem: float = None    # MB, None nếu không đo được
    out: bytes = b""
    err: str = ""
    warn: list = field(default_factory=list)


@dataclass
class TestResult:
    idx: int
    test: Test
    verdict: str
    msgs: list
    run: RunResult


# ════════════════════════════════════════════════════════════════════
#  KIỂM TRA DỮ LIỆU VÀO (validator) — đảm bảo test đúng đặc tả của đề
# ════════════════════════════════════════════════════════════════════
class BadInput(Exception):
    pass


def need(cond, msg):
    if not cond:
        raise BadInput(msg)


INT_RE = re.compile(r"^-?[0-9]+$")


def parse_int(tok, lo, hi, what):
    need(INT_RE.match(tok) is not None, "%s: %r không phải số nguyên" % (what, tok[:20]))
    need(tok == str(int(tok)), "%s: %r có số 0 thừa hoặc '-0'" % (what, tok))
    v = int(tok)
    need(lo <= v <= hi, "%s = %d ngoài khoảng [%d, %d]" % (what, v, lo, hi))
    return v


def ints(line, lo, hi, what):
    return [parse_int(t, lo, hi, what) for t in line.split(" ")]


def split_lines(inp, final_nl=True):
    try:
        t = inp.decode("ascii")
    except UnicodeDecodeError:
        raise BadInput("dữ liệu vào có ký tự ngoài ASCII")
    need("\r" not in t, "dữ liệu vào chứa \\r")
    if t.endswith("\n"):
        t = t[:-1]
    else:
        need(not final_nl, "thiếu \\n ở cuối dữ liệu vào")
    return t.split("\n")


def val_A(inp):
    L = split_lines(inp)
    need(len(L) == 2, "phải có đúng 2 dòng")
    n = parse_int(L[0], 1, 200000, "n")
    a = ints(L[1], -10**9, 10**9, "a_i")
    need(len(a) == n, "số phần tử != n")


def val_B(inp):
    L = split_lines(inp)
    need(len(L) == 1, "phải có đúng 1 dòng")
    v = ints(L[0], -10**9, 10**9, "a,b")
    need(len(v) == 2, "dòng phải có đúng 2 số")


def val_C(inp):
    L = split_lines(inp, final_nl=False)
    total = 0
    for l in L:
        need(l != "", "có dòng trống")
        total += len(ints(l, -10**9, 10**9, "x"))
    need(1 <= total <= 200000, "số lượng số = %d ngoài [1, 2e5]" % total)


ALLOWED_D = set(string.ascii_letters + string.digits + " ")


def val_D(inp):
    L = split_lines(inp, final_nl=False)
    n = parse_int(L[0], 1, 1000, "n")
    need(len(L) == n + 1, "số dòng văn bản != n")
    for i, l in enumerate(L[1:], 1):
        need(1 <= len(l) <= 100, "dòng %d dài %d ký tự (cần 1..100)" % (i, len(l)))
        need(set(l) <= ALLOWED_D, "dòng %d có ký tự ngoài chữ/số/dấu cách" % i)
        need(l[0] != " " and l[-1] != " ", "dòng %d có dấu cách ở đầu/cuối" % i)


def val_E(inp):
    L = split_lines(inp)
    need(len(L) == 2, "phải có đúng 2 dòng")
    n = parse_int(L[0], 1, 10**5, "n")
    a = ints(L[1], -10**6, 10**6, "a_i")
    need(len(a) == n, "số phần tử != n")


def val_F(inp):
    L = split_lines(inp)
    h = ints(L[0], 1, 1000, "n,q")
    need(len(h) == 2, "dòng 1 phải có n và q")
    n, q = h
    need(len(L) == 2 + q, "số dòng != 2 + q")
    need(len(ints(L[1], -10**9, 10**9, "a_i")) == n, "số phần tử != n")
    for l in L[2:]:
        v = ints(l, -10**9, 10**9, "l,r")
        need(len(v) == 2 and v[0] <= v[1], "truy vấn phải có 2 số với l <= r")


def val_G(inp):
    L = split_lines(inp)
    h = ints(L[0], 1, 500, "n,m")
    need(len(h) == 2, "dòng 1 phải có n và m")
    n, m = h
    need(len(L) == 1 + n, "số dòng != 1 + n")
    for l in L[1:]:
        need(len(ints(l, -10**9, 10**9, "giá trị")) == m, "một hàng không đủ m số")


def val_H(inp):
    L = split_lines(inp)
    need(len(L) == 4, "phải có đúng 4 dòng")
    n = parse_int(L[0], 1, 200000, "n")
    need(len(ints(L[1], -10**9, 10**9, "a_i")) == n, "số phần tử != n")
    q = parse_int(L[2], 1, 200000, "q")
    need(len(ints(L[3], -10**9, 10**9, "x")) == q, "số truy vấn != q")


def val_I(inp):
    try:
        t = inp.decode("ascii")
    except UnicodeDecodeError:
        raise BadInput("có ký tự ngoài ASCII")
    if t.endswith("\n"):
        t = t[:-1]
    need("\n" not in t and "\r" not in t, "phải là đúng một dòng")
    need(len(t) <= 10**5, "dòng dài quá 1e5 ký tự")
    need(all(32 <= ord(c) <= 126 for c in t), "có ký tự không in được")


OP_RE = re.compile(r"^(IN [a-z]{1,20}|OUT|SIZE)$")


def val_J(inp):
    L = split_lines(inp)
    n = parse_int(L[0], 1, 200000, "n")
    need(len(L) == n + 1, "số thao tác != n")
    for i, l in enumerate(L[1:], 1):
        need(OP_RE.match(l) is not None, "thao tác %d sai dạng: %r" % (i, l[:30]))


# ════════════════════════════════════════════════════════════════════
#  SINH TEST + ĐÁP ÁN (mỗi bài đúng 5 test)
#  Đáp án tính bằng cách viết ĐỘC LẬP, không dùng lại code mẫu của tài liệu.
# ════════════════════════════════════════════════════════════════════
LOWER = string.ascii_lowercase


def _ints(a):
    return " ".join(map(str, a))


def gen_A():
    R = random.Random(14001)
    T = []

    def add(label, kind, a):
        inp = ("%d\n%s\n" % (len(a), _ints(a))).encode()
        exp = ("%d %d\n" % (sum(a), max(a))).encode()
        T.append(Test(label, kind, inp, exp))

    add("Ví dụ trong đề", "đơn giản", [3, -1, -7, 2, 4])
    add("n = 1, giá trị −10^9", "biên", [-10**9])
    add("Toàn số âm −5 −2 −9 (bẫy khởi tạo max = 0)", "biên", [-5, -2, -9])
    a = [R.randint(-10**9, 10**9) for _ in range(200000)]
    a[0], a[1] = -10**9, 10**9
    add("n = 2·10^5, ngẫu nhiên trong [−10^9, 10^9]", "tệ nhất", a)
    a = [R.randint(-10**9, -1) for _ in range(200000)]
    a[-1] = -10**9
    add("n = 2·10^5, toàn số âm (tổng ≈ −10^14)", "tệ nhất", a)
    return T


def gen_B():
    cases = [
        (10**9, 10**9, "Ví dụ trong đề: 10^9 · 10^9 = 10^18", "đơn giản"),
        (-10**9, 10**9, "Hai số trái dấu, tích = −10^18", "biên"),
        (0, -5, "Có số 0, tích = 0", "biên"),
        (-10**9, -10**9, "Hai số âm cực đại, tích = 10^18", "tệ nhất"),
        (-999999999, 10**9, "Sát biên, tích ≈ −10^18", "tệ nhất"),
    ]
    T = []
    for a, b, label, kind in cases:
        T.append(Test(label, kind, ("%d %d\n" % (a, b)).encode(), ("%d\n" % (a * b)).encode()))
    return T


def gen_C():
    R = random.Random(14003)
    T = []

    def add(label, kind, text, nums):
        T.append(Test(label, kind, text.encode(), ("%d %d\n" % (len(nums), sum(nums))).encode()))

    add("Ví dụ trong đề: 3 số, mỗi số một dòng", "đơn giản", "1\n2\n3\n", [1, 2, 3])
    add("Chỉ một số duy nhất", "biên", "-7\n", [-7])
    rows = [[5, -3], [10], [7, 7, 7], [-10**9, 10**9]]
    add("Số nằm lộn xộn: dòng 2 số, dòng 1 số, dòng 3 số...", "biên",
        "".join(_ints(r) + "\n" for r in rows), [x for r in rows for x in r])
    a = [R.randint(-10**9, 10**9) for _ in range(200000)]
    add("2·10^5 số trên ĐÚNG MỘT dòng", "tệ nhất", _ints(a) + "\n", a)
    a = [10**9] * 200000
    add("2·10^5 số, mỗi số một dòng, KHÔNG có \\n ở cuối file", "tệ nhất", "\n".join(map(str, a)), a)
    return T


def gen_D():
    R = random.Random(14004)
    T = []
    alnum = string.ascii_letters + string.digits

    def add(label, kind, lines, final_nl=True):
        text = "%d\n%s" % (len(lines), "\n".join(lines)) + ("\n" if final_nl else "")
        best = ""
        for l in lines:
            if len(l) > len(best):
                best = l
        T.append(Test(label, kind, text.encode(), (best + "\n").encode()))

    add("Ví dụ trong đề", "đơn giản", ["mot hai", "mot hai ba bon", "xin chao"])
    add("n = 1, dòng chỉ có 1 ký tự", "biên", ["q"])
    add("Hòa: hai dòng cùng dài nhất (lấy dòng TRƯỚC), có 2 dấu cách liền nhau", "biên",
        ["hai  ba", "bon nam", "mot"])
    add("File KHÔNG có \\n ở cuối, dòng cuối dài nhất hơn đúng 1 ký tự", "biên",
        ["abcdefgh", "xyz", "abcdefghi"], final_nl=False)

    def rand_line(length):
        chars = [R.choice(alnum)]
        for _ in range(length - 2):
            chars.append(" " if R.random() < 0.2 else R.choice(alnum))
        if length >= 2:
            chars.append(R.choice(alnum))
        return "".join(chars)

    lines = [rand_line(R.randint(1, 99)) for _ in range(1000)]
    lines[299] = "A" + "  " + "b" * 47 + "   " + "C" * 47          # dài đúng 100, nhiều dấu cách liền nhau
    assert len(lines[299]) == 100 and lines[299][-1] != " "
    lines[699] = rand_line(100)                                    # cũng dài 100: phải bị bỏ qua
    add("n = 1000, dòng dài 100 ký tự xuất hiện 2 lần (lấy lần đầu), có nhiều dấu cách", "tệ nhất", lines)
    return T


def gen_E():
    T = []

    def add(label, kind, a):
        mean = Fraction(sum(a), len(a))
        inp = ("%d\n%s\n" % (len(a), _ints(a))).encode()
        # Đề và code mẫu Python quy định cách in "%.6f" % (tong / n).
        # Sinh đáp án đúng y hệt quy tắc ấy, không tự đặt thêm cách làm tròn khác.
        exp = (("%.6f" % (sum(a) / len(a))) + "\n").encode()
        T.append(Test(label, kind, inp, exp, {"mean": mean}))

    add("Ví dụ trong đề: 7/3 = 2.333333", "đơn giản", [1, 2, 4])
    add("n = 1, giá trị −10^6", "biên", [-10**6])
    add("Tổng bằng 0 (phải in 0.000000)", "biên", [5, -5, 3, -3])
    add("Số âm chia không hết: −10/7", "biên", [-1, -2, -3, 0, 1, -4, -1])
    add("n = 10^5, gần 10^6, trung bình 999999.99999", "tệ nhất", [10**6] * 99999 + [999999])
    return T


def gen_F():
    R = random.Random(14006)
    T = []

    def add(label, kind, a, qs):
        inp = "%d %d\n%s\n%s" % (len(a), len(qs), _ints(a), "".join("%d %d\n" % (l, r) for l, r in qs))
        exp = "".join("%d\n" % sum(1 for x in a if l <= x <= r) for l, r in qs)
        T.append(Test(label, kind, inp.encode(), exp.encode()))

    add("Ví dụ trong đề", "đơn giản", [1, 5, 2, 4, 3], [(1, 3), (5, 5), (6, 10)])
    add("n = q = 1, l = r = giá trị duy nhất", "biên", [-10**9], [(-10**9, -10**9)])
    add("Mọi đầu mút đều là giá trị có thật, có giá trị lặp (bẫy < thay <=)", "biên",
        [10, 10, 20, 30, 30, 30],
        [(10, 30), (10, 10), (30, 30), (20, 20), (11, 29), (31, 40), (5, 9), (10, 20)])
    add("Giá trị và đầu mút ở ±10^9", "biên", [-10**9, 10**9, 0, -10**9, 10**9],
        [(-10**9, 10**9), (-10**9, -10**9), (10**9, 10**9), (-999999999, 999999999), (0, 0), (1, 10**9),
         (-10**9, -1)])
    a = [R.randint(-10**9, 10**9) for _ in range(1000)]
    qs = []
    for i in range(1000):
        if i % 2 == 0:
            l, r = sorted((R.choice(a), R.choice(a)))
        else:
            l, r = sorted((R.randint(-10**9, 10**9), R.randint(-10**9, 10**9)))
        qs.append((l, r))
    qs[0] = (-10**9, 10**9)
    add("n = q = 1000, nửa số đầu mút lấy đúng từ dãy", "tệ nhất", a, qs)
    return T


def gen_G():
    R = random.Random(14007)
    T = []

    def add(label, kind, mat):
        n, m = len(mat), len(mat[0])
        inp = "%d %d\n%s" % (n, m, "".join(_ints(r) + "\n" for r in mat))
        exp = "".join("%d\n" % sum(r) for r in mat)
        T.append(Test(label, kind, inp.encode(), exp.encode()))

    add("Ví dụ trong đề: bảng 2 × 3", "đơn giản", [[1, 2, 3], [4, 5, 6]])
    add("Bảng 1 × 1, giá trị −10^9", "biên", [[-10**9]])
    add("Bảng chỉ có 1 hàng, 500 cột", "biên", [[R.randint(-10**9, 10**9) for _ in range(500)]])
    add("Bảng 500 hàng, chỉ 1 cột (nhầm hàng/cột sẽ sai số dòng)", "biên",
        [[R.randint(-10**9, 10**9)] for _ in range(500)])
    mat = [[R.randint(-10**9, 10**9) for _ in range(500)] for _ in range(500)]
    mat[0] = [10**9] * 500
    mat[1] = [-10**9] * 500
    add("Bảng 500 × 500, có hàng toàn 10^9 và hàng toàn −10^9", "tệ nhất", mat)
    return T


def gen_H():
    R = random.Random(14008)
    T = []

    def add(label, kind, a, qs):
        cnt = Counter(a)
        inp = "%d\n%s\n%d\n%s\n" % (len(a), _ints(a), len(qs), _ints(qs))
        exp = "".join("%d\n" % cnt.get(x, 0) for x in qs)
        T.append(Test(label, kind, inp.encode(), exp.encode()))

    add("Ví dụ trong đề", "đơn giản", [1, 2, 2, 3, 3], [2, 3, 9])
    add("n = q = 1, x trùng với phần tử duy nhất (−10^9)", "biên", [-10**9], [-10**9])
    add("Có số 0 và số âm, có truy vấn không xuất hiện", "biên", [0, 0, 0, -5, -5, 7], [0, -5, 7, 8, -8])
    a = R.sample(range(-10**9, 10**9 + 1), 200000)
    qs = [R.choice(a) if i % 2 == 0 else R.randint(-10**9, 10**9) for i in range(200000)]
    add("n = q = 2·10^5, mọi giá trị đôi một khác nhau (nhân 2 giới hạn = 4·10^10)", "tệ nhất", a, qs)
    pool = [R.randint(-10**9, 10**9) for _ in range(100)] + [-10**9, 10**9, 0]
    a = R.choices(pool, k=200000)
    qs = R.choices(pool + [R.randint(-10**9, 10**9) for _ in range(20)], k=200000)
    add("n = q = 2·10^5, chỉ 103 giá trị khác nhau (lặp rất nhiều)", "tệ nhất", a, qs)
    return T


def gen_I():
    R = random.Random(14009)
    T = []

    def add(label, kind, text, final_nl=True):
        u = sum(1 for c in text if "A" <= c <= "Z")
        lo = sum(1 for c in text if "a" <= c <= "z")
        d = sum(1 for c in text if "0" <= c <= "9")
        o = len(text) - u - lo - d
        inp = text.encode() + (b"\n" if final_nl else b"")
        T.append(Test(label, kind, inp, ("%d %d %d %d\n" % (u, lo, d, o)).encode()))

    add("Ví dụ trong đề: Hello World 123!", "đơn giản", "Hello World 123!")
    add("Dòng RỖNG, file 0 byte (bẫy EOFError của input())", "biên", "", final_nl=False)
    add("Dấu cách ở đầu và cuối phải được đếm", "biên", "   Ab 12 ~   ")
    add("Đủ 95 ký tự ASCII in được (32..126)", "biên", "".join(chr(c) for c in range(32, 127)))
    add("Dòng dài 10^5 ký tự ngẫu nhiên", "tệ nhất", "".join(R.choices([chr(c) for c in range(32, 127)], k=100000)))
    return T


def gen_J():
    R = random.Random(14010)
    T = []

    def add(label, kind, ops):
        q = deque()
        out = []
        for s in ops:
            p = s.split()
            if p[0] == "IN":
                q.append(p[1])
            elif p[0] == "OUT":
                out.append(q.popleft() if q else "EMPTY")
            else:
                out.append(str(len(q)))
        inp = "%d\n%s\n" % (len(ops), "\n".join(ops))
        T.append(Test(label, kind, inp.encode(), "".join(x + "\n" for x in out).encode()))

    add("Ví dụ trong đề", "đơn giản", ["IN an", "IN binh", "OUT", "SIZE", "OUT", "OUT"])
    add("n = 1: OUT khi hàng rỗng, phải in EMPTY", "biên", ["OUT"])
    add("Chỉ toàn IN: không được in gì (kết quả rỗng)", "biên", ["IN an", "IN binh", "IN an"])

    def name(k):
        return "".join(R.choices(LOWER, k=k))

    ops = []
    for _ in range(200000):
        r = R.random()
        if r < 0.45:
            ops.append("IN " + name(R.randint(1, 20)))
        elif r < 0.80:
            ops.append("OUT")
        else:
            ops.append("SIZE")
    add("n = 2·10^5, thao tác ngẫu nhiên, có nhiều lần OUT khi rỗng", "tệ nhất", ops)
    ops = ["IN " + name(20) for _ in range(100000)] + ["OUT"] * 99999 + ["SIZE"]
    add("10^5 lần IN (tên 20 chữ) rồi 99999 lần OUT: hàng dài 10^5 (bẫy list.pop(0))", "tệ nhất", ops)
    return T


# ════════════════════════════════════════════════════════════════════
#  CHẤM KẾT QUẢ (định dạng + giá trị)
# ════════════════════════════════════════════════════════════════════
def norm(b):
    """CRLF -> LF. Trên Windows print() luôn ghi \\r\\n nên không thể coi là lỗi của thí sinh."""
    return b.replace(b"\r\n", b"\n")


def lines_of(b):
    b = norm(b)
    if b.strip(b"\n") == b"":
        return []
    return b.rstrip(b"\n").split(b"\n")


def show(b, width=120):
    s = b.decode("utf-8", "replace") if isinstance(b, bytes) else b
    if len(s) > width:
        s = s[:width] + "…(+%d ký tự)" % (len(s) - width)
    return s


def wa_detail(o, exp):
    ol, el = lines_of(o), lines_of(exp)
    for i in range(min(len(ol), len(el))):
        if ol[i].split() != el[i].split():
            return ["khác đáp án ở dòng %d" % (i + 1), "cần : " + show(el[i]), "nhận : " + show(ol[i])]
    if len(ol) < len(el):
        return ["thiếu dòng: cần %d dòng, chỉ có %d" % (len(el), len(ol)),
                "dòng %d cần: %s" % (len(ol) + 1, show(el[len(ol)]))]
    if len(ol) > len(el):
        return ["thừa dòng: cần %d dòng, có %d" % (len(el), len(ol)),
                "dòng %d thừa: %s" % (len(el) + 1, show(ol[len(el)]))]
    return ["nội dung khác đáp án"]


def analyze_format(o, exp):
    """o, exp đã qua norm(). Trả về danh sách mô tả lỗi định dạng (giá trị đã đúng)."""
    iss = []
    if b"\r" in o:
        iss.append("có ký tự \\r đứng lẻ")
    if o and not o.endswith(b"\n"):
        iss.append("thiếu ký tự xuống dòng ở cuối kết quả")
    tail = len(o) - len(o.rstrip(b"\n"))
    if tail > 1:
        iss.append("thừa %d dòng trống ở cuối kết quả" % (tail - 1))
    ol, el = lines_of(o), lines_of(exp)
    blank = sum(1 for l in ol if l.strip() == b"") - sum(1 for l in el if l.strip() == b"")
    if blank > 0:
        iss.append("có %d dòng trống thừa (ở đầu hoặc xen giữa)" % blank)
    elif len(ol) != len(el):
        iss.append("số dòng khác đáp án: cần %d, có %d (giá trị nằm sai dòng/sai cách ngăn)" % (len(el), len(ol)))
    n_rep = 0
    for i in range(min(len(ol), len(el))):
        l, e = ol[i], el[i]
        if l != e and l.split() == e.split() and n_rep < 3:
            n_rep += 1
            if l.rstrip(b" \t") != l and e.rstrip(b" \t") == e:
                iss.append("dòng %d có dấu cách/tab thừa ở cuối" % (i + 1))
            elif l.lstrip(b" \t") != l and e.lstrip(b" \t") == e:
                iss.append("dòng %d có dấu cách/tab thừa ở đầu" % (i + 1))
            else:
                iss.append("dòng %d: khoảng trắng giữa các phần tử khác đáp án" % (i + 1))
    if not iss:
        iss.append("bố cục khác đáp án")
    return iss


def generic_check(out, test, lenient):
    o, exp = norm(out), test.exp
    if o == exp:
        return "AC", []
    if o.split() != exp.split():
        return "WA", wa_detail(o, exp)
    iss = analyze_format(o, exp)
    if lenient:
        return "AC", ["(--lenient) bỏ qua lỗi định dạng: " + "; ".join(iss)]
    return "WA", ["SAI ĐỊNH DẠNG: " + "; ".join(iss)]


NUM_RE = re.compile(r"^[+-]?([0-9]+\.?[0-9]*|\.[0-9]+)([eE][+-]?[0-9]+)?$")
DEC_RE = re.compile(r"^-?[0-9]+(\.([0-9]+))?$")


def check_E(out, test, lenient):
    """Bài E: đúng giá trị theo %.6f và đúng 6 chữ số sau dấu chấm."""
    o = norm(out)
    if o == test.exp:
        return "AC", []
    toks = o.split()
    if len(toks) != 1:
        return "WA", ["cần đúng 1 số thực, nhận %d phần tử" % len(toks)]
    tok = toks[0].decode("ascii", "replace")
    if not NUM_RE.match(tok):
        return "WA", ["%r không phải số thực hợp lệ" % tok[:30]]
    mean = test.meta["mean"]
    expected_token = test.exp.strip().decode()
    if tok.lstrip("+") == expected_token:
        iss = analyze_format(o, test.exp)
        if tok.startswith("+"):
            iss.insert(0, "không được có dấu '+' phía trước")
        if lenient:
            return "AC", ["(--lenient) bỏ qua lỗi định dạng: " + "; ".join(iss)]
        return "WA", ["SAI ĐỊNH DẠNG: " + "; ".join(iss)]
    if mean == 0 and tok.startswith("-") and tok[1:] == expected_token:
        iss = ["giá trị bằng 0 nhưng in dấu trừ (%s): phải in 0.000000" % tok]
        if lenient:
            return "AC", ["(--lenient) bỏ qua lỗi định dạng: " + "; ".join(iss)]
        return "WA", ["SAI ĐỊNH DẠNG: " + "; ".join(iss)]
    m = DEC_RE.match(tok)
    d = len(m.group(2) or "") if m else None
    v = Fraction(tok)
    tol = Fraction(1, 10**9)
    if d is not None:
        tol = max(tol, Fraction(1, 2 * 10**d))
    if d != 6 and abs(v - mean) <= tol:
        if d is None:
            iss = ["số viết dạng khoa học/dấu '+': cần đúng 6 chữ số sau dấu chấm"]
        else:
            iss = ["cần đúng 6 chữ số sau dấu chấm, nhận %d chữ số (%s)" % (d, tok[:30])]
        if lenient:
            return "AC", ["(--lenient) bỏ qua lỗi định dạng: " + "; ".join(iss)]
        return "WA", ["SAI ĐỊNH DẠNG: " + "; ".join(iss)]
    return "WA", ["giá trị sai", "cần : " + test.exp.decode().strip(), "nhận : " + show(tok)]


PROBLEMS = [
    Problem("A", "Tổng và giá trị lớn nhất", 1.0, 256,
            "1 dòng: tổng và giá trị lớn nhất, cách nhau đúng 1 dấu cách", gen_A, val_A),
    Problem("B", "Tích hai số", 1.0, 256, "1 dòng: một số nguyên (tích a·b)", gen_B, val_B),
    Problem("C", "Đọc tới hết dữ liệu", 1.0, 256,
            "1 dòng: số lượng và tổng, cách nhau đúng 1 dấu cách", gen_C, val_C),
    Problem("D", "Dòng dài nhất", 1.0, 256,
            "1 dòng: dòng dài nhất (giữ nguyên dấu cách bên trong; hòa thì lấy dòng trước)", gen_D, val_D),
    Problem("E", "Trung bình cộng", 1.0, 256,
            "1 dòng: số thực với ĐÚNG 6 chữ số sau dấu chấm", gen_E, val_E, check_E),
    Problem("F", "Đếm trong đoạn", 1.0, 256,
            "q dòng, mỗi truy vấn một số nguyên (số giá trị nằm trong [l, r], kể cả hai đầu)", gen_F, val_F),
    Problem("G", "Tổng từng hàng", 1.0, 256,
            "n dòng, mỗi dòng một tổng, từ hàng đầu tới hàng cuối", gen_G, val_G),
    Problem("H", "Đếm số lần xuất hiện", 1.0, 256,
            "q dòng, mỗi truy vấn một số nguyên (số lần x xuất hiện)", gen_H, val_H),
    Problem("I", "Phân loại ký tự", 1.0, 256,
            "1 dòng: 4 số cách nhau đúng 1 dấu cách: chữ hoa, chữ thường, chữ số, ký tự khác", gen_I, val_I),
    Problem("J", "Mô phỏng hàng đợi", 0.5, 256,
            "mỗi OUT/SIZE in đúng một dòng (tên, EMPTY hoặc số người); IN không in gì", gen_J, val_J),
]
BY_LETTER = {p.letter: p for p in PROBLEMS}
_TEST_CACHE = {}


def get_tests(prob):
    if prob.letter not in _TEST_CACHE:
        tests = prob.gen()
        assert len(tests) == 5, "mỗi bài phải có đúng 5 test"
        for i, t in enumerate(tests, 1):
            try:
                prob.validate(t.inp)
            except BadInput as e:
                raise SystemExit("LỖI BỘ CHẤM: test %d của bài %s vi phạm đặc tả đề: %s" % (i, prob.letter, e))
        _TEST_CACHE[prob.letter] = tests
    return _TEST_CACHE[prob.letter]


# ════════════════════════════════════════════════════════════════════
#  CHẠY CHƯƠNG TRÌNH (đo thời gian + bộ nhớ, giới hạn tài nguyên)
# ════════════════════════════════════════════════════════════════════
def _child_env():
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def _vmhwm_kb(path):
    try:
        with open(path, "rb") as f:
            for line in f:
                if line.startswith(b"VmHWM:"):
                    return int(line.split()[1])
    except (OSError, ValueError):
        pass
    return 0


def _run_posix(cmd, fin, fout, ferr, cwd, tl, ml_mb):
    import resource
    import signal

    def pre():
        try:
            lim = int((ml_mb + AS_SLACK_MB) * MB)
            resource.setrlimit(resource.RLIMIT_AS, (lim, lim))
        except (ValueError, OSError):
            pass
        try:
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        except (ValueError, OSError):
            pass

    r = RunResult()
    t0 = time.perf_counter()
    proc = subprocess.Popen(cmd, stdin=fin, stdout=fout, stderr=ferr, cwd=cwd, env=_child_env(),
                            preexec_fn=pre, start_new_session=True, close_fds=True)
    is_linux = sys.platform.startswith("linux")
    stat_path = "/proc/%d/status" % proc.pid
    peak = 0
    ru = None
    st = 0
    while True:
        try:
            pid, st, ru = os.wait4(proc.pid, os.WNOHANG)
        except ChildProcessError:
            pid, st, ru = proc.pid, 0, None
        el = time.perf_counter() - t0
        if pid:
            break
        if is_linux:
            peak = max(peak, _vmhwm_kb(stat_path))
        stop = None
        if el > tl:
            r.tle = True
            stop = True
        elif os.fstat(fout.fileno()).st_size > OUT_CAP:
            r.ole = True
            stop = True
        if stop:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except OSError:
                try:
                    proc.kill()
                except OSError:
                    pass
            try:
                pid, st, ru = os.wait4(proc.pid, 0)
            except ChildProcessError:
                st = 0
            break
        time.sleep(POLL)
    r.elapsed = el
    r.code = os.waitstatus_to_exitcode(st)
    proc.returncode = r.code
    if is_linux:
        # /proc có thể bỏ lỡ đỉnh bộ nhớ của tiến trình chạy rất nhanh; ru_maxrss
        # được lấy lúc tiến trình kết thúc. Dùng giá trị lớn hơn để tránh lọt MLE.
        ru_mb = (ru.ru_maxrss / 1024.0) if ru is not None else 0.0
        r.mem = max(peak / 1024.0, ru_mb) if (peak or ru_mb) else None
    elif ru is not None:
        r.mem = ru.ru_maxrss / (1024.0 * 1024.0)
    return r


_WIN = {}


def _win_api():
    if _WIN:
        return _WIN
    import ctypes
    from ctypes import wintypes

    class IO_COUNTERS(ctypes.Structure):
        _fields_ = [(n, ctypes.c_ulonglong) for n in (
            "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
            "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]

    class BASIC(ctypes.Structure):
        _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64),
                    ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                    ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                    ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD),
                    ("SchedulingClass", wintypes.DWORD)]

    class EXT(ctypes.Structure):
        _fields_ = [("BasicLimitInformation", BASIC), ("IoInfo", IO_COUNTERS),
                    ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                    ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]

    k = ctypes.WinDLL("kernel32", use_last_error=True)
    k.CreateJobObjectW.restype = wintypes.HANDLE
    k.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    k.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
    k.SetInformationJobObject.restype = wintypes.BOOL
    k.QueryInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD,
                                            ctypes.c_void_p]
    k.QueryInformationJobObject.restype = wintypes.BOOL
    k.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    k.AssignProcessToJobObject.restype = wintypes.BOOL
    k.CloseHandle.argtypes = [wintypes.HANDLE]
    _WIN.update(ctypes=ctypes, k=k, EXT=EXT)
    return _WIN


def _run_windows(cmd, fin, fout, ferr, cwd, tl, ml_mb):
    r = RunResult()
    job = None
    api = None
    try:
        api = _win_api()
        k, ctypes, EXT = api["k"], api["ctypes"], api["EXT"]
        job = k.CreateJobObjectW(None, None)
        info = EXT()
        info.BasicLimitInformation.LimitFlags = 0x100 | 0x2000   # PROCESS_MEMORY | KILL_ON_JOB_CLOSE
        info.ProcessMemoryLimit = int(ml_mb * MB)
        if not k.SetInformationJobObject(job, 9, ctypes.byref(info), ctypes.sizeof(info)):
            raise OSError("SetInformationJobObject thất bại")
    except Exception as e:      # noqa: BLE001
        if job and api:
            try:
                api["k"].CloseHandle(job)
            except Exception:   # noqa: BLE001
                pass
        r.warn.append("Windows: không dựng được Job Object, bộ nhớ không được giới hạn/đo (%s)" % e)
        job = None
    t0 = time.perf_counter()
    proc = subprocess.Popen(cmd, stdin=fin, stdout=fout, stderr=ferr, cwd=cwd, env=_child_env(),
                            creationflags=0x08000000)   # CREATE_NO_WINDOW
    if job:
        try:
            if not api["k"].AssignProcessToJobObject(job, int(proc._handle)):
                raise OSError("AssignProcessToJobObject thất bại")
        except Exception as e:  # noqa: BLE001
            r.warn.append("Windows: không gán được tiến trình vào Job Object (%s)" % e)
            try:
                api["k"].CloseHandle(job)
            except Exception:   # noqa: BLE001
                pass
            job = None
    while True:
        if proc.poll() is not None:
            break
        el = time.perf_counter() - t0
        if el > tl:
            r.tle = True
        elif os.fstat(fout.fileno()).st_size > OUT_CAP:
            r.ole = True
        if r.tle or r.ole:
            proc.kill()
            proc.wait()
            break
        time.sleep(POLL)
    r.elapsed = time.perf_counter() - t0
    r.code = proc.returncode
    if job:
        try:
            k, ctypes, EXT = api["k"], api["ctypes"], api["EXT"]
            out = EXT()
            if k.QueryInformationJobObject(job, 9, ctypes.byref(out), ctypes.sizeof(out), None):
                r.mem = out.PeakProcessMemoryUsed / float(MB)
        finally:
            api["k"].CloseHandle(job)
    return r


def _tail(path, n=4000):
    try:
        with open(path, "rb") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - n))
            return f.read().decode("utf-8", "replace")
    except OSError:
        return ""


def run_solution(pyexe, script, data, prob, scale, workdir):
    ip, op, ep = (os.path.join(workdir, n) for n in ("in.txt", "out.txt", "err.txt"))
    with open(ip, "wb") as f:
        f.write(data)
    fin, fout, ferr = open(ip, "rb"), open(op, "wb"), open(ep, "wb")
    try:
        cmd = [pyexe, os.path.abspath(script)]
        if IS_WIN:
            r = _run_windows(cmd, fin, fout, ferr, workdir, prob.tl * scale, prob.ml)
        else:
            r = _run_posix(cmd, fin, fout, ferr, workdir, prob.tl * scale, prob.ml)
    finally:
        fin.close()
        fout.close()
        ferr.close()
    with open(op, "rb") as f:
        r.out = f.read(OUT_CAP + 1)
    r.err = _tail(ep)
    return r


def classify(r, prob, scale):
    """Trả về (verdict, msgs) nếu đã kết luận được từ cách chương trình chạy; None nếu cần so kết quả."""
    tl = prob.tl * scale
    if r.tle:
        return "TLE", ["chương trình bị dừng sau %.2f s (giới hạn %.2f s)" % (r.elapsed, tl)]
    if r.ole:
        return "WA", ["kết quả in ra vượt 64 MB — chương trình bị dừng"]
    mem_over = r.mem is not None and r.mem > prob.ml
    # Chỉ nhận MemoryError ở dòng kết thúc traceback; một chương trình tự in chữ
    # "MemoryError" ra stderr không được phép biến RE/WA thành MLE.
    mem_err = re.search(r"(?m)^MemoryError(?::.*)?$", r.err.strip()) is not None
    # SIGKILL tự nó chưa chứng minh MLE (bài làm có thể tự gửi SIGKILL). Chỉ coi
    # là hết bộ nhớ khi số đo đỉnh đã tiến sát giới hạn.
    oom_kill = ((not IS_WIN) and r.code == -9 and r.mem is not None
                and r.mem >= prob.ml * 0.90)
    if mem_over or mem_err or oom_kill:
        if mem_over:
            why = "dùng tới %.1f MB (giới hạn %d MB)" % (r.mem, prob.ml)
        elif mem_err:
            why = "MemoryError khi xin thêm bộ nhớ (giới hạn %d MB)" % prob.ml
        else:
            why = "bị hệ điều hành dừng (SIGKILL) khi hết bộ nhớ"
        return "MLE", [why]
    if r.code != 0:
        lines = [l for l in r.err.strip().splitlines() if l.strip()]
        msgs = ["mã thoát %s" % r.code]
        if not IS_WIN and r.code < 0:
            import signal
            try:
                msgs = ["bị tín hiệu %s" % signal.Signals(-r.code).name]
            except ValueError:
                pass
        msgs += [l[:200] for l in lines[-4:]]
        return "RE", msgs
    if r.elapsed > tl:
        return "TLE", ["chạy %.2f s (giới hạn %.2f s)" % (r.elapsed, tl)]
    return None


# ════════════════════════════════════════════════════════════════════
#  HIỂN THỊ
# ════════════════════════════════════════════════════════════════════
def preview(data, full=False, head=8, tail=2, width=100, ind="      "):
    if len(data) == 0:
        return ind + dim("(rỗng — 0 byte)")
    text = data.decode("utf-8", "replace").replace("\r\n", "\n")
    has_nl = text.endswith("\n")
    lines = text[:-1].split("\n") if has_nl else text.split("\n")
    total = len(lines)
    if not full and total > head + tail + 1:
        hidden = total - head - tail
        shown = lines[:head] + [None] + lines[-tail:]
    else:
        hidden = 0
        shown = lines
    rows = []
    for l in shown:
        if l is None:
            rows.append(ind + dim("… (ẩn %d dòng) …" % hidden))
            continue
        if not full and len(l) > width:
            l = l[:width] + dim("…(+%d ký tự)" % (len(l) - width))
        rows.append(ind + l)
    foot = "(%d byte, %d dòng%s)" % (len(data), total, "" if has_nl else ", KHÔNG có \\n ở cuối")
    rows.append(ind + dim(foot))
    return "\n".join(rows)


def visible(data, ind="      ", max_lines=6, width=100):
    t = data.decode("utf-8", "replace").replace("\r\n", "\n")
    parts = t.split("\n")
    has_nl = parts and parts[-1] == ""
    if has_nl:
        parts = parts[:-1]
    rows = []
    for i, p in enumerate(parts[:max_lines]):
        p = p.replace("\r", "␍").replace(" ", "·").replace("\t", "→")
        if len(p) > width:
            p = p[:width] + "…"
        last = (i == len(parts) - 1)
        rows.append(ind + p + ("⏎" if (not last or has_nl) else dim("(hết, không có ⏎)")))
    if len(parts) > max_lines:
        rows.append(ind + dim("… (còn %d dòng)" % (len(parts) - max_lines)))
    return "\n".join(rows)


def line(ch="─", n=78):
    return ch * n


def fmt_time(r):
    return (">%.3f s" % r.elapsed) if r.tle else "%.3f s" % r.elapsed


def fmt_mem(r):
    return "%.1f MB" % r.mem if r.mem is not None else "n/a"


def judge_problem(prob, script, args, show_io=True, quiet=False, stop_first=False):
    """Chấm một bài; trả về danh sách TestResult."""
    emit = (lambda *a, **k: None) if quiet else print
    tests = get_tests(prob)
    scale = args.scale
    results = []
    workdir = tempfile.mkdtemp(prefix="cham_")
    try:
        emit()
        emit(paint(line("═"), "1"))
        emit(paint(" BÀI %s — %s" % (prob.letter, prob.title), "1") + dim("   (file: %s)" % script))
        emit(" Giới hạn : %.2f s%s | %d MB | vào ra chuẩn (stdin/stdout)"
             % (prob.tl * scale, "" if scale == 1 else " (đã nhân hệ số %.2f)" % scale, prob.ml))
        emit(" Kết quả  : " + prob.fmt)
        emit(" Chế độ   : " + ("nới lỏng (--lenient): sai định dạng vẫn tính AC" if args.lenient
                               else "NGHIÊM NGẶT: sai định dạng = WA (không đạt)"))
        emit(paint(line("═"), "1"))
        warned = set()
        for i, t in enumerate(tests, 1):
            if args.test and i != args.test:
                continue
            r = run_solution(args.python, script, t.inp, prob, scale, workdir)
            res = classify(r, prob, scale)
            if res is None:
                chk = prob.check or generic_check
                res = chk(r.out, t, args.lenient)
            verdict, msgs = res
            tr = TestResult(i, t, verdict, msgs, r)
            results.append(tr)
            if args.save_tests:
                _save_test(args.save_tests, prob, i, t, r)
            if not quiet:
                emit()
                emit(paint("▌Test %d/%d" % (i, len(tests)), "1") + "  %s  " % t.label + dim("[%s]" % t.kind))
                if show_io:
                    emit("  Input:")
                    emit(preview(t.inp, args.full))
                    emit("  Đáp án đúng:")
                    emit(preview(t.exp, args.full))
                    emit("  Output của chương trình:")
                    if verdict == "TLE" and r.tle:
                        emit("      " + dim("(bị dừng do quá thời gian, output chưa đầy đủ nên không so sánh)"))
                    elif verdict in ("RE", "MLE") and not r.out:
                        emit("      " + dim("(không có output)"))
                    else:
                        emit(preview(r.out, args.full))
                emit("  ➜ %s  %s | thời gian %s | bộ nhớ %s"
                     % (vtag(verdict), VDESC[verdict], fmt_time(r), fmt_mem(r)))
                for m in msgs:
                    emit("      · " + m)
                if verdict == "WA" and any(m.startswith("SAI ĐỊNH DẠNG:") for m in msgs):
                    emit("      Nhìn thấy khoảng trắng  (· dấu cách, → tab, ⏎ xuống dòng)")
                    emit("      đáp án:")
                    emit(visible(t.exp, ind="        "))
                    emit("      của bạn:")
                    emit(visible(norm(r.out), ind="        "))
                if r.code == 0 and r.err.strip() and verdict in ("AC", "WA"):
                    emit("      " + dim("(stderr có nội dung, bị bỏ qua: %s)" % r.err.strip().splitlines()[-1][:100]))
                for w in r.warn:
                    if w not in warned:
                        warned.add(w)
                        emit("      " + paint("! " + w, "1;33"))
            if stop_first and verdict != "AC":
                break
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    return results


def overall(results):
    for r in results:
        if r.verdict != "AC":
            return r.verdict
    return "AC"


def print_summary(prob, results):
    print()
    print(paint(line("─"), "1"))
    print(paint(" TỔNG KẾT BÀI %s — %s" % (prob.letter, prob.title), "1"))
    print(line("─"))
    print(" %-4s %-9s %-8s %-11s %-9s %s" % ("Test", "Loại", "Kết quả", "Thời gian", "Bộ nhớ", "Mô tả"))
    for r in results:
        tag = vtag(r.verdict) + " " * (8 - len(r.verdict))
        print(" %-4d %-9s %s %-11s %-9s %s" % (r.idx, r.test.kind, tag, fmt_time(r.run), fmt_mem(r.run),
                                              r.test.label[:60]))
    ac = sum(1 for r in results if r.verdict == "AC")
    v = overall(results)
    cnt = Counter(r.verdict for r in results)
    extra = ", ".join("%s×%d" % (k, cnt[k]) for k in ("WA", "TLE", "RE", "MLE") if cnt.get(k))
    print(line("─"))
    print(" KẾT LUẬN: %s  —  %d/%d test AC%s" % (vtag(v), ac, len(results), ("  (" + extra + ")") if extra else ""))
    print("           " + VDESC[v] + ("" if v == "AC" else "  (theo test lỗi đầu tiên)"))
    print(paint(line("─"), "1"))


def _save_test(base, prob, i, t, r):
    d = os.path.join(base, "bai_%s" % prob.letter)
    os.makedirs(d, exist_ok=True)
    for ext, data in (("in", t.inp), ("ans", t.exp), ("out", r.out)):
        with open(os.path.join(d, "test%d.%s" % (i, ext)), "wb") as f:
            f.write(data)


# ════════════════════════════════════════════════════════════════════
#  TỰ KIỂM TRA BỘ CHẤM
# ════════════════════════════════════════════════════════════════════
SELFTEST = [(("mau_dung/bai%02d.py" % (i + 1)), p.letter, "AC") for i, p in enumerate(PROBLEMS)] + [
    ("mau_sai/A_max0.py", "A", "WA"),
    ("mau_sai/A_dau_cach_doi.py", "A", "WA"),
    ("mau_sai/A_lap_vo_han.py", "A", "TLE"),
    ("mau_sai/A_ngon_bo_nho_45tr.py", "A", "MLE"),
    ("mau_sai/A_xin_bo_nho_4GB.py", "A", "MLE"),
    ("mau_sai/B_int_input.py", "B", "RE"),
    ("mau_sai/C_eof_error.py", "C", "RE"),
    ("mau_sai/D_readline.py", "D", "WA"),
    ("mau_sai/E_chia_nguyen.py", "E", "WA"),
    ("mau_sai/E_in_tho.py", "E", "WA"),
    ("mau_sai/F_nho_hon_thuong.py", "F", "WA"),
    ("mau_sai/G_bang_tham_chieu.py", "G", "WA"),
    ("mau_sai/H_count.py", "H", "TLE"),
    ("mau_sai/I_input.py", "I", "RE"),
    ("mau_sai/I_split.py", "I", "WA"),
    ("mau_sai/J_pop0.py", "J", "TLE"),
    ("mau_sai/J_thieu_empty.py", "J", "RE"),
    ("mau_sai/J_thua_dong_trong.py", "J", "WA"),
]


def selftest(args):
    base = os.path.dirname(os.path.abspath(__file__))
    print(paint(line("═"), "1"))
    print(paint(" TỰ KIỂM TRA BỘ CHẤM: chạy bài mẫu đúng (phải AC) và bài mẫu sai (phải ra đúng kết luận dự kiến)", "1"))
    print(paint(line("═"), "1"))
    bad = 0
    print(" %-32s %-4s %-9s %-9s %s" % ("File", "Bài", "Dự kiến", "Thực tế", ""))
    for rel, letter, want in SELFTEST:
        path = os.path.join(base, rel)
        if not os.path.exists(path):
            print(" %-32s %-4s %-9s %-9s %s" % (rel, letter, want, "THIẾU", paint("✗", "1;31")))
            bad += 1
            continue
        res = judge_problem(BY_LETTER[letter], path, args, quiet=True, stop_first=True)
        got = overall(res)
        ok = got == want
        bad += 0 if ok else 1
        info = ""
        if res:
            fail = next((r for r in res if r.verdict != "AC"), None)
            if fail:
                info = "(test %d)" % fail.idx
        print(" %-32s %-4s %-9s %-9s %s %s" % (rel, letter, want, got,
                                                paint("✓", "1;32") if ok else paint("✗ SAI", "1;31"), info))
    print(line("─"))
    if bad:
        print(paint(" CÓ %d MỤC KHÔNG KHỚP — bộ chấm hoặc môi trường có vấn đề." % bad, "1;31"))
    else:
        print(paint(" TẤT CẢ %d MỤC KHỚP DỰ KIẾN — bộ chấm hoạt động đúng trên máy này." % len(SELFTEST), "1;32"))
    return 1 if bad else 0


# ════════════════════════════════════════════════════════════════════
#  DÒNG LỆNH
# ════════════════════════════════════════════════════════════════════
def resolve_problem(tok):
    t = tok.strip()
    m = re.fullmatch(r"(?i)(?:bai)?0*([1-9]|10)", t)
    if m:
        return PROBLEMS[int(m.group(1)) - 1]
    m = re.fullmatch(r"(?i)(?:bai)?([a-j])", t)
    if m:
        return BY_LETTER[m.group(1).upper()]
    return None


def cmd_list():
    print(" %-4s %-26s %-8s %-8s %s" % ("Bài", "Tên", "Thời gian", "Bộ nhớ", "File mặc định"))
    for p in PROBLEMS:
        print(" %-4s %-26s %-8s %-8s %s" % ("%s/%d" % (p.letter, p.num), p.title, "%.1f s" % p.tl,
                                            "%d MB" % p.ml, p.filename))
    return 0


def main(argv=None):
    global USE_COLOR
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:      # noqa: BLE001
            pass
    ap = argparse.ArgumentParser(
        prog="cham.py", formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Bộ chấm 10 bài A..J (Buổi 14, bản Python). Ví dụ:\n"
                    "  python cham.py A                chấm bài A bằng bai01.py\n"
                    "  python cham.py 3 code.py        chấm bài C (số 3) bằng code.py\n"
                    "  python cham.py --all --dir nop  chấm cả 10 bài trong thư mục nop/\n"
                    "  python cham.py --selftest       tự kiểm tra bộ chấm")
    ap.add_argument("items", nargs="*", help="BÀI [FILE.py]  (BÀI = A..J hoặc 1..10), hoặc chỉ FILE baiNN.py")
    ap.add_argument("--all", action="store_true", help="chấm cả 10 bài (bai01.py..bai10.py)")
    ap.add_argument("--dir", default=".", help="thư mục chứa file bài làm (mặc định: thư mục hiện tại)")
    ap.add_argument("--list", action="store_true", help="liệt kê các bài và giới hạn")
    ap.add_argument("--selftest", action="store_true", help="tự kiểm tra bộ chấm bằng bài mẫu đúng/sai")
    ap.add_argument("--test", type=int, metavar="N", help="chỉ chạy test số N (1..5)")
    ap.add_argument("--stop", action="store_true", help="dừng ở test lỗi đầu tiên")
    ap.add_argument("--brief", action="store_true", help="không in nội dung input/đáp án/output")
    ap.add_argument("--detail", action="store_true", help="với --all: in đầy đủ input/đáp án/output từng test")
    ap.add_argument("--full", action="store_true", help="không rút gọn nội dung dài (cẩn thận: có thể rất dài)")
    ap.add_argument("--lenient", action="store_true", help="nới lỏng: bỏ qua lỗi định dạng (tính là AC)")
    ap.add_argument("--scale", type=float, default=1.0, metavar="X",
                    help="nhân giới hạn thời gian với X (dùng khi máy chậm)")
    ap.add_argument("--python", default=sys.executable, help="trình thông dịch dùng để chạy bài làm")
    ap.add_argument("--save-tests", metavar="DIR", help="ghi test (.in), đáp án (.ans), output (.out) ra thư mục DIR")
    ap.add_argument("--no-color", action="store_true", help="tắt màu")
    args = ap.parse_args(argv)

    USE_COLOR = sys.stdout.isatty() and not args.no_color and "NO_COLOR" not in os.environ
    if USE_COLOR and IS_WIN:
        os.system("")          # bật xử lý mã ANSI trên Windows 10+
    if args.scale <= 0:
        ap.error("--scale phải > 0")

    if args.list:
        return cmd_list()
    if args.selftest:
        return selftest(args)

    if args.all:
        rows = []
        for p in PROBLEMS:
            path = os.path.join(args.dir, p.filename)
            if not os.path.exists(path):
                rows.append((p, "THIẾU FILE", 0, 5))
                continue
            res = judge_problem(p, path, args, show_io=args.detail, stop_first=args.stop)
            print_summary(p, res)
            rows.append((p, overall(res), sum(1 for r in res if r.verdict == "AC"), len(res)))
            # Không giữ hàng chục MB dữ liệu test của bài trước trong chế độ --all.
            # Điều này cũng tránh làm sai số đo bộ nhớ của tiến trình con trên POSIX.
            _TEST_CACHE.pop(p.letter, None)
            del res
        print()
        print(paint(line("═"), "1"))
        print(paint(" TỔNG HỢP 10 BÀI", "1"))
        print(line("─"))
        good = 0
        for p, v, ac, n in rows:
            good += 1 if v == "AC" else 0
            print(" Bài %s  %-26s %-11s %d/%d test AC" % (p.letter, p.title, vtag(v) if v != "THIẾU FILE" else v, ac, n))
        print(line("─"))
        print(" %d/10 bài đạt AC toàn bộ." % good)
        return 0 if good == 10 else 1

    if not args.items:
        ap.print_help()
        return 2
    first = args.items[0]
    script = None
    prob = None
    if first.lower().endswith(".py"):
        script = first
        m = re.fullmatch(r"(?i)bai0*(\d+)\.py", os.path.basename(first))
        if m and 1 <= int(m.group(1)) <= 10:
            prob = PROBLEMS[int(m.group(1)) - 1]
        if len(args.items) > 1:
            prob = resolve_problem(args.items[1]) or prob
        if prob is None:
            print("Không suy ra được bài từ tên file %r. Hãy ghi rõ: python cham.py A %s" % (first, first))
            return 2
    else:
        prob = resolve_problem(first)
        if prob is None:
            print("Bài %r không hợp lệ. Dùng A..J hoặc 1..10 (xem --list)." % first)
            return 2
        script = args.items[1] if len(args.items) > 1 else os.path.join(args.dir, prob.filename)
    if not os.path.isfile(script):
        print("Không tìm thấy file bài làm: %s" % script)
        print("Đặt bài làm tên %s trong thư mục hiện tại, hoặc chỉ rõ đường dẫn: python cham.py %s duong_dan.py"
              % (prob.filename, prob.letter))
        return 2
    if args.test and not (1 <= args.test <= 5):
        ap.error("--test phải trong 1..5")
    res = judge_problem(prob, script, args, show_io=not args.brief, stop_first=args.stop)
    print_summary(prob, res)
    return 0 if overall(res) == "AC" and res else 1


if __name__ == "__main__":
    sys.exit(main())

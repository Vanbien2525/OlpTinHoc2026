import sys
s = b"".join(sys.stdin.buffer.read().split())
upper = sum(65 <= c <= 90 for c in s)
lower = sum(97 <= c <= 122 for c in s)
digit = sum(48 <= c <= 57 for c in s)
print(upper, lower, digit, len(s) - upper - lower - digit)

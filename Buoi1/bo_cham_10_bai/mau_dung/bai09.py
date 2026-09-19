import sys

s = sys.stdin.buffer.readline().rstrip(b"\r\n")
upper = lower = digit = other = 0
for c in s:
    if 65 <= c <= 90:
        upper += 1
    elif 97 <= c <= 122:
        lower += 1
    elif 48 <= c <= 57:
        digit += 1
    else:
        other += 1
print(upper, lower, digit, other)

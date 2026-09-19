import sys
d = list(map(int, sys.stdin.buffer.read().split()))
n = d[0]
print(f"{sum(d[1:1+n]) // n:.6f}")

import sys
d = list(map(int, sys.stdin.buffer.read().split()))
a = d[1:1 + d[0]]
print(f"{sum(a)}  {max(a)}")

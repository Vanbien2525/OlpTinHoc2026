import sys

d = sys.stdin.buffer.read().split()
n = int(d[0])
a = list(map(int, d[1:1 + n]))
print(sum(a), max(a))

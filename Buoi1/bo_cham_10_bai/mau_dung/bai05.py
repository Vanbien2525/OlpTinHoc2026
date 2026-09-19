import sys

d = sys.stdin.buffer.read().split()
n = int(d[0])
total = sum(map(int, d[1:1 + n]))
print("%.6f" % (total / n))

import sys
d = list(map(int, sys.stdin.buffer.read().split()))
a = d[1:1 + d[0]]
mx = 0
for x in a:
    mx = max(mx, x)
print(sum(a), mx)

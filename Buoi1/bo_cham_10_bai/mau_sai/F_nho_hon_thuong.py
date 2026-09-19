import sys
d = list(map(int, sys.stdin.buffer.read().split()))
n, q = d[0], d[1]
a = d[2:2+n]
p = 2+n
for _ in range(q):
    left, right = d[p], d[p+1]
    p += 2
    print(sum(1 for x in a if left < x < right))

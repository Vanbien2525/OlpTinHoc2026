import sys
d = list(map(int, sys.stdin.buffer.read().split()))
n, m = d[0], d[1]
table = [[0] * m] * n
p = 2
for i in range(n):
    for j in range(m):
        table[i][j] = d[p]
        p += 1
for row in table:
    print(sum(row))

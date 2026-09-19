import sys

d = list(map(int, sys.stdin.buffer.read().split()))
n, m = d[0], d[1]
p = 2
ans = []
for _ in range(n):
    ans.append(str(sum(d[p:p + m])))
    p += m
sys.stdout.write("\n".join(ans) + "\n")

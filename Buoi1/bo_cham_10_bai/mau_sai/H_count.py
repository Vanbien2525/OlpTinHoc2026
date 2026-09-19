import sys
d = list(map(int, sys.stdin.buffer.read().split()))
n = d[0]
a = d[1:1+n]
q = d[n+1]
for x in d[n+2:n+2+q]:
    print(a.count(x))

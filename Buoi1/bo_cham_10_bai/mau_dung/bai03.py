import sys

a = list(map(int, sys.stdin.buffer.read().split()))
print(len(a), sum(a))

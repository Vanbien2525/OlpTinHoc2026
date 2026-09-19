import sys

rows = sys.stdin.buffer.read().split(b"\n")
n = int(rows[0])
lines = rows[1:1 + n]
best = max(lines, key=len)
sys.stdout.buffer.write(best + b"\n")

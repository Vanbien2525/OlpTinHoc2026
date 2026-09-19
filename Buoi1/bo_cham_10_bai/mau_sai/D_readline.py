import sys
n = int(sys.stdin.readline())
best = ""
for _ in range(n):
    line = sys.stdin.readline()
    if len(line) > len(best):
        best = line
sys.stdout.write(best)

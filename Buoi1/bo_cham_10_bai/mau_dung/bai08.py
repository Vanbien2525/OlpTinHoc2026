import sys
from collections import Counter

d = sys.stdin.buffer.read().split()
n = int(d[0])
counts = Counter(d[1:1 + n])
q = int(d[n + 1])
queries = d[n + 2:n + 2 + q]
sys.stdout.write("\n".join(str(counts[x]) for x in queries) + "\n")

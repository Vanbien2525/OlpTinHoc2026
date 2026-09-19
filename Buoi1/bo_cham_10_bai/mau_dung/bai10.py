import sys
from collections import deque

lines = sys.stdin.buffer.read().splitlines()
n = int(lines[0])
queue = deque()
ans = []
for line in lines[1:1 + n]:
    if line.startswith(b"IN "):
        queue.append(line[3:])
    elif line == b"OUT":
        ans.append(queue.popleft() if queue else b"EMPTY")
    else:
        ans.append(str(len(queue)).encode())
sys.stdout.buffer.write(b"\n".join(ans) + (b"\n" if ans else b""))

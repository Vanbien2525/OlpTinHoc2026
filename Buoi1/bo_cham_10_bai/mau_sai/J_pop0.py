import sys
lines = sys.stdin.buffer.read().splitlines()
queue = []
ans = []
for line in lines[1:]:
    if line.startswith(b"IN "):
        queue.append(line[3:])
    elif line == b"OUT":
        ans.append(queue.pop(0) if queue else b"EMPTY")
    else:
        ans.append(str(len(queue)).encode())
sys.stdout.buffer.write(b"\n".join(ans) + (b"\n" if ans else b""))

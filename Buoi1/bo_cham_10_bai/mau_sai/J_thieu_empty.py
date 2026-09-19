import sys
lines = sys.stdin.buffer.read().splitlines()
queue = []
for line in lines[1:]:
    if line.startswith(b"IN "):
        queue.append(line[3:])
    elif line == b"OUT":
        print(queue.pop(0).decode())
    else:
        print(len(queue))

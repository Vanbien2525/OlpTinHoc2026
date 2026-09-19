import sys
from collections import deque
def main():
    du_lieu = sys.stdin.buffer.read().split(b"\n")
    n = int(du_lieu[0])
    hang = deque()
    ra = []
    for i in range(1, n + 1):
        d = du_lieu[i].split()
        if not d:
            continue
        if d[0] == b"IN":
            hang.append(d[1])
        elif d[0] == b"OUT":
            ra.append(hang.popleft() if hang else b"EMPTY")
        else:
            ra.append(str(len(hang)).encode())
    # if ra:
    sys.stdout.buffer.write(b"\n".join(ra) + b"\n")

main()
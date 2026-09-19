import sys
def main():
    du_lieu = sys.stdin.buffer.read().split()
    n = int(du_lieu[0])
    m = int(du_lieu[1])
    ra = []
    p = 2
    for _ in range(n):
        ra.append(sum(map(int, du_lieu[p:p + m])))
        p += m
    sys.stdout.write("\n".join(map(str, ra)) + "\n")
main()
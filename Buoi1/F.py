import sys

def main():
    du_lieu = sys.stdin.buffer.read().split()
    n = int(du_lieu[0])
    q = int(du_lieu[1])
    n_list = list(map(int, du_lieu[2: 2+n]))
    p = 2 + n
    ra = []
    for _ in range(q):
        l = int(du_lieu[p])
        r = int(du_lieu[p+1])
        p+=2
        ra.append(sum(1 for x in n_list if l <= x <= r))
    sys.stdout.write("\n".join(map(str, ra)) + "\n")

main()
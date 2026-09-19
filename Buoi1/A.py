import sys

def main():
    du_lieu = sys.stdin.buffer.read().split()

    n = int(du_lieu[0])
    a = list(map(int, du_lieu[1:1+n]))

    print(sum(a), max(a))

main()
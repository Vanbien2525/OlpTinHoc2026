import sys

def main():
    du_lieu = sys.stdin.buffer.read().split()
    n = int(du_lieu[0])
    tong = sum(map(int, du_lieu[1:1 + n]))
    print(f"{tong/n:.6f}")

main()
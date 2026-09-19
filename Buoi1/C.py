import sys

def main():
    du_lieu = sys.stdin.buffer.read().split()
    a = list(map(int, du_lieu))
    print(len(a), sum(a))
    
main()
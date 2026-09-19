import sys
from collections import Counter

def main():
    du_lieu = sys.stdin.buffer.read().split()
    
    n = int(du_lieu[0])
    dem = Counter(du_lieu[1:1+n])
    q = int(du_lieu[n+1])
    truy_van = du_lieu[2+n:2+n+q]
    sys.stdout.write("\n".join(str(dem.get(x, 0)) for x in truy_van) + "\n")

if __name__ == "__main__":
    main()
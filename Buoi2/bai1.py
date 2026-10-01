import sys

def main():
    du_lieu = sys.stdin.buffer.read().split()
    n = int(du_lieu[0])
    a = sorted(list(map(int, du_lieu[1:1+n])))
    
    
    tong = sum(a)
    tich_max = max((a[n-1] * a[n-2]), (a[0] * a[1]))
    sys.stdout.write("%d %d\n" %(tong, tich_max))
main()
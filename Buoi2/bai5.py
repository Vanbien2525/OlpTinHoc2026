import sys

THANG = 10 ** 20
def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    f = []
    p = 1
    for _ in range(n):
        a = int(data[p]); b = int(data[p+1]); p +=2
        f.append((((a * THANG) // b), b, a))
    f.sort()
    sys.stdout.write("".join(["%d %d\n" % (t[2], t[1]) for t in f]))
    
main()
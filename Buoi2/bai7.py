import sys
def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0]); k = int(data[1])
    p = 2
    ds = []
    for _ in range(n):
        ten = data[p]; diem = int(data[p + 1]); p += 2
        ds.append((-diem, ten))
    ds.sort()
    ra = ["%s %d" % (t[1].decode(), -t[0]) for t in ds[:k]]
    sys.stdout.write("\n".join(ra) + "\n")
main()
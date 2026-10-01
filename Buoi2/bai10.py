import sys
from bisect import bisect_left

def main():
    data = sys.stdin.buffer.read().split()
    q = int(data[0])
    ds = []
    ra = []
    them = ra.append
    tim = bisect_left
    p = 1
    for _ in range(q):
        loai = data[p]; x = int(data[p + 1]); p += 2
        if loai == b"1":
            i = tim(ds, x)
            if i == len(ds) or ds[i] != x: # insert only if not already present
                ds.insert(i, x)
            continue
        if not ds:
            them(-1)
            continue
        i = tim(ds, x)
        if i == len(ds):
            them(x - ds[i - 1])
        elif i == 0:
            them(ds[0] - x)
        else:
            a = ds[i] - x
            b = x - ds[i - 1]
            them(a if a < b else b)
    sys.stdout.write("\n".join(map(str, ra)) + "\n")
main()
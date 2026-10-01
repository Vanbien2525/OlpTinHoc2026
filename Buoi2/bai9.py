import sys
def main():
    data = sys.stdin.buffer.read().split(b"\n")
    n = int(data[0])
    ra = []
    them = ra.append
    for i in range(1, n + 1):
        tu = data[i].split()
        if tu:
            them(b"%d %s" % (len(tu), max(tu, key=len)))
        else:
            them(b"0 -")
    sys.stdout.buffer.write(b"\n".join(ra) + b"\n")
main()
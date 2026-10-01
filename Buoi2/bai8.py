import sys
def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0]); q = int(data[1])
    vt = 0
    ra = []
    them = ra.append
    for tok in data[2:2 + q]:
        vt = (vt + int(tok)) % n # Python % is never negative when n > 0
        them(vt)
    sys.stdout.write("\n".join(map(str, ra)) + "\n")
main()
import sys
from bisect import bisect_right

def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    a = list(map(int, data[1: 1+n]))
    q = int(data[n+1])
    q_i = list(map(int, data[n+2:n+2+q]))
    a = sorted(a)
    tim = bisect_right
    ra = [tim(a, int(t)) for t in q_i]
    sys.stdout.write("\n".join(map(str,ra)) + "\n")
main()
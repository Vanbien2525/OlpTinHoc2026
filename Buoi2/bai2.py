import sys

def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    a = list(map(int,data[1:1+n]))    
    b = sorted(set(a))
    hang = {val: i for i, val in enumerate(b, start=1)}
    ket_qua = [hang[i] for i in a]
    sys.stdout.write(" ".join(map(str,ket_qua)) + "\n")
main()
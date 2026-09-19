import sys

def main():
    du_lieu = sys.stdin.buffer.read().split(b"\n")
    n = int(du_lieu[0])
    tot_nhat = b""
    for i in range(1, n+1):
        d = du_lieu[i].rstrip(b"\n") if i < len(du_lieu) else b""
        if len(d) > len(tot_nhat):
            tot_nhat = d
    sys.stdout.buffer.write(tot_nhat + b"\n")
    
main()
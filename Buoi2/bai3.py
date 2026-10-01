import sys

def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    x = int(data[1])
    da_thay = {}
    lay = da_thay.get
    dap = 0
    for tok in data[2:2+n]:
        v = int(tok)
        dap += lay(x - v, 0)
        da_thay[v] = lay(v, 0) +1
    sys.stdout.write("%d\n" % dap)
main()
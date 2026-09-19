import sys
def main():
    a, b = map(int, sys.stdin.buffer.read().split()[:2])
    print(a * b)
    
main()
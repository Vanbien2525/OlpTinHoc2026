import sys

def main():
    dong = sys.stdin.readline().rstrip("\r\n")
    
    hoa = thuong = so = khac = 0
    for c in dong:
        if c.isupper():      
            hoa += 1
        elif c.islower():    
            thuong += 1
        elif c.isdigit():  
            so += 1
        else:
            khac += 1
            
    print(hoa, thuong, so, khac)

if __name__ == "__main__":
    main()

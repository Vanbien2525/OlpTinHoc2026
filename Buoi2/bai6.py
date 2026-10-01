import sys
from heapq import heapify, heappop, heappush

def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    
    # Khởi tạo min-heap từ danh sách n đống sỏi ban đầu
    h = list(map(int, data[1:1 + n]))
    heapify(h)  # Dựng heap O(n) chạy ở tầng mã C
    
    tong = 0
    # Lặp cho đến khi chỉ còn đúng 1 đống sỏi (xử lý an toàn ca n = 1)
    while len(h) > 1:
        a = heappop(h)  # Lấy đống nhẹ nhất thứ 1
        b = heappop(h)  # Lấy đống nhẹ nhất thứ 2
        a += b
        tong += a
        heappush(h, a)  # Đẩy đống vừa gộp trở lại heap
        
    sys.stdout.write("%d\n" % tong)

main()
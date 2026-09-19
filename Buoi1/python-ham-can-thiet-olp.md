# Các hàm & module Python cần thuộc khi luyện thuật toán thi đấu (OLP)

> Ghi chú: Buổi 14 (bản Python) đã dạy phần vào/ra chuẩn (`sys.stdin.buffer.read()`, `sys.stdout.write`), `Counter`, `deque`. File này liệt kê **thêm** những gì chưa nhắc tới, để tra cứu dần qua các buổi sau.

## Mục lục
1. Built-in cần nhuần nhuyễn
2. `itertools`
3. `collections` (mở rộng)
4. `heapq` — hàng đợi ưu tiên
5. `bisect` — tìm kiếm nhị phân
6. `math`
7. `functools`
8. Xử lý xâu/ký tự
9. Kỹ thuật đệ quy & tốc độ
10. Cấu trúc dữ liệu cần tự cài (chưa có sẵn)

---

## 1. Built-in cần nhuần nhuyễn

| Hàm | Công dụng |
|---|---|
| `sorted(iterable, key=..., reverse=...)` | Sort có tiêu chí (lambda), so sánh nhiều tầng bằng tuple |
| `list.sort(...)` | Giống `sorted` nhưng sort tại chỗ, không tạo list mới |
| `enumerate(iterable, start=0)` | Lấy chỉ số kèm giá trị, khỏi viết `range(len(...))` |
| `zip(a, b, ...)` | Ghép nhiều dãy song song |
| `map(func, iterable)` | Áp hàm lên cả dãy, hay dùng với `int` để parse nhanh |
| `filter(func, iterable)` | Lọc phần tử theo điều kiện |
| `any(...)`, `all(...)` | Kiểm tra điều kiện trên cả dãy, chạy trong mã C nên nhanh |
| `min`/`max` với `key=` | Tìm phần tử tối ưu theo tiêu chí phức tạp |
| `pow(a, b, mod)` | Lũy thừa modulo bằng mũ nhị phân dựng sẵn — nhanh hơn hẳn `a**b % mod` khi số mũ lớn |
| `divmod(a, b)` | Lấy thương và dư cùng lúc |

## 2. `itertools`

| Hàm | Công dụng |
|---|---|
| `accumulate(a)` | Tổng tiền tố dựng sẵn; có tham số `func=` để làm max/min tiền tố |
| `permutations(a, r)` | Sinh hoán vị — dùng cho bài n nhỏ (O(n!)) |
| `combinations(a, r)` | Sinh tổ hợp |
| `combinations_with_replacement(a, r)` | Tổ hợp có lặp |
| `product(a, b, ...)` | Tích Descartes, thay nhiều vòng for lồng nhau |
| `groupby(a)` | Gom nhóm phần tử liên tiếp bằng nhau (cần sort trước) |
| `chain(a, b)` | Nối nhiều iterable mà không copy |
| `islice(a, start, stop)` | Cắt lát trên iterator (kể cả iterator vô hạn) |
| `pairwise(a)` *(3.10+)* | Duyệt từng cặp liên tiếp, thay `zip(a, a[1:])` |

## 3. `collections` (mở rộng)

| Công cụ | Công dụng |
|---|---|
| `defaultdict(int)` / `defaultdict(list)` | Khỏi check key tồn tại; `defaultdict(list)` hay dùng dựng đồ thị kề |
| `Counter(...).most_common(k)` | Top-k phần tử xuất hiện nhiều nhất |
| `deque.appendleft`, `.rotate(k)`, `.extendleft` | Deque hai đầu thật sự, không chỉ hàng đợi một chiều |
| `namedtuple` | Struct nhẹ, code rõ ràng hơn tuple thường khi nhiều trường |

## 4. `heapq` — hàng đợi ưu tiên

- `heappush(h, x)`, `heappop(h)` — thêm/lấy phần tử nhỏ nhất, O(log n).
- `heapify(list)` — biến list thành min-heap tại chỗ, O(n).
- `nlargest(k, a)`, `nsmallest(k, a)` — lấy top-k mà không cần sort cả dãy.
- **Lưu ý:** chỉ có min-heap; muốn max-heap thì đảo dấu giá trị khi push.

## 5. `bisect` — tìm kiếm nhị phân trên dãy đã sort

- `bisect_left(a, x)`, `bisect_right(a, x)` — tìm vị trí chèn, O(log n) thay vì quét O(n).
- `insort_left(a, x)`, `insort_right(a, x)` — chèn giữ nguyên thứ tự sort (tìm vị trí O(log n), nhưng chèn vào list vẫn O(n) do dịch chuyển phần tử).

## 6. `math`

| Hàm | Công dụng |
|---|---|
| `gcd(a, b)`, `lcm(a, b)` *(lcm từ 3.9+)* | Ước chung lớn nhất / bội chung nhỏ nhất, khỏi tự cài Euclid |
| `isqrt(n)` | Căn bậc hai nguyên chính xác (khác `int(sqrt(n))` có thể sai lệch do số thực) |
| `comb(n, k)`, `perm(n, k)`, `factorial(n)` | Tổ hợp/chỉnh hợp/giai thừa dựng sẵn, chính xác tuyệt đối |
| `ceil`, `floor`, `log2` | Làm tròn, log |
| `inf` | Hằng số vô cực — khởi tạo min ban đầu an toàn hơn chọn số lớn tùy ý |
| `prod(a)` *(3.8+)* | Tích cả dãy, giống `sum` nhưng nhân |

## 7. `functools`

- `reduce(func, iterable, init)` — gộp dãy bằng phép toán tuỳ ý.
- `lru_cache(maxsize=None)` hoặc `cache` *(3.9+)* — memo hóa tự động cho hàm đệ quy; quan trọng khi làm quy hoạch động kiểu top-down (đệ quy + nhớ) thay vì tự viết bảng.
- `cmp_to_key(func)` — khi tiêu chí sort cần hàm so sánh hai phần tử, không viết được bằng `key` đơn giản.

## 8. Xử lý xâu/ký tự

- Module `string`: `string.ascii_lowercase`, `ascii_uppercase`, `digits` — danh sách ký tự dựng sẵn.
- `str.join`, `str.translate` + `str.maketrans` — thay thế hàng loạt ký tự nhanh hơn vòng lặp từng ký tự.
- `str.zfill(k)`, `.ljust(k)`, `.rjust(k)` — căn lề/đệm số 0 khi cần in đúng định dạng.

## 9. Kỹ thuật đệ quy & tốc độ

- `sys.setrecursionlimit(n)` — Python mặc định giới hạn đệ quy ~1000; DFS trên đồ thị/cây sâu sẽ RE nếu không tăng.
- Với đệ quy thật sâu (hàng chục nghìn), tăng `setrecursionlimit` thôi chưa đủ vì stack hệ điều hành cũng giới hạn — cần chạy trong thread riêng với stack lớn hơn, hoặc chuyển đệ quy thành vòng lặp tự quản lý stack.
- PyPy: nhiều hệ thống chấm bài (kể cả một số vòng OLP) cho phép nộp bằng PyPy thay CPython, và PyPy có thể nhanh hơn nhiều lần — nên kiểm tra quy chế cuộc thi đang luyện.

## 10. Cấu trúc dữ liệu cần tự cài (chưa có sẵn trong thư viện chuẩn)

Ghi tên trước, buổi học nào dạy tới thì khớp vào:

- Disjoint Set Union (Union-Find) — có nén đường đi + hợp theo hạng
- Segment Tree
- Fenwick Tree (Binary Indexed Tree)
- Trie
- Sparse Table

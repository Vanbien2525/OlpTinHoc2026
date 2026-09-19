# BỘ CHẤM 10 BÀI A–J — BUỔI 14 PYTHON

Bộ chấm chạy trực tiếp bài làm Python, cấp dữ liệu qua `stdin`, nhận kết quả từ `stdout`, đo thời gian và bộ nhớ, rồi kết luận theo đúng 5 trạng thái chuẩn:

- **AC**: đúng giá trị và đúng hoàn toàn định dạng.
- **WA**: sai giá trị hoặc sai định dạng vào–ra. Nếu giá trị đúng nhưng định dạng sai, báo cáo ghi rõ `SAI ĐỊNH DẠNG` và biểu diễn dấu cách bằng `·`, tab bằng `→`, xuống dòng bằng `⏎`.
- **TLE**: chạy quá giới hạn thời gian của đề.
- **RE**: chương trình lỗi khi chạy hoặc kết thúc bằng mã lỗi.
- **MLE**: dùng quá giới hạn bộ nhớ hoặc phát sinh `MemoryError`.

Mỗi bài có đúng **5 test cố định và tái lập**, gồm test ví dụ/đơn giản, test biên và test xấu nhất. Khi chấm một bài, màn hình hiển thị cho từng test: tên test, loại test, input, đáp án đúng, output thực tế, thời gian, bộ nhớ và kết luận. Dữ liệu rất dài được rút gọn trên màn hình nhưng vẫn được đưa đầy đủ vào bài làm và so sánh đầy đủ từng byte.

## 1. Yêu cầu

- Windows 10/11, Linux hoặc macOS.
- Python 3.9 trở lên. Khuyến nghị dùng đúng bản Python bạn dùng để làm bài.
- Không cần cài thư viện ngoài; bộ chấm chỉ dùng thư viện chuẩn.

Kiểm tra Python trên Windows:

```powershell
python --version
```

Nếu lệnh `python` không chạy nhưng máy có Python Launcher, thay `python` trong các lệnh bên dưới bằng `py -3`.

## 2. Cách đặt file bài làm

Tên mặc định:

| Bài | File | Thời gian | Bộ nhớ |
|---|---|---:|---:|
| A | `bai01.py` | 1 giây | 256 MB |
| B | `bai02.py` | 1 giây | 256 MB |
| C | `bai03.py` | 1 giây | 256 MB |
| D | `bai04.py` | 1 giây | 256 MB |
| E | `bai05.py` | 1 giây | 256 MB |
| F | `bai06.py` | 1 giây | 256 MB |
| G | `bai07.py` | 1 giây | 256 MB |
| H | `bai08.py` | 1 giây | 256 MB |
| I | `bai09.py` | 1 giây | 256 MB |
| J | `bai10.py` | 0,5 giây | 256 MB |

Bạn có thể để file bài làm cạnh `cham.py`, hoặc chỉ rõ đường dẫn tới file ở nơi khác.

## 3. Các lệnh thường dùng

Mở PowerShell/CMD tại thư mục bộ chấm rồi chạy:

```powershell
# Xem danh sách bài
python cham.py --list

# Chấm bài A bằng file mặc định bai01.py
python cham.py A

# Chấm bài C bằng một file bất kỳ
python cham.py C D:\BaiTap\code_cua_toi.py

# Có thể gọi bằng số bài
python cham.py 10 bai10.py

# Tự nhận bài C từ tên bai03.py
python cham.py bai03.py

# Chỉ chạy test số 4 của bài H
python cham.py H bai08.py --test 4

# Dừng ngay tại test không AC đầu tiên
python cham.py H bai08.py --stop

# Chấm nhưng không in nội dung input/output
python cham.py H bai08.py --brief

# Lưu cả input, đáp án và output của 5 test ra thư mục ket_qua_test
python cham.py H bai08.py --save-tests ket_qua_test
```

Chấm cả 10 bài trong thư mục `bai_nop` (bên trong phải có `bai01.py` tới `bai10.py`):

```powershell
python cham.py --all --dir bai_nop
```

Mặc định khi chấm cả 10 bài, bộ chấm in bảng tổng kết gọn. Muốn hiện input/output của từng test:

```powershell
python cham.py --all --dir bai_nop --detail
```

## 4. Tự kiểm tra bộ chấm trước khi sử dụng

Chạy:

```powershell
python cham.py --selftest
```

Bộ chấm sẽ chạy 10 lời giải đúng và 18 chương trình cố ý sai để chứng minh đủ các nhánh AC, WA (gồm sai định dạng), TLE, RE và MLE. Kết quả cuối phải là:

```text
TẤT CẢ 28 MỤC KHỚP DỰ KIẾN
```

Thư mục `mau_dung` chứa lời giải chuẩn cho 10 bài. Thư mục `mau_sai` chỉ phục vụ tự kiểm tra verdict; không dùng làm bài nộp.

## 5. Quy tắc chấm định dạng

Chế độ mặc định là nghiêm ngặt:

- Không được in lời nhắc như `Nhap n:` hay thông tin debug ra `stdout`.
- Không được thừa/thiếu dấu cách, tab, dòng trống hoặc dòng kết quả.
- Kết quả không rỗng phải có đúng một ký tự xuống dòng ở cuối.
- Bài E phải có đúng 6 chữ số sau dấu chấm và dùng đúng quy tắc `"%.6f" % (tong / n)` của code mẫu trong tài liệu.
- Bài D phải giữ nguyên dấu cách bên trong dòng dài nhất.
- Bài J không có thao tác `OUT`/`SIZE` thì output phải là file rỗng 0 byte; in một dòng trống vẫn là WA.
- Xuống dòng Windows `CRLF` được chuẩn hóa thành `LF`, nên `print()` bình thường trên Windows không bị phạt oan.

Tùy chọn `--lenient` bỏ qua lỗi khoảng trắng nếu các token vẫn đúng. Đây chỉ là chế độ hỗ trợ tìm lỗi, **không dùng để kết luận bài đã đạt chuẩn đề**.

## 6. Khi máy chạy chậm hơn môi trường chuẩn

Thời gian mặc định bám đúng đề. Nếu máy đang chạy nhiều ứng dụng nền hoặc Python trên máy chậm đáng kể, có thể thử hệ số thời gian:

```powershell
python cham.py J bai10.py --scale 1.5
```

Lúc này giới hạn bài J là `0,5 × 1,5 = 0,75` giây và báo cáo sẽ ghi rõ hệ số. Không nên dùng hệ số quá lớn vì có thể làm lời giải chậm sai độ phức tạp lọt TLE.

## 7. Đọc báo cáo

Mỗi test có dạng:

```text
Test 3/5  ... [biên]
Input: ...
Đáp án đúng: ...
Output của chương trình: ...
➜ WA ... | thời gian ... | bộ nhớ ...
```

Ở cuối bài có bảng 5 test và kết luận chung. Bài chỉ đạt khi cả 5 test đều AC. Kết luận chung lấy verdict của test không AC đầu tiên.

Trên Windows, giới hạn bộ nhớ dùng Job Object. Nếu Windows hoặc chính sách hệ thống không cho gắn tiến trình vào Job Object, bộ chấm sẽ hiện cảnh báo rõ ràng; các verdict khác vẫn hoạt động, nhưng số liệu/giới hạn bộ nhớ trên lần chạy đó không được xem là đáng tin cậy.

## 8. Cấu trúc gói

```text
bo_cham_10_bai/
├── cham.py
├── HUONG_DAN.md
├── CHAM_BAI.bat
├── de_bai.pdf
├── mau_dung/
│   └── bai01.py ... bai10.py
└── mau_sai/
    └── các chương trình dùng bởi --selftest
```

Không sửa `cham.py`, `mau_dung` hoặc `mau_sai` nếu muốn kết quả tự kiểm tra còn nguyên giá trị. Chỉ cần đặt bài của bạn cạnh `cham.py` hoặc truyền đường dẫn file cho lệnh chấm.

# CoffeeManager

CoffeeManager là ứng dụng desktop (Python + Tkinter) hỗ trợ quản lý vận hành quán cà phê: đặt bàn, gọi món, quản lý đơn hàng, nhân sự, lương và báo cáo.

## 1) Hướng dẫn cài đặt

### Bước 1: Clone source code
```bash
git clone <repo-url>
cd CoffeeManager
```

### Bước 2: Tạo môi trường ảo (khuyến nghị)

**Windows (PowerShell):**
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Bước 3: Cài dependencies
```bash
pip install -r requirements.txt
pip install firebase-admin
```

> Ghi chú: `firebase-admin` hiện đang được import trong mã nguồn để hỗ trợ kết nối cloud, nhưng có thể chưa nằm trong `requirements.txt`.

### Bước 4 (tuỳ chọn): Cấu hình Firebase
Nếu muốn đồng bộ với Firestore, chuẩn bị file service account theo một trong các cách:

- Đặt biến môi trường:
```bash
export FIREBASE_CREDENTIALS=/duong-dan/toi/serviceAccountKey.json
```
(Windows PowerShell dùng: `$env:FIREBASE_CREDENTIALS="C:\\path\\serviceAccountKey.json"`)

- Hoặc đặt file tại một trong 2 vị trí:
  - `./serviceAccountKey.json`
  - `./Config/serviceAccountKey.json`

Nếu không cấu hình Firebase, app vẫn chạy bình thường với SQLite cục bộ.

### Bước 5: Chạy ứng dụng
```bash
python main.py
```

---

## 2) Tính năng chính

### Dành cho mọi tài khoản
- Đăng nhập hệ thống.
- Xem tình trạng bàn và thao tác đặt/chuyển trạng thái bàn.
- Gọi món theo bàn, quản lý chi tiết món trong đơn.
- Theo dõi báo cáo/thống kê doanh thu cơ bản.

### Dành cho Admin
- Quản lý nhân viên.
- Quản lý tài khoản người dùng (Admin/Staff).
- Quản lý lương.
- Quản lý danh mục món và sản phẩm.

### Dữ liệu & đồng bộ
- Lưu trữ cục bộ bằng SQLite (`database.db`).
- Tự tạo bảng dữ liệu khi khởi động lần đầu.
- Có hỗ trợ kết nối Firebase/Firestore để đồng bộ từ xa (tuỳ chọn).

---

## 3) Yêu cầu môi trường

- Python **3.10+** (khuyến nghị 3.11).
- Hệ điều hành: Windows / macOS / Linux.
- Tkinter (thường đi kèm Python chuẩn).

Các thư viện cần thiết:
- `pillow`
- `openpyxl`
- `firebase-admin`

---

## 4) Tài khoản mặc định lần đầu

Khi database chưa có user, hệ thống tự tạo tài khoản Admin mặc định:

- **Username:** `admin`
- **Password:** `admin123`

> Khuyến nghị đổi mật khẩu ngay sau lần đăng nhập đầu tiên.

---

## 5) Cấu trúc thư mục chính

```text
CoffeeManager/
├── main.py
├── Config/         # cấu hình DB, Firebase, image
├── Controllers/    # xử lý nghiệp vụ
├── Models/         # thao tác dữ liệu
├── Views/          # giao diện Tkinter
├── Utils/          # tiện ích dùng chung
├── uploads/        # ảnh tải lên
├── requirements.txt
└── database.db
```

---

## 6) Lỗi thường gặp

- **`ModuleNotFoundError: No module named 'firebase_admin'`**
  - Cài thêm: `pip install firebase-admin`

- **Tkinter không hiển thị giao diện (Linux minimal/server):**
  - Cài gói GUI tương ứng hệ điều hành (ví dụ `python3-tk` trên Ubuntu/Debian).

- **Không kết nối được Firebase:**
  - Kiểm tra lại file `serviceAccountKey.json` và biến `FIREBASE_CREDENTIALS`.

---

## 7) Gợi ý sử dụng

- Tạo danh mục món trước khi thêm sản phẩm để quản lý menu rõ ràng.
- Tạo nhân viên và tài khoản Staff cho nhân sự vận hành theo ca.
- Kiểm tra báo cáo định kỳ và xuất dữ liệu khi cần đối soát.

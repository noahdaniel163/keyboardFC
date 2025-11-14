# KeyboardFC - FC Online Automation Tool

## 📋 Mô tả
Công cụ tự động hóa cho game FC Online, hỗ trợ:
- Tự động nhập mật khẩu bằng cách nhận diện số 8 trên bàn phím ảo
- Tự động click nút xác nhận trong các hộp thoại game

## 🛠️ Cài đặt

### Yêu cầu hệ thống
- Windows 10/11
- Python 3.7+
- Game FC Online

### Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### Dependencies chính
```
pyautogui==0.9.54
pygetwindow==0.0.9
opencv-python==4.8.1.78
numpy==1.24.3
ultralytics==8.0.196
```

## ⚙️ Cấu hình

### 1. Cấu hình mật khẩu (config.json)
```json
{
    "password": "8888"
}
```

### 2. Cấu hình xác nhận (config_confirm.json)
```json
{
    "button_type": "confirm",
    "click_delay": 1.0,
    "max_attempts": 3
}
```

## 🎯 Sử dụng

### Phương pháp 1: Sử dụng file .bat
```bash
# Chạy tự động nhập mật khẩu
start.bat

# Chạy tự động click xác nhận
"Click confirm.bat"
```

### Phương pháp 2: Chạy trực tiếp Python
```bash
# Tự động nhập mật khẩu
python auto_input_fc.py

# Tự động click xác nhận
python ClickXacNhan.py
```

## 📝 Cách hoạt động

### Auto Input Password
1. **Khởi động**: Script tìm cửa sổ FC Online
2. **Template Setup**: Tạo hoặc sử dụng template số 8 theo độ phân giải
3. **Screen Capture**: Chụp màn hình game
4. **Pattern Recognition**: Sử dụng OpenCV để tìm số 8
5. **Auto Click**: Click theo mật khẩu đã cấu hình
6. **Logging**: Ghi lại toàn bộ quá trình

### Auto Confirm Click
1. **Window Detection**: Tìm cửa sổ game FC Online
2. **Button Template**: Tạo/sử dụng template nút xác nhận
3. **Adaptive Scaling**: Tự động điều chỉnh kích thước template
4. **Multi-attempt**: Thử tối đa 3 lần nếu không tìm thấy
5. **Screenshot Capture**: Chụp ảnh khu vực trước khi click
6. **Detailed Logging**: Ghi log chi tiết với timestamp

## 🔧 Tính năng nâng cao

### Adaptive Scaling
- Tự động điều chỉnh kích thước template theo độ phân giải màn hình
- Hỗ trợ từ 640x480 đến các độ phân giải cao
- Scale factors: 0.7x, 0.85x, 1x, 1.15x, 1.3x

### Template Management
- Tự động tạo template cho mỗi độ phân giải
- Lưu trữ trong thư mục riêng biệt
- Naming convention: `8_{width}x{height}.png`

### Logging System
- Log files với timestamp
- Screenshots khu vực click
- Chi tiết confidence scores
- Tự động cleanup logs cũ

## 📊 Thông số kỹ thuật

### Ngưỡng nhận diện
- **Digit recognition**: 0.8 (80% confidence)
- **Button recognition**: 0.75 (75% confidence)

### Timing
- **Click delay**: 0.25s giữa các lần click
- **Confirm delay**: 1.0s trước khi click xác nhận
- **Retry delay**: 2.0s giữa các lần thử

### Template sizes
- **Base digit template**: 25px (auto-scaled)
- **Base button template**: 40px (auto-scaled)
- **Capture region**: 150px x 150px

## 🐛 Troubleshooting

### Lỗi thường gặp

**1. Không tìm thấy cửa sổ FC Online**
```
Solution: Đảm bảo game đang chạy với title "FC ONLINE" hoặc "FC Online"
```

**2. Không nhận diện được số 8**
```
Solution: 
- Xóa thư mục digit_templates và tạo lại template
- Đảm bảo con trỏ chuột đúng vị trí số 8 khi tạo template
- Kiểm tra độ phân giải màn hình
```

**3. Confidence score thấp**
```
Solution:
- Kiểm tra chất lượng template
- Điều chỉnh ngưỡng THRESHOLD trong code
- Thử tạo lại template với lighting conditions tốt hơn
```

**4. Script chạy chậm**
```
Solution:
- Giảm số lượng scale factors trong find_digit_adaptive()
- Tăng DELAY_BETWEEN_CLICKS nếu cần
- Đóng các ứng dụng không cần thiết
```

## 📁 Cấu trúc Logs

### Click Logs (click_logs/)
```
click_log_YYYYMMDD_HHMMSS.txt
├── Timestamp bắt đầu
├── Thông tin cửa sổ game
├── Mật khẩu sử dụng
├── Chi tiết các lần click
└── Timestamp kết thúc
```

### Confirm Logs (confirm_logs/)
```
confirm_log_YYYYMMDD_HHMMSS.txt
├── Thông tin session
├── Cấu hình sử dụng
├── Screenshots/ (ảnh chụp khu vực click)
└── Chi tiết từng lần thử
```

## ⚠️ Lưu ý quan trọng

1. **Game phải đang chạy** trước khi chạy script
2. **Không di chuyển chuột** trong quá trình script hoạt động
3. **Template được tạo 1 lần** cho mỗi độ phân giải
4. **Backup templates** quan trọng trước khi update
5. **Kiểm tra logs** để debug khi có lỗi

## 🔄 Update và Maintenance

### Cập nhật template
```bash
# Xóa template cũ
rmdir /s digit_templates
rmdir /s button_templates

# Chạy lại script để tạo template mới
python auto_input_fc.py
```

### Cleanup logs
```bash
# Logs tự động cleanup khi chạy script mới
# Hoặc xóa thủ công:
rmdir /s click_logs
rmdir /s confirm_logs
```

## 📞 Hỗ trợ

Nếu gặp vấn đề, hãy kiểm tra:
1. File logs trong thư mục tương ứng
2. Screenshots trong confirm_logs/screenshots/
3. Template files có được tạo đúng không
4. Cấu hình JSON có hợp lệ không

## 🏷️ Version History

- **v1.0**: Basic password input automation
- **v1.1**: Added confirm button clicking
- **v1.2**: Adaptive scaling support
- **v1.3**: Enhanced logging and error handling

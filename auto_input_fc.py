import pyautogui
import pygetwindow as gw
import cv2
import numpy as np
import os
import time
import json
import ctypes
import shutil
from datetime import datetime

# === Cau hinh ===
TEMPLATE_DIR = "digit_templates"
CONFIG_FILE = "config.json"
LOG_DIR = "click_logs"
THRESHOLD = 0.8
DELAY_BETWEEN_CLICKS = 0.25

# Set DPI Awareness
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

def cleanup_old_logs():
    if os.path.exists(LOG_DIR):
        try:
            shutil.rmtree(LOG_DIR)
            print(f"Da xoa thu muc nhat ky cu: {LOG_DIR}")
        except Exception as e:
            print(f"Loi khi xoa nhat ky cu: {e}")

def setup_logging():
    cleanup_old_logs()
    os.makedirs(LOG_DIR, exist_ok=True)
    log_filename = f"click_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    return os.path.join(LOG_DIR, log_filename)

def get_fc_window():
    for title in ["FC ONLINE", "FC Online"]:
        wins = gw.getWindowsWithTitle(title)
        if wins:
            return wins[0]
    raise Exception("Khong tim thay cua so FC ONLINE")

def screenshot_window(window):
    """Chup toan bo cua so game - khong ep kich thuoc"""
    img = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR), (window.left, window.top)

def calculate_template_scale(window_width, window_height):
    """Tinh toan scale factor tu dong"""
    base_width, base_height = 640, 480
    scale_x = window_width / base_width
    scale_y = window_height / base_height
    return min(scale_x, scale_y)

def find_digit_adaptive(frame, template_path, window_size):
    """Tim so voi scale tu dong"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    
    if template is None:
        return None, 0, "unknown"
    
    base_scale = calculate_template_scale(window_size[0], window_size[1])
    scale_factors = [base_scale * 0.7, base_scale * 0.85, base_scale, base_scale * 1.15, base_scale * 1.3]
    
    best_confidence = 0
    best_position = None
    
    for scale in scale_factors:
        new_w = max(10, int(template.shape[1] * scale))
        new_h = max(10, int(template.shape[0] * scale))
        
        if new_h > gray.shape[0] or new_w > gray.shape[1]:
            continue
            
        scaled_template = cv2.resize(template, (new_w, new_h))
        res = cv2.matchTemplate(gray, scaled_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        
        if max_val > best_confidence and max_val >= THRESHOLD:
            best_confidence = max_val
            best_position = (max_loc[0] + new_w // 2, max_loc[1] + new_h // 2)
            print(f"Do phan giai {window_size[0]}x{window_size[1]}, Scale {scale:.2f}: Confidence {max_val:.3f}")
    
    return best_position, best_confidence

def get_or_create_template(window_size):
    """Lay hoac tao template phu hop voi do phan giai hien tai"""
    template_filename = f"8_{window_size[0]}x{window_size[1]}.png"
    template_path = os.path.join(TEMPLATE_DIR, template_filename)
    
    if os.path.exists(template_path):
        print(f"Su dung template co san: {template_filename}")
        return template_path
    
    # Tao template moi
    print(f"Chua co template cho do phan giai {window_size[0]}x{window_size[1]}")
    print("=== TAO TEMPLATE MOI ===")
    print("Hay di chuot den so 8 tren ban phim game")
    input("Nhan Enter khi san sang...")
    
    x, y = pyautogui.position()
    
    # Template size tu dong theo do phan giai
    base_size = 25
    scale_factor = min(window_size[0] / 640, window_size[1] / 480)
    template_size = int(base_size * scale_factor)
    
    region = (x-template_size//2, y-template_size//2, template_size, template_size)
    
    try:
        img = pyautogui.screenshot(region=region)
        template = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        
        os.makedirs(TEMPLATE_DIR, exist_ok=True)
        cv2.imwrite(template_path, template)
        
        print(f"Da tao template: {template_path}")
        print(f"Kich thuoc template: {template_size}x{template_size}")
        return template_path
    except Exception as e:
        print(f"Loi tao template: {e}")
        return None

def load_config():
    default_config = {"password": "8888"}
    
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(default_config, f, indent=4)
        print(f"Tao file {CONFIG_FILE} voi mat khau mac dinh: 8888")
    
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    
    return config.get("password", "8888")

def main():
    # Khoi tao logging
    log_file = setup_logging()
    print(f"File nhat ky: {log_file}")
    
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"BAT DAU CHUONG TRINH - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n")
    
    # Doc mat khau
    password = load_config()
    print(f"Mat khau can nhap: {password}")
    
    # Tim cua so game
    win = get_fc_window()
    print(f"Tim thay cua so: {win.title}")
    print(f"Do phan giai cua so: {win.width}x{win.height}")
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"Cua so: {win.title}\n")
        f.write(f"Do phan giai: {win.width}x{win.height}\n")
        f.write(f"Mat khau: {password}\n")
    
    # Chup man hinh
    frame, win_pos = screenshot_window(win)
    print(f"Kich thuoc anh chup: {frame.shape[1]}x{frame.shape[0]}")
    
    # Lay hoac tao template phu hop
    window_size = (win.width, win.height)
    template_path = get_or_create_template(window_size)
    
    if not template_path:
        print("Khong the tao hoac tim thay template")
        return
    
    # Tim so 8 voi scale tu dong
    print("Dang tim so 8...")
    pos, confidence = find_digit_adaptive(frame, template_path, window_size)
    
    if not pos:
        print("Khong tim thay so 8!")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write("LOI: Khong tim thay so 8!\n")
        return
    
    # Tinh vi tri click
    abs_x = win_pos[0] + pos[0]
    abs_y = win_pos[1] + pos[1]
    
    print(f"Vi tri so 8: ({pos[0]}, {pos[1]})")
    print(f"Click tai: ({abs_x}, {abs_y})")
    
    # Click mat khau
    print(f"Bat dau nhap {len(password)} lan...")
    
    for i, digit in enumerate(password):
        if digit == '8':
            pyautogui.click(abs_x, abs_y)
            print(f"Click lan {i+1}")
            time.sleep(DELAY_BETWEEN_CLICKS)
    
    # Ghi ket thuc
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"KET THUC - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n")
    
    print("Hoan thanh!")
    print(f"Xem nhat ky tai: {LOG_DIR}")

if __name__ == "__main__":
    main()
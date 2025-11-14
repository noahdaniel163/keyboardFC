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
TEMPLATE_DIR = "button_templates"
CONFIG_FILE = "config_confirm.json"
LOG_DIR = "confirm_logs"
THRESHOLD = 0.75
DELAY_BEFORE_CLICK = 1.0

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
    log_filename = f"confirm_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    return os.path.join(LOG_DIR, log_filename)

def log_action(log_file, action_type, pos, abs_pos, confidence, screenshot_path=None):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"=== {action_type} - {timestamp} ===\n")
        f.write(f"Vi tri tuong doi: ({pos[0]}, {pos[1]})\n")
        f.write(f"Vi tri tuyet doi: ({abs_pos[0]}, {abs_pos[1]})\n")
        f.write(f"Do tin cay: {confidence:.3f}\n")
        if screenshot_path:
            f.write(f"Anh chup: {screenshot_path}\n")
        f.write("-" * 50 + "\n")
    
    print(f"[LOG] {action_type}: ({abs_pos[0]}, {abs_pos[1]}) - Tin cay: {confidence:.3f}")

def capture_region(click_count, click_pos, region_size=150):
    try:
        x1 = max(0, click_pos[0] - region_size//2)
        y1 = max(0, click_pos[1] - region_size//2)
        x2 = min(pyautogui.size().width, click_pos[0] + region_size//2)
        y2 = min(pyautogui.size().height, click_pos[1] + region_size//2)
        
        region_img = pyautogui.screenshot(region=(x1, y1, x2-x1, y2-y1))
        
        screenshot_dir = os.path.join(LOG_DIR, "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshot_dir, f"confirm_{click_count}_{datetime.now().strftime('%H%M%S')}.png")
        region_img.save(screenshot_path)
        
        return screenshot_path
    except Exception as e:
        print(f"Loi chup man hinh: {e}")
        return None

def get_fc_window():
    for title in ["FC ONLINE", "FC Online"]:
        wins = gw.getWindowsWithTitle(title)
        if wins:
            return wins[0]
    raise Exception("Khong tim thay cua so FC ONLINE")

def screenshot_window(window):
    img = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR), (window.left, window.top)

def find_button_adaptive(frame, template_path, window_size):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    
    if template is None:
        return None, 0
    
    base_width, base_height = 640, 480
    scale_x = window_size[0] / base_width
    scale_y = window_size[1] / base_height
    base_scale = min(scale_x, scale_y)
    
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

def get_or_create_button_template(button_type, window_size):
    template_filename = f"{button_type}_{window_size[0]}x{window_size[1]}.png"
    template_path = os.path.join(TEMPLATE_DIR, template_filename)
    
    if os.path.exists(template_path):
        print(f"Su dung template co san: {template_filename}")
        return template_path
    
    print(f"Chua co template cho nut {button_type} o do phan giai {window_size[0]}x{window_size[1]}")
    print(f"=== TAO TEMPLATE CHO NUT {button_type.upper()} ===")
    print(f"Hay di chuot den nut {button_type} tren game")
    input("Nhan Enter khi san sang...")
    
    x, y = pyautogui.position()
    
    base_size = 40
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

def load_confirm_config():
    default_config = {
        "button_type": "confirm",
        "click_delay": 1.0,
        "max_attempts": 3
    }
    
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(default_config, f, indent=4)
        print(f"Tao file {CONFIG_FILE} voi cau hinh mac dinh")
    
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    
    return config

def main():
    log_file = setup_logging()
    print(f"File nhat ky: {log_file}")
    
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"BAT DAU CHUONG TRINH CLICK NUT XAC NHAN - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n")
    
    config = load_confirm_config()
    button_type = config.get("button_type", "confirm")
    click_delay = config.get("click_delay", 1.0)
    max_attempts = config.get("max_attempts", 3)
    
    print(f"Loai nut: {button_type}")
    print(f"Thoi gian cho: {click_delay} giay")
    print(f"So lan thu toi da: {max_attempts}")
    
    win = get_fc_window()
    print(f"Tim thay cua so: {win.title}")
    print(f"Do phan giai cua so: {win.width}x{win.height}")
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"Cua so: {win.title}\n")
        f.write(f"Do phan giai: {win.width}x{win.height}\n")
        f.write(f"Loai nut: {button_type}\n")
    
    window_size = (win.width, win.height)
    
    # Tim nut xac nhan
    for attempt in range(max_attempts):
        print(f"\n=== Lan thu {attempt + 1} ===")
        
        frame, win_pos = screenshot_window(win)
        print(f"Kich thuoc anh chup: {frame.shape[1]}x{frame.shape[0]}")
        
        template_path = get_or_create_button_template(button_type, window_size)
        
        if not template_path:
            print("Khong the tao hoac tim thay template")
            continue
        
        print(f"Dang tim nut {button_type}...")
        pos, confidence = find_button_adaptive(frame, template_path, window_size)
        
        if pos:
            abs_x = win_pos[0] + pos[0]
            abs_y = win_pos[1] + pos[1]
            
            print(f"Tim thay nut {button_type} tai: ({abs_x}, {abs_y})")
            
            # Ghi nhat ky
            screenshot_path = capture_region(attempt + 1, (abs_x, abs_y))
            log_action(log_file, f"CLICK_NUT_{button_type.upper()}", pos, (abs_x, abs_y), confidence, screenshot_path)
            
            # Cho truoc khi click
            print(f"Cho {click_delay} giay truoc khi click...")
            time.sleep(click_delay)
            
            # Click nut
            pyautogui.click(abs_x, abs_y)
            print(f"Da click nut {button_type}")
            
            # Ghi thanh cong
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"CLICK THANH CONG LAN {attempt + 1}\n")
            
            break
        else:
            print(f"Khong tim thay nut {button_type} lan thu {attempt + 1}")
            
            if attempt < max_attempts - 1:
                print("Cho 2 giay va thu lai...")
                time.sleep(2)
    
    else:
        print(f"Khong tim thay nut {button_type} sau {max_attempts} lan thu")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write("LOI: Khong tim thay nut xac nhan!\n")
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"KET THUC - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n")
    
    print("Hoan thanh!")
    print(f"Xem nhat ky tai: {LOG_DIR}")

if __name__ == "__main__":
    main()
    
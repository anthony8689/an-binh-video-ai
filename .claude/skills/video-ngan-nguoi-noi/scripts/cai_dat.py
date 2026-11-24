"""Cài bộ công cụ trên máy mới, chạy một lần.
  python cai_dat.py [thư mục kênh]
Kiểm FFmpeg, Node, thư viện Python; chép engine vào ~/.video-ngan/engine rồi npm install; tạo ho-so-kenh.json mẫu ở thư mục kênh.
Chỉ dùng thư viện chuẩn của Python để chạy được cả khi máy chưa có gì."""
import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
GOC = Path(__file__).resolve().parent.parent
ENGINE = Path.home() / ".video-ngan" / "engine"
THU_VIEN = {"faster_whisper": "faster-whisper", "cv2": "opencv-python", "numpy": "numpy", "google.auth": "google-auth", "requests": "requests", "playwright": "playwright"}
thieu = []


def co(lenh):
    tim = shutil.which(lenh)
    print(("✔ " if tim else "✘ ") + lenh + (f": {tim}" if tim else " chưa có"))
    if not tim:
        thieu.append(lenh)


co("ffmpeg")
co("ffprobe")
co("node")
co("npm")
if thieu:
    print("\nCài các công cụ còn thiếu rồi chạy lại:\n  FFmpeg: https://ffmpeg.org/download.html (thêm vào PATH)\n  Node.js bản LTS: https://nodejs.org")
    sys.exit(1)

can_pip = [p for m, p in THU_VIEN.items() if importlib.util.find_spec(m) is None]
co_gpu = shutil.which("nvidia-smi") is not None and subprocess.run(["nvidia-smi", "-L"], capture_output=True).returncode == 0
if co_gpu and importlib.util.find_spec("nvidia") is None:
    can_pip += ["nvidia-cublas-cu12", "nvidia-cudnn-cu12"]
print("✔ có GPU NVIDIA" if co_gpu else "⚠ không thấy GPU NVIDIA, phần nghe lời sẽ chạy CPU, chậm hơn nhiều")
if can_pip:
    print("Cài thư viện Python:", ", ".join(can_pip))
    subprocess.run([sys.executable, "-m", "pip", "install", *can_pip], check=True)
subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
print("✔ thư viện Python đủ. Python dùng cho mọi lệnh sau:", sys.executable)

ENGINE.mkdir(parents=True, exist_ok=True)
shutil.copytree(GOC / "engine", ENGINE, dirs_exist_ok=True)
if not (ENGINE / "node_modules").exists():
    print("Cài Remotion (vài phút)...")
    subprocess.run(["npm.cmd" if sys.platform == "win32" else "npm", "install", "--no-audit", "--no-fund"], cwd=ENGINE, check=True)
print("✔ engine:", ENGINE)

if len(sys.argv) > 1:
    kenh = Path(sys.argv[1])
    kenh.mkdir(parents=True, exist_ok=True)
    f = kenh / "ho-so-kenh.json"
    if f.exists():
        print("✔ đã có", f, "(giữ nguyên)")
    else:
        shutil.copy2(GOC / "references" / "ho-so-kenh.mau.json", f)
        print("✔ tạo", f, "- mở file này điền thông tin kênh")
    (kenh / "kho-canh").mkdir(exist_ok=True)
    (kenh / "du-an").mkdir(exist_ok=True)
print("\nCài xong. Whisper tải mô hình large-v3 (khoảng 3 GB) ở lần chạy đầu. GPU NVIDIA giúp nhanh hơn nhiều, không có vẫn chạy được.")

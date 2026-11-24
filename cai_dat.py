"""Cài bộ làm video AI của An Bình AI lên máy Windows của học viên.

Cách chạy (PowerShell, trong thư mục kho vừa tải về):
    python cai_dat.py            kiểm + tự cài phần mềm còn thiếu + chép skill/agent
    python cai_dat.py --chi-kiem chỉ kiểm, không cài gì (vẫn chép skill/agent nếu chưa có)

Việc script làm:
1. Kiểm Python 3.10+, FFmpeg, Node.js, Git, yt-dlp, faster-whisper, edge-tts.
   Thiếu thì tự cài bằng winget / pip, cài xong kiểm lại.
   Bị chặn (diệt virus, thiếu quyền, không có winget) thì in đúng lệnh PowerShell để tự dán.
2. Chép skill vào %USERPROFILE%\\.claude\\skills và agent vào %USERPROFILE%\\.claude\\agents.
   KHÔNG ghi đè tệp đã có: tệp trùng tên thì bỏ qua và báo lại.
3. Đủ hết thì in "MÁY SẴN SÀNG".
"""
import argparse
import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

KHO = Path(__file__).resolve().parent
NGUON_SKILL = KHO / ".claude" / "skills"
NGUON_AGENT = KHO / ".claude" / "agents"
WINGET_CO = ["--accept-source-agreements", "--accept-package-agreements", "--silent", "-e"]


def nha():
    return Path(os.environ.get("USERPROFILE") or Path.home())


def chay(lenh, giay=900):
    try:
        r = subprocess.run(lenh, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=giay)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except FileNotFoundError:
        return 127, "không tìm thấy lệnh"
    except subprocess.TimeoutExpired:
        return 124, "quá thời gian"
    except Exception as e:  # noqa: BLE001
        return 1, str(e)


def nap_lai_path():
    """winget cài xong chưa vào PATH của cửa sổ đang mở: đọc lại PATH trong registry + thêm chỗ quen."""
    them = []
    try:
        import winreg
        for goc, khoa in ((winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
                          (winreg.HKEY_CURRENT_USER, "Environment")):
            try:
                with winreg.OpenKey(goc, khoa) as k:
                    v, _ = winreg.QueryValueEx(k, "Path")
                    them += [os.path.expandvars(x) for x in v.split(";") if x]
            except OSError:
                pass
    except ImportError:
        pass
    la = os.environ.get("LOCALAPPDATA", "")
    them += [os.path.join(la, "Microsoft", "WinGet", "Links"), r"C:\Program Files\nodejs", r"C:\Program Files\Git\cmd",
             os.path.join(os.path.dirname(sys.executable), "Scripts")]
    cu = os.environ.get("PATH", "").split(";")
    os.environ["PATH"] = ";".join(cu + [x for x in them if x and x not in cu])


def tim_ffmpeg_goi_winget():
    la = Path(os.environ.get("LOCALAPPDATA", ""))
    for f in (la / "Microsoft" / "WinGet" / "Packages").glob("Gyan.FFmpeg*/**/bin/ffmpeg.exe"):
        return f
    return None


def co_lenh(ten, doi_so="--version"):
    if ten == "ffmpeg" and not shutil.which("ffmpeg"):
        f = tim_ffmpeg_goi_winget()
        if f:
            os.environ["PATH"] += ";" + str(f.parent)
    if not shutil.which(ten):
        return None
    ma, ra = chay([ten, doi_so], 60)
    return ra.strip().splitlines()[0][:70] if ma == 0 and ra.strip() else None


def co_goi_py(mo_dun):
    return importlib.util.find_spec(mo_dun) is not None


# (tên hiển thị, hàm kiểm, lệnh tự cài, lệnh PowerShell để học viên tự dán)
PY = f'"{sys.executable}"'
MUC = [
    ("FFmpeg", lambda: co_lenh("ffmpeg", "-version"), ["winget", "install", "--id", "Gyan.FFmpeg"] + WINGET_CO,
     "winget install -e --id Gyan.FFmpeg"),
    ("Node.js", lambda: co_lenh("node"), ["winget", "install", "--id", "OpenJS.NodeJS.LTS"] + WINGET_CO,
     "winget install -e --id OpenJS.NodeJS.LTS"),
    ("Git", lambda: co_lenh("git"), ["winget", "install", "--id", "Git.Git"] + WINGET_CO,
     "winget install -e --id Git.Git"),
    ("yt-dlp", lambda: co_lenh("yt-dlp") or ("có (gói Python)" if co_goi_py("yt_dlp") else None),
     [sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"], f"& {PY} -m pip install --upgrade yt-dlp"),
    ("faster-whisper", lambda: "có" if co_goi_py("faster_whisper") else None,
     [sys.executable, "-m", "pip", "install", "faster-whisper"], f"& {PY} -m pip install faster-whisper"),
    ("edge-tts", lambda: "có" if co_goi_py("edge_tts") else None,
     [sys.executable, "-m", "pip", "install", "edge-tts"], f"& {PY} -m pip install edge-tts"),
]


def kiem_python():
    v = sys.version_info
    if v < (3, 10):
        print(f"  ✘ Python {v.major}.{v.minor} quá cũ (cần 3.10 trở lên).")
        print("    Dán lệnh này vào PowerShell, cài xong đóng mở lại PowerShell rồi chạy lại cai_dat.py:")
        print("    winget install -e --id Python.Python.3.12")
        return False
    print(f"  ✔ Python {v.major}.{v.minor}.{v.micro}")
    return True


def kiem_va_cai(chi_kiem):
    thieu = []
    for ten, kiem, cai, lenh_tay in MUC:
        kq = kiem()
        if kq:
            print(f"  ✔ {ten}: {kq}")
            continue
        if chi_kiem:
            print(f"  ✘ {ten}: chưa có")
            thieu.append((ten, lenh_tay))
            continue
        if cai[0] == "winget" and not shutil.which("winget"):
            print(f"  ✘ {ten}: chưa có, máy không có winget để tự cài")
            thieu.append((ten, lenh_tay))
            continue
        print(f"  … {ten}: chưa có, đang tự cài (có thể mất vài phút)…")
        ma, ra = chay(cai)
        nap_lai_path()
        importlib.invalidate_caches()
        kq = kiem()
        if kq:
            print(f"  ✔ {ten}: đã cài xong ({kq})")
        else:
            ly_do = "bị chặn (diệt virus hoặc thiếu quyền)" if ma not in (0, 124) else ("quá thời gian" if ma == 124 else "cài xong nhưng chưa nhận, cần mở lại PowerShell")
            print(f"  ✘ {ten}: tự cài không được — {ly_do}")
            dong = [x for x in ra.strip().splitlines() if x.strip()][-2:]
            for x in dong:
                print(f"      {x[:150]}")
            thieu.append((ten, lenh_tay))
    return thieu


def chep(nguon, dich, ten_nhom):
    """Chép cây thư mục, KHÔNG ghi đè tệp đã có. Trả (số tệp chép, danh sách trùng)."""
    if not nguon.is_dir():
        print(f"  ✘ Không thấy {nguon} — tải lại kho cho đủ.")
        return 0, []
    da_chep, trung = 0, []
    for f in sorted(nguon.rglob("*")):
        if not f.is_file() or "__pycache__" in f.parts:
            continue
        dich_f = dich / f.relative_to(nguon)
        if dich_f.exists():
            trung.append(dich_f)
            continue
        dich_f.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dich_f)
        da_chep += 1
    so = len([d for d in nguon.iterdir() if d.is_dir()]) if ten_nhom == "skill" else len(list(nguon.glob("*.md")))
    print(f"  ✔ {ten_nhom}: {so} {ten_nhom} → {dich} (chép {da_chep} tệp, bỏ qua {len(trung)} tệp đã có)")
    return da_chep, trung


def main():
    ap = argparse.ArgumentParser(description="Cài bộ làm video AI của An Bình AI")
    ap.add_argument("--chi-kiem", action="store_true", help="chỉ kiểm, không tự cài phần mềm")
    a = ap.parse_args()

    print("=== BỘ LÀM VIDEO AI — AN BÌNH AI ===")
    print("Bước 1: kiểm phần mềm")
    if not kiem_python():
        print("\nMÁY CHƯA SẴN SÀNG")
        sys.exit(1)
    nap_lai_path()
    thieu = kiem_va_cai(a.chi_kiem)

    print("\nBước 2: chép skill và agent vào máy")
    claude = nha() / ".claude"
    _, trung_s = chep(NGUON_SKILL, claude / "skills", "skill")
    _, trung_a = chep(NGUON_AGENT, claude / "agents", "agent")
    trung = trung_s + trung_a
    if trung:
        print(f"  ⚠ {len(trung)} tệp đã có sẵn trên máy nên KHÔNG ghi đè (giữ bản của bạn):")
        nhom = {}
        for f in trung:
            r = f.relative_to(claude)
            k = str(Path(*r.parts[:2])) if r.parts[0] == "skills" else str(r)
            nhom[k] = nhom.get(k, 0) + 1
        for k, n in sorted(nhom.items()):
            print(f"      {k}  ({n} tệp trùng)")
        print("    Muốn dùng bản mới của kho: đổi tên/cất thư mục cũ rồi chạy lại cai_dat.py.")

    print()
    if thieu:
        print("Còn thiếu phần mềm. Mở PowerShell (chuột phải → Run as administrator nếu bị chặn quyền), dán từng lệnh:")
        for ten, lenh in thieu:
            print(f"    {lenh}        # {ten}")
        print("Dán xong đóng PowerShell, mở lại rồi chạy: python cai_dat.py")
        print("\nMÁY CHƯA SẴN SÀNG")
        sys.exit(1)
    print("Mở Claude Code trong thư mục làm việc của bạn và gõ thử:")
    print('    Edit video <tên file> cho tôi')
    print('    Dựng một video giới thiệu bản thân cho tôi theo cấu trúc BNI')
    print("\nMÁY SẴN SÀNG")


if __name__ == "__main__":
    main()

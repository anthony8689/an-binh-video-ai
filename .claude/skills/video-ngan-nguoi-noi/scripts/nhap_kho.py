"""Tự nhận gói KHO-HOC-VIEN (cảnh AI không người, nhạc, tiếng hiệu ứng) cho thư mục kênh (24/11/2026).

  python nhap_kho.py "<thư mục kênh>"

Tìm KHO-HOC-VIEN*.zip hoặc thư mục KHO-HOC-VIEN ở: thư mục kênh, thư mục cha của nó, Downloads, Desktop, Documents.
Kho cảnh của kênh còn trống thì giải nén kho-canh/ và tai-nguyen/ vào thư mục kênh (không ghi đè tệp đã có),
rồi điền boNhac, boTieng, nhac, tiengChuyenCanh vào ho-so-kenh.json nếu các mục đó còn trống hoặc trỏ tới file không có.
Không thấy gói thì im lặng bỏ qua: bni.py, tron_am.py vẫn chạy được (nền màu tự tạo, chỉ có giọng)."""
import json
import shutil
import sys
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
NHAC = ("beat-vlog", "phonk", "future-bass")
TIENG = ("luot", "luot-manh", "hien-the", "thong-bao", "chup", "nhieu", "thanh-cong")


def tim_goi(kenh: Path):
    nha = Path.home()
    for cho in (kenh, kenh.parent, nha / "Downloads", nha / "Desktop", nha / "Documents"):
        if not cho.is_dir():
            continue
        thu_muc = cho / "KHO-HOC-VIEN"
        if (thu_muc / "kho-canh").is_dir():
            return thu_muc
        zips = sorted(cho.glob("KHO-HOC-VIEN*.zip"), key=lambda f: f.stat().st_mtime, reverse=True)
        if zips:
            return zips[0]
    return None


def kho_trong(kenh: Path):
    k = kenh / "kho-canh"
    return not k.is_dir() or not any(k.rglob("*.mp4"))


def nhap(kenh) -> bool:
    kenh = Path(kenh)
    if not kho_trong(kenh):
        dien_ho_so(kenh)
        return False
    goi = tim_goi(kenh)
    if goi is None:
        return False
    print(f"• thấy gói kho {goi}: đang chép cảnh, nhạc vào {kenh} (vài phút lần đầu)")
    if goi.is_dir():
        for x in ("kho-canh", "tai-nguyen"):
            if (goi / x).is_dir():
                shutil.copytree(goi / x, kenh / x, dirs_exist_ok=True)
    else:
        with zipfile.ZipFile(goi) as z:
            for ten in z.namelist():
                if ten.endswith("/") or ".." in ten:
                    continue
                phan = ten.split("/", 1)[1] if ten.startswith("KHO-HOC-VIEN/") else ten
                if not phan.startswith(("kho-canh/", "tai-nguyen/")):
                    continue
                dich = kenh / phan
                if dich.exists():
                    continue
                dich.parent.mkdir(parents=True, exist_ok=True)
                with z.open(ten) as nguon, open(dich, "wb") as ra:
                    shutil.copyfileobj(nguon, ra)
    dien_ho_so(kenh)
    so = sum(1 for _ in (kenh / "kho-canh").rglob("*.mp4"))
    print(f"✔ đã nhận kho: {so} cảnh không người, nhạc {', '.join(NHAC)}")
    return True


def dien_ho_so(kenh: Path):
    f = kenh / "ho-so-kenh.json"
    if not f.exists():
        return
    h = json.loads(f.read_text(encoding="utf-8"))
    co = lambda p: bool(p) and (kenh / p).is_file()  # noqa: E731
    doi = False
    bo_nhac = h.get("boNhac") or {}
    for n in NHAC:
        p = f"tai-nguyen/nhac/{n}.mp3"
        if n not in bo_nhac and co(p):
            bo_nhac[n] = {"file": p, "tu": 9.5} if n == "future-bass" else p
            doi = True
    bo_tieng = h.get("boTieng") or {}
    for t in TIENG:
        p = f"tai-nguyen/am/{t}.wav"
        if t not in bo_tieng and co(p):
            bo_tieng[t] = p
            doi = True
    if not co(h.get("nhac")) and co("tai-nguyen/nhac/beat-vlog.mp3"):
        h["nhac"] = "tai-nguyen/nhac/beat-vlog.mp3"
        doi = True
    if not co(h.get("tiengChuyenCanh")) and co("tai-nguyen/am/luot.wav"):
        h["tiengChuyenCanh"] = "tai-nguyen/am/luot.wav"
        doi = True
    if doi:
        h["boNhac"], h["boTieng"] = bo_nhac, bo_tieng
        f.write_text(json.dumps(h, ensure_ascii=False, indent=2), encoding="utf-8")
        print("✔ hồ sơ kênh: đã khai nhạc và tiếng hiệu ứng từ kho")


if __name__ == "__main__":
    if not nhap(sys.argv[1]):
        print("• không có gói KHO-HOC-VIEN mới cần nhận (hoặc kho đã có)")

"""Trộn âm theo timeline.json: giọng giữ nguyên, nhạc thấp hơn giọng theo nhacDuoiGiong của hồ sơ (mặc định 10 LU), tiếng hiệu ứng khoảng -14 dBFS.
  python tron_am.py <thư mục dự án>
nhac.txt của dự án: tên trong boNhac của hồ sơ (giá trị là file, hoặc {"file", "tu"} để bỏ đoạn đầu) hoặc đường dẫn file. Không có thì dùng nhac của hồ sơ.
Cảnh trong canh.json có thể thêm: am (thay tiếng lúc vào cảnh), amMoc (phát ở mỗi mốc của cảnh). Giá trị là tên trong boTieng.
Trong boTieng, giá trị là file (phát 1,2 giây đầu) hoặc {"file", "dai"} để phát dai giây.
Ghi render/ra.mp4."""
import json
import re
import subprocess
import sys
from pathlib import Path

from chung import doc, duong_dan, ho_so
from kiem_chot import kiem_nhac

da = Path(sys.argv[1])
h = ho_so(da)
T = doc(da / "timeline.json")
GIONG_HET, TONG, MOC = T["het_tieng"], T["tong"], T["moc"]
bo_nhac, bo_tieng = h.get("boNhac", {}), h.get("boTieng", {})
chon = (da / "nhac.txt").read_text(encoding="utf-8").strip() if (da / "nhac.txt").exists() else ""
loi_nhac = kiem_nhac(chon)  # luật đã chốt số 11, máy kiểm (references/da-chot.json → nhacDuocDung)
if loi_nhac:
    sys.exit("✘ " + loi_nhac)
muc = bo_nhac.get(chon)
nhac_tu = muc.get("tu", 0) if isinstance(muc, dict) else 0  # bài vào nhịp muộn thì bỏ đoạn đầu
nhac = str(duong_dan(h, muc["file"] if isinstance(muc, dict) else muc)) if muc else chon or str(duong_dan(h, h["nhac"]))
DUOI_GIONG = h.get("nhacDuoiGiong", 10)  # nhạc thấp hơn giọng bao nhiêu LU; 22 dB từng làm nhạc gần như không nghe thấy
mac_dinh = str(duong_dan(h, h["tiengChuyenCanh"]))
DAI_TIENG = 1.2  # tiếng chuyển cảnh chỉ cần ngắn; tiếng dài khai "dai" trong boTieng
canh = doc(da / "props.json")["canh"] if (da / "props.json").exists() else []
hinh, master, ra = str(da / "render/hinh-cam.mp4"), str(da / "render/master.mp4"), str(da / "render/ra.mp4")


def do(file, loc):
    return subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-i", file, "-af", loc, "-vn", "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace").stderr


def tieng(ten):
    """Trả về (file, số giây phát)."""
    if ten not in bo_tieng:
        sys.exit(f"Không có tiếng '{ten}' trong boTieng của hồ sơ: {', '.join(bo_tieng) or 'trống'}")
    muc = bo_tieng[ten]
    if isinstance(muc, dict):
        return str(duong_dan(h, muc["file"])), float(muc.get("dai", DAI_TIENG))
    return str(duong_dan(h, muc)), DAI_TIENG


# Danh sách (giây, (file, số giây phát)) cần phát
phat = []
for t in MOC:
    c = next((x for x in canh if abs(x["tu"] - t) < 0.02), {})
    phat.append((t, tieng(c["am"]) if c.get("am") else (mac_dinh, DAI_TIENG)))
for c in canh:
    if c.get("amMoc"):
        phat += [(c["tu"] + m, tieng(c["amMoc"])) for m in c.get("moc", []) if isinstance(m, (int, float)) and m >= 0.25]
phat.sort(key=lambda x: x[0])

lufs_nhac = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", do(nhac, "ebur128=framelog=quiet"))[-1])
lufs_giong = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", do(master, "ebur128=framelog=quiet"))[-1])
g_nhac = lufs_giong - DUOI_GIONG - lufs_nhac
files = sorted({x for _, x in phat})
g_sfx = {f: -14 - float(re.findall(r"max_volume: (-?[\d.]+) dB", do(f, "volumedetect"))[-1]) for f in {f for f, _ in files}}
print(json.dumps({"giong_lufs": lufs_giong, "nhac_lufs": lufs_nhac, "gain_nhac_db": round(g_nhac, 1), "so_tieng": len(phat)}))

loc = [f"[1:a]apad=whole_dur={TONG}[g]",
       "[g]asplit=2[g][gk]",
       # Nhạc tự nén xuống khi có giọng, nhô lên ở chỗ nghỉ để bài có nhịp thở
       f"[2:a]atrim={nhac_tu}:{nhac_tu + TONG},asetpts=PTS-STARTPTS,volume={g_nhac:.2f}dB[n0]",
       "[n0][gk]sidechaincompress=threshold=0.05:ratio=2.5:attack=15:release=300[n1]",
       f"[n1]volume='if(gt(t,{GIONG_HET}),min(1+(t-{GIONG_HET})*3,2.2),1)':eval=frame,afade=t=in:d=0.3,afade=t=out:st={TONG - 1.2}:d=1.2[n]"]
vao = ["-i", hinh, "-i", master, "-i", nhac]
for k, (f, dai) in enumerate(files):
    vao += ["-i", f]
    dung = [i for i, x in enumerate(phat) if x[1] == (f, dai)]
    loc.append(f"[{3 + k}:a]atrim=0:{dai},afade=t=out:st={dai - 0.3:.2f}:d=0.3,volume={g_sfx[f]:.2f}dB,asplit={len(dung)}" + "".join(f"[s{i}]" for i in dung))
for i, (t, _) in enumerate(phat):
    loc.append(f"[s{i}]adelay={int(max(0, t - 0.12) * 1000)}:all=1[d{i}]")
loc.append("[g][n]" + "".join(f"[d{i}]" for i in range(len(phat))) + f"amix=inputs={2 + len(phat)}:normalize=0:duration=first,alimiter=limit=0.84:level=0[a]")
subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *vao, "-filter_complex", ";".join(loc),
                "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-t", str(TONG), "-movflags", "+faststart", ra], check=True)
print("xong", ra)

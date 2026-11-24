"""Edit nhanh một file quay người nói thành video dọc có phụ đề, nhạc nhẹ (24/11/2026, câu lệnh "Edit video <file> cho tôi").

  python edit.py "<thư mục kênh>" "<file quay>" [--ten <tên dự án>] [--tieu-de "DÒNG 1|DÒNG 2"] [--het]

Tự làm, không hỏi duyệt:
  1. Tạo <kênh>/du-an/<số>-edit-<tên>/, ghi doan.json (nguon), loai.txt = edit, nhac.txt.
  2. Nghe lời bằng Whisper, chia đảo tiếng (khe > 0,35 giây), BỎ: đảo chỉ có tiếng ậm ừ, đảo quá ngắn, lần nói hỏng
     (đảo sau bắt đầu giống đảo trước thì giữ lần sau, theo luật chọn lần nói sau cùng). Chỉ bỏ, không đảo thứ tự, không thêm lời.
  3. Ghi doan (mỗi đảo giữ thêm 0,08 giây đầu, 0,12 giây cuối), loi.txt (cụm ≤ 28 ký tự), canh.json:
     mở bằng nguoi-chu (tiêu đề lấy từ --tieu-de, không có thì 4–6 chữ đầu của câu đầu), còn lại là nguoi.
  4. Chạy dung.py: dừng ở ảnh soát (thêm --het để chạy một mạch tới thành phẩm).
Xem lại bo-cat.txt (đảo đã bỏ và lý do) trước khi giao.
"""
import argparse
import difflib
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

from whisper_vi import nghe

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ND = Path(__file__).resolve().parent
KHE = 0.35
AM_UM = {"ờ", "ừ", "ừm", "à", "ơ", "ừ", "hừm", "ạ", "ư", "um", "uhm", "ừa", "ờm"}


def khong_dau(s):
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn").replace("đ", "d")


def chu(w):
    return re.sub(r"[^\w]", "", w["word"].lower())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kenh")
    ap.add_argument("file")
    ap.add_argument("--ten")
    ap.add_argument("--tieu-de")
    ap.add_argument("--het", action="store_true")
    a = ap.parse_args()
    kenh, f = Path(a.kenh).resolve(), Path(a.file).resolve()
    if not (kenh / "ho-so-kenh.json").exists():
        sys.exit(f"✘ {kenh} chưa có ho-so-kenh.json, chạy cai_dat.py \"{kenh}\" trước.")
    from nhap_kho import nhap
    nhap(kenh)  # có gói KHO-HOC-VIEN trong Downloads thì tự nhận nhạc, cảnh
    du_an = kenh / "du-an"
    du_an.mkdir(exist_ok=True)
    so = 1 + max([int(m.group(1)) for x in du_an.iterdir() if (m := re.match(r"(\d+)-", x.name))] or [0])
    ten = a.ten or re.sub(r"[^a-z0-9]+", "-", khong_dau(f.stem)).strip("-")[:30] or "video"
    cu = sorted(du_an.glob(f"*-edit-{ten}"))
    da = cu[-1] if cu else du_an / f"{so:02d}-edit-{ten}"  # chạy lại cùng tên thì dùng lại dự án cũ
    da.mkdir(exist_ok=True)
    (da / "loai.txt").write_text("edit", encoding="utf-8")
    if not (da / "nhac.txt").exists():
        (da / "nhac.txt").write_text("beat-vlog", encoding="utf-8")
    print("dự án:", da)

    # File quay có viền đen (màn hình ngang nằm trong khung dọc): cắt viền, đặt hình giữa, nền là chính hình làm mờ
    cd = subprocess.run(["ffmpeg", "-hide_banner", "-ss", "2", "-t", "8", "-i", str(f), "-vf", "cropdetect=24:2:0", "-f", "null", "-"],
                        capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    m = re.findall(r"crop=(\d+):(\d+):(\d+):(\d+)", cd)
    wh = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(f)],
                        capture_output=True, text=True).stdout.strip().split(",")
    if m and len(wh) == 2:
        cw, ch, cx, cy = map(int, m[-1])
        W, H = int(wh[0]), int(wh[1])
        if ch < 0.85 * H or cw < 0.85 * W:
            lam = da / "nguon-doc-x14.mp4"  # x14: dải giữa phóng 1,4 lần
            if not lam.exists():
                print(f"• file có viền đen (hình thật {cw}x{ch} trong {W}x{H}): làm bản dọc nền mờ")
                subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(f), "-filter_complex",
                                f"[0]crop={cw}:{ch}:{cx}:{cy},split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:2[bg];"
                                f"[b]scale=1512:-2,crop=1080:ih[fg];[bg][fg]overlay=0:(H-h)/2,format=yuv420p",  # phóng 1,4 lần cho mặt to hơn
                                "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-c:a", "aac", "-b:a", "192k", str(lam)], check=True)
            f = lam

    # Khoảng lặng THẬT của âm thanh (silencedetect), dùng để lọc câu bịa, kéo điểm kết, tách khoảng ngừng
    sd = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(f), "-af", "silencedetect=noise=-32dB:d=0.25", "-vn", "-f", "null", "-"],
                        capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    lang = list(zip(map(float, re.findall(r"silence_start: ([\d.]+)", sd)), map(float, re.findall(r"silence_end: ([\d.]+)", sd))))

    def co_tieng(a0, b0):
        """Số giây có tiếng trong [a0, b0]."""
        return max(0.0, (b0 - a0) - sum(max(0.0, min(b0, y) - max(a0, x)) for x, y in lang))

    # 2. Nghe lời, chia đảo
    W = []
    for s_ in nghe(str(f)):
        ws = [w for w in s_["words"] if w["word"].strip()]
        dai = (ws[-1]["end"] - ws[0]["start"]) if ws else 0
        if len(ws) >= 4 and dai > 0 and len(ws) / dai > 7:
            # Whisper ghi giờ dồn lại (nhiều chữ trong thời gian ngắn). Hai khả năng:
            # - câu BỊA ("Hẹn gặp lại các bạn trong những video tiếp theo" ở cuối file): âm thanh thật gần như im -> bỏ;
            # - câu THẬT bị dồn giờ (17 chữ ghi 1,8 giây nhưng tiếng nói kéo 2,5 giây) -> giữ, đánh dấu để kéo điểm kết theo tiếng.
            #   Lần đầu (24/11) chỉ xét tốc độ đã bỏ nhầm nửa câu về lương; người chấm bắt được.
            am = co_tieng(ws[0]["start"], ws[-1]["end"] + 1.0)
            if len(ws) / max(am, 0.01) > 9:
                print(f"• bỏ câu Whisper bịa ({len(ws)} chữ, chỉ {am:.2f} giây có tiếng): {s_['text'][:60]}")
                continue
            # Nghe lại riêng vùng này (không nối ngữ cảnh câu trước): nghe cả file, Whisper từng chép lặp đầu câu trước
            # ("Các bạn sẽ được nhận lương hàng tháng") và ghi "700 .000." thay cho "700 đến 1.200 euro" (24/11/2026).
            ss = max(0.0, ws[0]["start"] - 3.0)
            lai = [w for x in nghe(str(f), ss=ss, t=ws[-1]["end"] + 1.2 - ss, vad=False) for w in x["words"] if w["word"].strip()]
            if lai:
                W = [w for w in W if w["start"] < ss - 0.05]
                ws = lai
                print(f"• nghe lại vùng {ss:.1f}–{ws[-1]['end']:.1f} giây vì Whisper ghi giờ dồn: {' '.join(w['word'].strip() for w in lai)[:70]}")
            else:
                for w in ws:
                    w["don"] = True
        if W:
            ws = [w for w in ws if w["start"] >= W[-1]["end"] - 0.05]  # bỏ chữ trùng giờ với vùng vừa nghe lại
        W += ws
    if not W:
        sys.exit("✘ Không nghe được lời nào trong file (file không có tiếng hoặc không phải tiếng Việt).")
    dao, hien = [], []
    for w in W:
        if hien and w["start"] - hien[-1]["end"] > KHE:
            dao.append(hien)
            hien = []
        hien.append(w)
    dao.append(hien)
    giu, bo = [], []
    for i, d in enumerate(dao):
        tu = [chu(w) for w in d if chu(w)]
        txt = " ".join(w["word"].strip() for w in d)
        if not tu or all(t in AM_UM for t in tu):
            bo.append((d, "ậm ừ"))
            continue
        if d[-1]["end"] - d[0]["start"] < 0.3 and len(tu) <= 1:
            bo.append((d, "quá ngắn"))
            continue
        # nói lại: đảo sau mở đầu giống đảo này thì đảo này là lần hỏng
        sau = next((x for x in dao[i + 1:i + 3]), None)
        if sau:
            tu_sau = [chu(w) for w in sau if chu(w)]
            n = min(len(tu), len(tu_sau), 6)
            if n >= 2 and difflib.SequenceMatcher(None, tu[:n], tu_sau[:n]).ratio() >= 0.75 and len(tu) <= len(tu_sau) + 2:
                bo.append((d, "nói lại ở đảo sau"))
                continue
        giu.append(d)
    (da / "bo-cat.txt").write_text("\n".join(f"[{d[0]['start']:.2f}-{d[-1]['end']:.2f}] ({ly}) " + " ".join(w['word'].strip() for w in d)
                                            for d, ly in bo) or "(không bỏ đảo nào ngoài khoảng lặng)", encoding="utf-8")
    print(f"✔ {len(dao)} đảo tiếng, giữ {len(giu)}, bỏ {len(bo)} (xem bo-cat.txt)")

    # Nói lại giữa chừng trong cùng một đảo ("...được nhận lương hàng | Các bạn sẽ được nhận lương hàng tháng..."):
    # một chuỗi ≥ 4 chữ xuất hiện lại trong vòng 12 chữ thì bỏ lần nói trước (từ chỗ bắt đầu lần trước tới trước lần sau)
    moi = []
    for d in giu:
        while True:
            t = [chu(w) for w in d]
            cat = None
            for k in (6, 5, 4):
                for i in range(k, len(t) - k + 1):
                    for j in range(max(0, i - 12), i):
                        if t[j:j + k] == t[i:i + k] and all(t[j:j + k]):
                            cat = (j, i)
                            break
                    if cat:
                        break
                if cat:
                    break
            if not cat:
                break
            j, i = cat
            print(f"• bỏ lần nói hỏng: {' '.join(w['word'].strip() for w in d[j:i])}")
            if j:
                moi.append(d[:j])
            d = d[i:]
        moi.append(d)
    giu = [d for d in moi if d]

    # Lặp chữ ở chỗ nối (nói "các bạn" rồi ngừng, nói lại "các bạn ..."): bỏ phần lặp ở cuối đảo trước, giữ lần sau
    for k in range(len(giu) - 1):
        a_, b_ = [chu(w) for w in giu[k]], [chu(w) for w in giu[k + 1]]
        for n in range(min(8, len(a_) - 1, len(b_)), 0, -1):
            if a_[-n:] == b_[:n]:
                giu[k] = giu[k][:-n]
                print(f"• bỏ chữ lặp ở chỗ nối: {' '.join(b_[:n])}")
                break

    # 3. doan: đúng giờ chữ đầu, chữ cuối (lap_master.py tự đệm 0,06 giây đầu, 0,12 giây cuối, không đệm thêm).
    #    Tách đoạn ở khoảng lặng THẬT > 0,45 giây bên trong (đo bằng âm thanh, Whisper hay nuốt khoảng ngừng).
    doan = []
    for k_, d in enumerate(giu):
        a0, b0 = d[0]["start"], d[-1]["end"]
        dau = a0
        con_tieng = not any(x <= b0 + 0.15 <= y or b0 <= x <= b0 + 0.15 for x, y in lang)
        if con_tieng and d[-1].get("don"):
            # câu bị dồn giờ: kéo điểm kết tới chỗ tiếng thật dừng, không quá đầu đảo sau
            sau = [x for x, y in lang if x > b0]
            tran = giu[k_ + 1][0]["start"] - 0.1 if k_ + 1 < len(giu) else 1e9
            b0 = min(sau[0] if sau else b0 + 1.5, tran, b0 + 2.0)
        elif con_tieng:
            # tiếng còn kéo sau chữ cuối mà Whisper không ghi (thường là mẩu nói hỏng trước khi nói lại): cắt sát chữ cuối,
            # vì lap_master.py còn đệm thêm 0,12 giây
            b0 -= 0.1
        for x, y in [(x, y) for x, y in lang if x > a0 + 0.2 and y < b0 - 0.2 and y - x > 0.45]:
            doan.append([0, round(dau, 2), round(x + 0.1, 2)])
            dau = y - 0.1
        doan.append([0, round(dau, 2), round(b0, 2)])
    (da / "doan.json").write_text(json.dumps({"nguon": [str(f)], "doan": doan, "toc": 1.0}, ensure_ascii=False), encoding="utf-8")
    # Phụ đề: gộp mẩu bắt đầu bằng dấu câu vào chữ trước ("700" ".000" -> "700.000"); khi dòng sắp quá 28 ký tự thì
    # ngắt trước chữ nối (và, thì, mà, để, của...) gần nhất, tránh cắt đôi từ ghép ("tương / lai", "sinh / viên")
    NOI = {"và", "thì", "mà", "để", "của", "cho", "với", "nhưng", "là", "sẽ", "đã", "không", "các", "những", "một", "khi",
           "nếu", "vì", "nên", "trong", "tại", "từ", "đến", "về", "ở", "hay", "hoặc", "rằng", "được", "có"}
    tat_ca = []
    for d in giu:
        for w in d:
            t = w["word"].strip()
            if tat_ca and re.match(r"^[.,%]\w", t):
                tat_ca[-1] += t
            else:
                tat_ca.append(t)
    # cắt theo dấu câu trước, rồi chia đôi vế dài ở chữ nối gần giữa nhất (không có thì ở giữa)
    ve, hien_ve = [], []
    for t in tat_ca:
        hien_ve.append(t)
        if re.search(r"[.,!?;:]$", t):
            ve.append(hien_ve)
            hien_ve = []
    if hien_ve:
        ve.append(hien_ve)

    def chia(ws_):
        if len(" ".join(ws_)) <= 28 or len(ws_) < 4:
            return [" ".join(ws_)]
        giua = len(ws_) / 2
        cho = [i for i in range(2, len(ws_) - 1) if ws_[i].lower().strip(",.") in NOI]
        i = min(cho, key=lambda x: abs(x - giua)) if cho else round(giua)
        return chia(ws_[:i]) + chia(ws_[i:])

    dong = [x for v in ve for x in chia(v)]
    # gộp mẩu quá ngắn (dưới 10 ký tự) vào dòng sau nếu vừa
    gon = []
    for x in dong:
        if gon and len(gon[-1]) < 10 and len(gon[-1]) + 1 + len(x) <= 28:
            gon[-1] += " " + x
        else:
            gon.append(x)
    dong = gon
    dong[0] = dong[0][:1].upper() + dong[0][1:]
    (da / "loi.txt").write_text("\n".join(dong) + "\n", encoding="utf-8")
    if a.tieu_de:
        tren, _, duoi = a.tieu_de.partition("|")
    else:
        tu0 = re.sub(r"[.,!?]", "", dong[0]).split()
        tren, duoi = " ".join(tu0[:3]).upper(), " ".join(tu0[3:6]).upper()
    mo = min(4, max(1, len(dong) - 1))
    canh = [{"loai": "nguoi-chu", "tu": 0, "den": mo + 1, "tren": tren, "duoi": duoi, "at": 3, "viTriPhuDe": 1560},
            {"loai": "nguoi", "tu": mo + 1, "den": "het", "viTriPhuDe": 1560}]
    if len(dong) <= 2:
        canh = [canh[0] | {"den": "het"}]
    (da / "canh.json").write_text(json.dumps({"canh": canh}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✔ loi.txt {len(dong)} dòng; tiêu đề: {tren} / {duoi}")

    # 4. Dựng
    r = subprocess.run([sys.executable, ND / "dung.py", da, *(["--het"] if a.het else [])])
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()

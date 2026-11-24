# An Bình AI — Bộ làm video AI cho Claude Code

Kho phục vụ buổi học làm video AI ngày 24/11/2026.

**An Bình AI** đào tạo và triển khai AI Agent cho chủ shop, hộ kinh doanh và doanh nghiệp nhỏ tại Việt Nam. Kho này là bộ **skill + agent** để Claude Code trên máy Windows tự dựng video: edit video quay thô, video giới thiệu bản thân BNI, video KOL AI bán hàng, lookbook, video cây cảnh, ảnh bìa.

## Dùng ngay: 2 câu lệnh

Mở Claude Code trong thư mục làm việc của bạn (nơi để file video), gõ một trong hai câu:

```
Edit video [tên file] cho tôi
```
→ skill `ab-edit` tự tìm file, cắt lời thừa, chỉnh màu da, lọc ồn, thêm phụ đề và nhạc nền không lời, rồi agent `nguoi-dung-video` dựng và agent `nguoi-soat-video` soát độc lập. Lỗi thì tự sửa. Bạn nhận video kèm phiếu chấm.

```
Dựng một video giới thiệu bản thân cho tôi theo cấu trúc BNI
```
→ skill `video-ngan-nguoi-noi` hỏi bạn **một lượt** thông tin còn thiếu (tên, nghề, giúp ai, bằng chứng, khách lý tưởng, liên hệ), tự viết lời 5 phần BNI khoảng 30 giây, dùng ảnh/video của bạn nếu có (thả vào thư mục `anh-video-cua-toi`), không có thì làm chế độ không mặt với giọng đọc AI miễn phí. Xong cũng qua `nguoi-soat-video` và báo kèm phiếu chấm.

Không cần duyệt từng bước. Claude không tự đăng video lên mạng xã hội.

## Cài đặt (một lần)

1. Cài **Claude Code** và đăng nhập.
2. Tải kho này về (nút **Code → Download ZIP**, giải nén) hoặc `git clone https://github.com/anthony8689/an-binh-video-ai`.
3. Mở PowerShell trong thư mục kho, chạy:
   ```
   python cai_dat.py
   ```
   Script kiểm và tự cài phần mềm còn thiếu (winget/pip), chép skill vào `%USERPROFILE%\.claude\skills` và agent vào `%USERPROFILE%\.claude\agents` (**không ghi đè** tệp bạn đã có), cuối cùng in **MÁY SẴN SÀNG**. Bị diệt virus hoặc thiếu quyền chặn thì script in đúng lệnh PowerShell để bạn tự dán.
4. Mở lại Claude Code để nạp skill và agent mới.
5. Tải **kho tài nguyên** (nhạc nền, cảnh trám, font, mẫu): [LINK KHO TÀI NGUYÊN DRIVE] — giải nén vào thư mục làm việc.

## Phần mềm cần

| Phần mềm | Dùng để | Tự cài bằng `cai_dat.py` |
|---|---|---|
| Python 3.10+ | Chạy script dựng | Không (cài trước: `winget install -e --id Python.Python.3.12`) |
| FFmpeg | Cắt, ghép, xuất video | Có (winget) |
| Node.js | Remotion / HyperFrames dựng đồ họa | Có (winget) |
| Git | Tải kho, cập nhật | Có (winget) |
| yt-dlp | Tải video mẫu bạn được phép dùng | Có (pip) |
| faster-whisper | Nghe lời tiếng Việt, làm phụ đề | Có (pip) |
| edge-tts | Giọng đọc AI miễn phí | Có (pip) |
| Google Chrome + tiện ích Claude in Chrome | Skill KOL và cây cảnh làm ảnh/clip trên Muse (muse.ai) | Không (tự cài, tự đăng nhập) |
| Card NVIDIA (không bắt buộc) | Whisper và xuất video nhanh hơn | — |

## Skill (9)

| Skill | Làm gì |
|---|---|
| `ab-edit` | Edit video quay thô thành video hoàn chỉnh; cắt livestream thành nhiều video ngắn; tạo biến thể hook để chạy quảng cáo |
| `video-ngan-nguoi-noi` | Video ngắn 9:16 người nói + mô hình đồ họa; video giới thiệu bản thân BNI 30 giây (có chế độ không mặt) |
| `video-ngan-hyperframes` | Đường dự phòng dựng lớp hình bằng HyperFrames khi Remotion lỗi |
| `anh-bia-video` | Ảnh bìa dọc 9:16, chữ ghép bằng code nên luôn đúng dấu tiếng Việt |
| `kol-ban-quan-ao` | Video KOL AI bán quần áo giọng livestream, chèn cận chi tiết |
| `kol-lookbook` | Video lookbook nhiều bộ đồ, cắt theo phách nhạc, không lời |
| `kol-mac-thu-mot-khung` | Video KOL mặc thử một sản phẩm, đứng một khung, quay lưng khoe áo |
| `kol-review-nghi-duong` | Video KOL AI review khu nghỉ dưỡng 45–55 giây |
| `video-cay-canh` | Video hàng loạt cho shop cây cảnh, sân vườn kiểu "ảnh thiết kế chuyển động" |

## Agent (23)

| Nhóm | Agent |
|---|---|
| Edit video thô và BNI | `nguoi-dung-video` (dựng), `nguoi-soat-video` (soát độc lập, chấm ĐẠT/SỬA LẠI kèm giây) |
| Kiểm duyệt chung | `kiem-duyet-doc-lap` |
| KOL bán quần áo | `kol-livestream-soat` |
| KOL lookbook | `sku-lb-lenh`, `sku-lb-dung`, `sku-lb-soi-da-mat`, `sku-lb-soi-trang-phuc`, `sku-lb-cham-dung` |
| KOL mặc thử một khung | `soi-mat-trang-diem-kol`, `soi-ao-xoay-lung-kol`, `soi-loi-giong-kol`, `cham-so-mau-kol`, `giam-sat-kol-mot-khung` |
| KOL review nghỉ dưỡng | `nd-soi-mat-kol`, `nd-soi-loi-giong`, `nd-cham-so-mau`, `nd-giam-sat-cuoi` |
| Video cây cảnh | `sku-cc-thiet-ke`, `sku-cc-muse`, `sku-cc-kiem-dung`, `sku-cc-cham-so-mau`, `sku-cc-dang-bai` |

## Lưu ý quan trọng

- **KOL riêng:** kho không kèm ảnh, mặt hay giọng của KOL nào. Tự tạo KOL của bạn theo [HUONG-DAN-TAO-KOL.md](HUONG-DAN-TAO-KOL.md).
- **Video mẫu:** không kèm video mẫu của người khác (bản quyền). Thư mục `video-mau/` trong từng skill chỉ có hướng dẫn; bạn tự đặt video mẫu mình được phép dùng.
- **Cấu hình:** tệp `*.mau.json` là mẫu trống. Chép thành tệp thật (bỏ `.mau`) rồi điền. Tệp cấu hình thật và khóa API **không** đưa lên GitHub (đã chặn trong `.gitignore`).
- **Nhạc mẫu** trong `kol-lookbook/nhac-mau` và `video-cay-canh/nhac-mau` là nhạc công cộng CC0 (nguồn ghi trong `NGUON-NHAC.txt`).
- Video có cảnh hoặc người do AI tạo phải **gắn nhãn nội dung AI** khi đăng.

## Giấy phép

MIT — xem [LICENSE](LICENSE). Mô hình nhận diện mặt YuNet đi kèm theo giấy phép riêng ở `scripts/mo-hinh/LICENSE-yunet.txt`.

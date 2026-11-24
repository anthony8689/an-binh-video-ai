# Bộ làm video AI — An Bình AI

- Luôn trả lời bằng tiếng Việt, lời thường, ngắn gọn. Người dùng không biết code: không dán lệnh dài, giải thích bằng lời.
- Hai câu lệnh chính, cả hai đều thuộc skill `video-ngan-nguoi-noi`:
  1. **Edit video thô** ("Edit video <tên file> cho tôi") → mục "Edit video từ file quay" (lệnh `edit.py`).
  2. **Video giới thiệu bản thân BNI** ("Dựng một video giới thiệu bản thân cho tôi theo cấu trúc BNI") → mục BNI (lệnh `bni.py`).
- Với cả hai: giao agent `video-dung` dựng, rồi gọi agent `video-cham-diem` chấm độc lập. Phiếu SỬA LẠI thì gửi lại `video-dung` sửa, chấm lại (tối đa 3 vòng). Không hỏi duyệt từng bước. Báo người dùng đường dẫn video kèm phiếu chấm cuối.
- Việc nâng cao (cắt livestream thành nhiều clip, làm biến thể quảng cáo, dựng video quảng cáo có duyệt từng bước) → skill `ab-edit`, chấm bằng `video-cham-diem`.
- Máy mới: chạy `python cai_dat.py` ở thư mục kho trước. Agent mới chỉ nhận sau khi đóng hẳn Claude và mở lại.
- Video KOL, lookbook, cây cảnh: dùng đúng skill tên tương ứng và các agent soi/chấm của skill đó.
- Không tự đăng lên mạng xã hội. Không xóa file gốc của người dùng. Không nhập mật khẩu thay người dùng.

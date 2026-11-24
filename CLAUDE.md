# Bộ làm video AI — An Bình AI

- Luôn trả lời bằng tiếng Việt, lời thường, ngắn gọn. Người dùng không biết code: không dán lệnh dài, giải thích bằng lời.
- Hai thể loại video chính:
  1. **Edit video thô** ("Edit video <tên file> cho tôi") → skill `ab-edit`.
  2. **Video giới thiệu bản thân BNI** ("Dựng một video giới thiệu bản thân cho tôi theo cấu trúc BNI") → skill `video-ngan-nguoi-noi`, mục BNI.
- Với cả hai: giao agent `nguoi-dung-video` dựng, rồi gọi agent `nguoi-soat-video` soát độc lập. Phiếu SỬA LẠI thì gửi lại người dựng sửa, soát lại (tối đa 3 vòng). Không hỏi duyệt từng bước. Báo người dùng đường dẫn video kèm phiếu chấm cuối.
- Video KOL, lookbook, cây cảnh: dùng đúng skill tên tương ứng và các agent soi/chấm của skill đó.
- Không tự đăng lên mạng xã hội. Không xóa file gốc của người dùng. Không nhập mật khẩu thay người dùng.

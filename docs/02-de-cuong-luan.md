# Đề cương khóa luận

Đề tài: Ứng dụng RAG kết hợp ontology cho tra cứu Luật Hôn nhân và gia đình.

## Chương 1. Mở đầu

Người dân hỏi bằng lời đời thường, trong khi căn cứ nằm ở Điều, Khoản dùng thuật ngữ khác, có ngoại lệ hoặc được nghị định, thông tư chi tiết hóa. Kho vài trăm khoản nên tìm theo độ tương tự câu dễ trả về điều gần nghĩa nhưng không phải điều điều chỉnh.

Câu hỏi nghiên cứu: ontology miền có làm tăng Recall@5 và MRR so với BM25, vector và RAG lai hay không, nhất là trên câu nhiều điều, câu lệch thuật ngữ và câu nối luật với văn bản hướng dẫn.

Phạm vi: Luật 52/2014/QH13, Nghị định 126/2014/NĐ-CP, Thông tư 02a/2015/TT-BTP. Ngoài phạm vi: hộ tịch trong nước, án lệ, hình sự, thừa kế, thủ tục nuôi con nuôi và giám hộ theo luật khác.

## Chương 2. Cơ sở

RAG: truy hồi rồi sinh câu có ràng buộc nguồn. Ontology pháp lý: khái niệm, quan hệ hẹp hơn, điều kiện, ngoại lệ, dẫn chiếu, quan hệ chi tiết hóa giữa luật và nghị định. Đơn vị văn bản Việt Nam: chương, điều, khoản, điểm. Các hướng liên quan: RAG pháp lý, GraphRAG, LKIF ở mức ý tưởng lớp khái niệm, không triển khai đầy đủ logic deontic.

## Chương 3. Phân tích và ontology miền

Nhóm khái niệm bám chương của luật: kết hôn, quan hệ vợ chồng và tài sản, ly hôn, cha mẹ con, cấp dưỡng, yếu tố nước ngoài. Chuẩn mực điều kiện kết hôn được ghi thành cá thể có điều kiện, ngoại lệ và khoản nguồn. Bảng ánh xạ khoản là phần kiểm tra được của đồ án.

## Chương 4. Cài đặt

Pipeline: làm sạch văn bản, parser, chỉ mục BM25 và vector, mở rộng SPARQL, hòa hạng, API FastAPI, giao diện hỏi đáp và trang duyệt khái niệm. Câu trả lời luôn kèm đoạn khoản gốc. Thông tư hết hiệu lực được gắn cờ.

## Chương 5. Thực nghiệm

Bộ 60 câu. Bốn hệ. Chỉ số Recall@5, MRR, Precision@5, tỷ lệ từ chối đúng. Phân tích theo nhóm. Phiếu chấm người trên 15 câu.

## Chương 6. Kết luận

Ontology có ích khi câu hỏi lệch từ hoặc cần khoản ngoại lệ và văn bản hướng dẫn. Giới hạn: kho nhỏ, ánh xạ mang dấu người làm, parser có thể cắt tiêu đề dài, thông tư đã hết hiệu lực, 60 câu chưa đủ để suy diễn thống kê mạnh. Hướng tiếp: án lệ và hộ tịch trong nước, embedding neural cố định cho thí nghiệm lặp lại.

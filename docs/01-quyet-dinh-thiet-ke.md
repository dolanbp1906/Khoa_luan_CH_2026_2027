# Quyết định thiết kế

## Phạm vi kho

Kho đóng băng ngày 11/10/2026, ghi trong `data/raw/manifest.json`:

- Luật số 52/2014/QH13, hiệu lực 01/01/2015.
- Nghị định 126/2014/NĐ-CP, hiệu lực 15/02/2015.
- Thông tư 02a/2015/TT-BTP, hiệu lực 10/04/2015. CSDL quốc gia về pháp luật ghi nhận thông tư hết hiệu lực toàn bộ từ 02/01/2016. Đồ án vẫn đưa vào kho vì đây là văn bản hướng dẫn trực tiếp của nghị định, và mỗi trích dẫn đều kèm cảnh báo hết hiệu lực.

Nguồn đối chiếu là vbpl.vn và Công báo. Bản tiếng Anh trên trang tổng hợp không được đưa vào kho. Thủ tục hộ tịch trong nước (Nghị định 123/2015/NĐ-CP) và án lệ nằm ngoài kho. Câu hỏi thuộc vùng đó bị từ chối.

Mặt chữ luật giữ bản 2014: cụm “Tòa án nhân dân khu vực” trong văn bản hợp nhất 2025 được trả về “Tòa án nhân dân cấp huyện”. Điều 132 và Điều 133 được ghép từ phần cuối luật vì bản trích PDF dừng ở Điều 131.

## Đơn vị truy hồi

Parser tách Chương / Điều / Khoản / Điểm. Đơn vị đưa vào chỉ mục là khoản. Điều không đánh số khoản dùng khoản 0. Điểm nằm trong văn bản của khoản.

## Ontology

`ontology/family-law.ttl` gồm 60 khái niệm OWL, các lớp LegalConcept, LegalProvision, LegalNorm, Actor. Quan hệ: `narrowerThan`, `regulatedBy`, `detailedBy`, `cites`, `hasCondition`, `hasException`, `hasSource`, `appliesToActor`.

Bảng `ontology/mapping.csv` là ánh xạ đã rà: khái niệm sang khoản, luật sang nghị định/thông tư, một số dẫn chiếu và ngoại lệ. Lúc chạy, hệ thống thêm cạnh `cites` khi khoản viết “quy định tại Điều …”.

Câu hỏi được ánh xạ bằng cụm `skos:altLabel` sau khi bỏ dấu. Chỉ khái niệm khớp mạnh (điểm cụm dài) mới được mở rộng SPARQL, để khái niệm cha như “kết hôn” không kéo cả chương vào một câu hỏi hẹp.

## Truy hồi và sinh câu trả lời

Bốn chế độ: BM25, vector, lai BM25+vector, lai có ontology. Danh sách hạng hòa bằng Reciprocal Rank Fusion, k = 60.

Embedding mặc định là hashing n-gram để thí nghiệm chạy offline. Biến `EMBEDDING_BACKEND=fastembed` và `EMBEDDING_MODEL=intfloat/multilingual-e5-small` bật mô hình neural đa ngữ khi máy đã cài `fastembed`.

Nếu `LLM_API_KEY` trống, câu trả lời là trích nguyên văn khoản đã truy hồi. Nếu có khóa, adapter gọi API tương thích OpenAI và chỉ giữ `provision_id` nằm trong tập đã truy hồi.

## Chỉ số

`eval/gold.json` có 60 câu, năm nhóm: một điều, nhiều điều, luật sang nghị định/thông tư, lời đời thường, ngoài phạm vi.

Trên câu trong kho: Recall@5, MRR, Precision@5. Trên cả bộ: tỷ lệ từ chối đúng. `eval/human_rubric.csv` để người chấm cho điểm 1–5 về bám văn bản, trích dẫn và đủ ý trên 15 câu. Các ô để trống cho đến khi chấm tay.

## Số đo trên bộ 60 câu

Lần chạy với embedding hashing n-gram, ghi ở `eval/results.txt`:

- BM25: Recall@5 0.625, MRR 0.637.
- Vector: Recall@5 0.531, MRR 0.538.
- RAG lai: Recall@5 0.604, MRR 0.628.
- RAG lai có ontology: Recall@5 0.750, MRR 0.765.

Mức tăng nằm ở nhóm nối luật với nghị định/thông tư (0.792 so với 0.625 của BM25) và nhóm lời đời thường (0.625 so với 0.250). Nhóm một điều đã sát trần ở cả bốn hệ. Nhóm nhiều điều, BM25 còn nhỉnh hơn một chút (0.667 so với 0.625) vì mở rộng khái niệm có thể chiếm chỗ của khoản thứ hai. Cả 12 câu ngoài kho đều bị từ chối đúng.

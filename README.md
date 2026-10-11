# Tra cứu Luật Hôn nhân và gia đình bằng RAG và ontology

Hệ thống hỏi đáp trên Luật số 52/2014/QH13, Nghị định 126/2014/NĐ-CP và Thông tư 02a/2015/TT-BTP. Câu trả lời kèm Điều, Khoản. Đây là công cụ tra cứu, không phải tư vấn pháp lý.

## Chạy

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
copy .env.example .env
.\.venv\Scripts\python -m backend.scripts.ingest
.\.venv\Scripts\python -m uvicorn backend.app.main:app --port 8000
```

Giao diện, terminal thứ hai:

```powershell
cd frontend
npm install
npm run dev
```

Mở http://localhost:5173. Để trống `LLM_API_KEY` thì hệ thống trả về trích dẫn khoản đã tìm được. Điền khóa nếu muốn câu trả lời do mô hình ngôn ngữ viết lại, vẫn bị kiểm `provision_id`.

Embedding mặc định là hashing n-gram, chạy không cần tải mô hình. Muốn vector neural: cài `fastembed`, đặt `EMBEDDING_BACKEND=fastembed` rồi chạy lại `ingest`.

## Đánh giá

```powershell
.\.venv\Scripts\python -m pytest backend/tests -q
.\.venv\Scripts\python -m eval.run_eval
```

Kết quả in Recall@5, MRR, Precision@5 và tỷ lệ từ chối đúng của bốn chế độ. Phiếu chấm tay nằm ở `eval/human_rubric.csv`.

Thiết kế và đề cương nằm trong `docs/`.

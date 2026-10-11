from backend.app.corpus.parser import fold_vi, parse_legal_text

SAMPLE = """
Chương I
NHỮNG QUY ĐỊNH CHUNG

Điều 1. Phạm vi điều chỉnh
Luật này quy định chế độ hôn nhân và gia đình.

Điều 5. Bảo vệ chế độ hôn nhân và gia đình
1. Quan hệ hôn nhân và gia đình được tôn trọng.
2. Cấm các hành vi sau đây:
a) Kết hôn giả tạo, ly hôn giả tạo;
b) Tảo hôn, cưỡng ép kết hôn;
3. Mọi hành vi vi phạm phải được xử lý.

Chương II
KẾT HÔN

Điều 8. Điều kiện kết hôn
1. Nam, nữ kết hôn với nhau phải tuân theo các điều kiện sau đây:
a) Nam từ đủ 20 tuổi trở lên, nữ từ đủ 18 tuổi trở lên;
b) Việc kết hôn do nam và nữ tự nguyện quyết định;
2. Nhà nước không thừa nhận hôn nhân giữa những người cùng giới tính.
"""


def test_parse_chapters_articles_clauses_points():
    parsed = parse_legal_text(SAMPLE)
    assert [chapter.label for chapter in parsed.chapters] == ["I", "II"]
    assert parsed.chapters[0].title.upper().startswith("NHỮNG QUY ĐỊNH")
    article5 = parsed.chapters[0].articles[1]
    assert article5.article_no == 5
    assert article5.title.startswith("Bảo vệ")
    numbers = [clause.clause_no for clause in article5.clauses]
    assert numbers == [1, 2, 3]
    assert [point.label for point in article5.clauses[1].points] == ["a", "b"]
    article8 = parsed.chapters[1].articles[0]
    assert article8.clauses[0].clause_no == 1
    assert "20 tuổi" in article8.clauses[0].full_text
    assert article8.clauses[1].clause_no == 2


def test_fold_vi():
    assert fold_vi("Ly hôn") == "Ly hon"
    assert "tuoi" in fold_vi("tuổi").lower() or fold_vi("tuổi") == "tuoi"

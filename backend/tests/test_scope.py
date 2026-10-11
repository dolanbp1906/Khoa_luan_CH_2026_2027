from backend.app.generation.service import out_of_scope_reason, select_hits
from backend.app.retrieval.service import Hit
from backend.app.retrieval.text import content_tokens


def test_out_of_scope_cases():
    assert out_of_scope_reason("Án lệ nào về nuôi con?")
    assert out_of_scope_reason("Thời hạn Tòa án giải quyết ly hôn là bao lâu?")
    assert out_of_scope_reason("Thủ tục kết hôn tại UBND xã trong nước cần giấy tờ gì?")
    assert out_of_scope_reason("Chia di sản thừa kế khi bố mất?") is not None


def test_in_scope_not_flagged():
    assert out_of_scope_reason("Nam bao nhiêu tuổi thì được kết hôn?") is None
    assert out_of_scope_reason("Thời hạn giải quyết hồ sơ đăng ký kết hôn với người nước ngoài?") is None


def _hit(provision_id: str, title: str, text: str) -> Hit:
    return Hit(
        provision_id, 0.02, text, f"Khoản {provision_id}", "52-2014-QH13", "52/2014/QH13",
        "Luật", 11, title, 4, True, None, "https://example.test",
    )


def test_toi_is_not_toi_cao():
    assert content_tokens("tôi") != content_tokens("tối")
    assert content_tokens("tài") != content_tokens("tại")
    noise = _hit("52-2014-QH13:d11:k4", "Xử lý việc kết hôn trái pháp luật", "Tòa án nhân dân tối cao chủ trì phối hợp hướng dẫn Điều này.")
    assert select_hits("Tôi là ai", [noise], []) == []


def test_selects_concept_provision_over_neighbor():
    right = _hit("52-2014-QH13:d59:k1", "Chia tài sản khi ly hôn", "Tài sản chung của vợ chồng được chia khi ly hôn theo thỏa thuận.")
    side = _hit("52-2014-QH13:d40:k1", "Chia tài sản trong thời kỳ hôn nhân", "Trong thời kỳ hôn nhân vợ chồng có quyền chia tài sản chung.")
    concepts = [{"id": "ChiaTaiSanKhiLyHon", "label": "Chia tài sản khi ly hôn", "provisions": [right.provision_id]}]
    chosen = select_hits("Ly hôn thì phân chia tài sản ra sao?", [side, right], concepts)
    assert [hit.provision_id for hit in chosen] == [right.provision_id]

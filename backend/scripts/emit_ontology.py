"""Sinh ontology/family-law.ttl và ontology/mapping.csv từ danh sách khái niệm."""

from __future__ import annotations

from backend.app.config import MAPPING_PATH, ONTOLOGY_PATH

# id, nhãn, cụm đời thường, khái niệm rộng hơn
CONCEPTS: list[tuple[str, str, list[str], str | None]] = [
    ("KetHon", "Kết hôn", ["kết hôn", "cuoi nhau", "lấy vợ", "lấy chồng"], None),
    ("DoTuoiKetHon", "Độ tuổi kết hôn", ["tuổi kết hôn", "bao nhiêu tuổi thì được kết hôn", "bao nhiêu tuổi thì được cưới", "đủ tuổi kết hôn", "tảo hôn"], "KetHon"),
    ("TuNguyenKetHon", "Tự nguyện kết hôn", ["tự nguyện kết hôn", "bị ép lấy chồng", "bị ép lấy vợ", "không tự nguyện"], "KetHon"),
    ("NangLucHanhViDanSu", "Năng lực hành vi dân sự khi kết hôn", ["mất năng lực hành vi dân sự", "không đủ năng lực hành vi"], "KetHon"),
    ("CamKetHon", "Cấm kết hôn", ["cấm kết hôn", "không được kết hôn", "trường hợp cấm"], "KetHon"),
    ("TaoHon", "Tảo hôn", ["tảo hôn", "lấy vợ khi chưa đủ tuổi", "cưới non"], "CamKetHon"),
    ("CuongEpKetHon", "Cưỡng ép kết hôn", ["cưỡng ép kết hôn", "ép kết hôn", "bắt cưới"], "CamKetHon"),
    ("LuaDoiKetHon", "Lừa dối kết hôn", ["lừa dối kết hôn", "lừa cưới"], "CamKetHon"),
    ("CanTroKetHon", "Cản trở kết hôn", ["cản trở kết hôn", "ngăn cản kết hôn"], "CamKetHon"),
    ("KetHonGiaTao", "Kết hôn giả tạo", ["kết hôn giả", "kết hôn giả tạo", "cưới giả"], "CamKetHon"),
    ("YeuSachCuaCai", "Yêu sách của cải trong kết hôn", ["thách cưới", "yêu sách của cải", "đòi của hồi môn"], "CamKetHon"),
    ("KetHonTraiPhapLuat", "Kết hôn trái pháp luật", ["kết hôn trái pháp luật", "kết hôn không đúng điều kiện"], "KetHon"),
    ("HuyKetHonTraiPhapLuat", "Hủy kết hôn trái pháp luật", ["hủy kết hôn", "xin hủy việc kết hôn"], "KetHonTraiPhapLuat"),
    ("DangKyKetHon", "Đăng ký kết hôn", ["đăng ký kết hôn", "giấy chứng nhận kết hôn", "chưa đăng ký kết hôn"], "KetHon"),
    ("HonNhanCungGioiTinh", "Hôn nhân cùng giới tính", ["kết hôn đồng giới", "cùng giới tính", "hai người nam kết hôn", "hai người nữ kết hôn"], "KetHon"),
    ("ChungSongNhuVoChong", "Chung sống như vợ chồng", ["chung sống như vợ chồng", "sống chung không đăng ký", "không có đăng ký kết hôn"], "KetHon"),
    ("ThoiKyHonNhan", "Thời kỳ hôn nhân", ["thời kỳ hôn nhân", "trong thời kỳ hôn nhân"], None),
    ("QuyenNghiaVuVoChong", "Quyền và nghĩa vụ của vợ chồng", ["quyền nghĩa vụ vợ chồng", "bình đẳng vợ chồng", "tình nghĩa vợ chồng"], None),
    ("DaiDienVoChong", "Đại diện giữa vợ và chồng", ["đại diện vợ chồng", "vợ đứng tên sổ đỏ", "chỉ ghi tên một người"], "QuyenNghiaVuVoChong"),
    ("TaiSanChung", "Tài sản chung của vợ chồng", ["tài sản chung", "nhà chung", "tiền lương vợ chồng"], "CheDoTaiSanLuatDinh"),
    ("TaiSanRieng", "Tài sản riêng của vợ chồng", ["tài sản riêng", "của hồi môn", "tài sản trước khi kết hôn"], "CheDoTaiSanLuatDinh"),
    ("CheDoTaiSanLuatDinh", "Chế độ tài sản theo luật định", ["chế độ tài sản luật định", "không có thỏa thuận tài sản"], "QuyenNghiaVuVoChong"),
    ("CheDoTaiSanThoaThuan", "Chế độ tài sản theo thỏa thuận", ["thỏa thuận tài sản", "hôn ước", "chế độ tài sản thỏa thuận"], "QuyenNghiaVuVoChong"),
    ("ChiaTaiSanTrongHonNhan", "Chia tài sản chung trong thời kỳ hôn nhân", ["chia tài sản khi còn đang kết hôn", "chia tài sản trong thời kỳ hôn nhân"], "TaiSanChung"),
    ("LyHon", "Ly hôn", ["ly hôn", "chia tay", "chấm dứt hôn nhân"], None),
    ("LyHonThuanTinh", "Thuận tình ly hôn", ["thuận tình ly hôn", "hai bên đồng ý ly hôn", "ly hôn đồng thuận"], "LyHon"),
    ("LyHonTheoYeuCauMotBen", "Ly hôn theo yêu cầu một bên", ["đơn phương ly hôn", "ly hôn một phía", "ly hôn một mình", "không chịu ký đơn", "vợ không đồng ý ly hôn", "chồng không ký đơn"], "LyHon"),
    ("HoaGiaiLyHon", "Hòa giải khi ly hôn", ["hòa giải ly hôn", "hòa giải ở tòa", "hòa giải ở cơ sở"], "LyHon"),
    ("ChiaTaiSanKhiLyHon", "Chia tài sản khi ly hôn", ["chia tài sản khi ly hôn", "chia nhà khi ly hôn", "chia nhà, chia đất", "chia đất khi ly hôn", "chia sổ đỏ"], "LyHon"),
    ("NuoiConSauLyHon", "Nuôi con sau ly hôn", ["quyền nuôi con", "giành con", "ai được nuôi con", "theo bố hay theo mẹ", "thăm nom con sau ly hôn"], "LyHon"),
    ("CapDuongSauLyHon", "Cấp dưỡng sau ly hôn", ["cấp dưỡng sau ly hôn", "tiền nuôi con sau ly hôn", "cấp dưỡng cho vợ khi ly hôn"], "CapDuong"),
    ("XacDinhChaMeCon", "Xác định cha, mẹ, con", ["xác định cha", "xác định mẹ", "xác định con", "nhận cha cho con"], None),
    ("NhanChaMeCon", "Nhận cha, mẹ, con", ["nhận cha mẹ con", "làm giấy nhận con", "nhận cha"], "XacDinhChaMeCon"),
    ("NghiaVuChaMe", "Nghĩa vụ của cha mẹ", ["nghĩa vụ cha mẹ", "chăm sóc nuôi dưỡng con", "giáo dục con"], None),
    ("QuyenCuaCon", "Quyền của con", ["quyền của con", "tài sản riêng của con"], None),
    ("GiamHo", "Giám hộ trong quan hệ gia đình", ["người giám hộ", "giám hộ"], None),
    ("NhanConNuoi", "Nuôi con nuôi", ["con nuôi", "cha nuôi", "mẹ nuôi"], None),
    ("MangThaiHoNhanDao", "Mang thai hộ vì mục đích nhân đạo", ["mang thai hộ nhân đạo", "mang thai hộ"], None),
    ("MangThaiHoThuongMai", "Mang thai hộ vì mục đích thương mại", ["mang thai hộ thương mại", "mang thai hộ lấy tiền"], "CamKetHon"),
    ("HoTroSinhSan", "Sinh con bằng kỹ thuật hỗ trợ sinh sản", ["thụ tinh trong ống nghiệm", "hỗ trợ sinh sản"], None),
    ("CapDuong", "Cấp dưỡng", ["cấp dưỡng", "chu cấp", "tiền nuôi"], None),
    ("MucCapDuong", "Mức cấp dưỡng", ["mức cấp dưỡng", "cấp dưỡng bao nhiêu", "mỗi tháng phải đưa bao nhiêu"], "CapDuong"),
    ("PhuongThucCapDuong", "Phương thức cấp dưỡng", ["đóng cấp dưỡng hàng tháng", "cấp dưỡng một lần"], "CapDuong"),
    ("ChamDutCapDuong", "Chấm dứt cấp dưỡng", ["khi nào hết cấp dưỡng", "chấm dứt cấp dưỡng", "không phải cấp dưỡng nữa"], "CapDuong"),
    ("NguoiYeuCauCapDuong", "Người có quyền yêu cầu cấp dưỡng", ["ai được yêu cầu cấp dưỡng", "trốn tránh cấp dưỡng"], "CapDuong"),
    ("TapQuan", "Tập quán về hôn nhân và gia đình", ["tập quán", "phong tục kết hôn"], None),
    ("TapQuanLacHau", "Tập quán lạc hậu", ["tập quán lạc hậu", "hủ tục"], "TapQuan"),
    ("YeuToNuocNgoai", "Yếu tố nước ngoài", ["yếu tố nước ngoài", "người nước ngoài", "có quốc tịch nước ngoài"], None),
    ("KetHonYeuToNuocNgoai", "Kết hôn có yếu tố nước ngoài", ["kết hôn với người nước ngoài", "cưới chồng nước ngoài", "cưới vợ nước ngoài"], "YeuToNuocNgoai"),
    ("LyHonYeuToNuocNgoai", "Ly hôn có yếu tố nước ngoài", ["ly hôn với người nước ngoài", "ly hôn ở nước ngoài"], "YeuToNuocNgoai"),
    ("XacDinhChaMeConYeuToNuocNgoai", "Xác định cha mẹ con có yếu tố nước ngoài", ["nhận con có yếu tố nước ngoài", "cha người nước ngoài"], "YeuToNuocNgoai"),
    ("CapDuongYeuToNuocNgoai", "Cấp dưỡng có yếu tố nước ngoài", ["cấp dưỡng người nước ngoài", "cấp dưỡng ở nước ngoài"], "YeuToNuocNgoai"),
    ("HopPhapHoaLanhSu", "Hợp pháp hóa lãnh sự", ["hợp pháp hóa lãnh sự", "giấy tờ nước ngoài"], "YeuToNuocNgoai"),
    ("CongNhanBanAnNuocNgoai", "Công nhận bản án nước ngoài", ["công nhận ly hôn nước ngoài", "bản án nước ngoài"], "YeuToNuocNgoai"),
    ("GiayXacNhanTinhTrangHonNhan", "Giấy xác nhận tình trạng hôn nhân", ["giấy xác nhận tình trạng hôn nhân", "giấy độc thân", "xác nhận chưa kết hôn"], "KetHonYeuToNuocNgoai"),
    ("GhiChuKetHonNuocNgoai", "Ghi vào sổ việc kết hôn ở nước ngoài", ["ghi chú kết hôn", "kết hôn ở nước ngoài rồi về việt nam", "ghi vào sổ việc kết hôn"], "KetHonYeuToNuocNgoai"),
    ("TrungTamTuVanHonNhan", "Trung tâm tư vấn hôn nhân có yếu tố nước ngoài", ["trung tâm tư vấn hôn nhân", "tư vấn kết hôn người nước ngoài"], "YeuToNuocNgoai"),
    ("ApDungPhapLuatNuocNgoai", "Áp dụng pháp luật nước ngoài", ["áp dụng pháp luật nước ngoài", "luật nước nào"], "YeuToNuocNgoai"),
    ("BaoLucGiaDinh", "Bạo lực gia đình", ["bạo lực gia đình", "bị chồng đánh", "bị vợ bạo hành"], "CamKetHon"),
    ("ThanhVienGiaDinh", "Thành viên gia đình", ["thành viên gia đình", "ai là người thân"], None),
]

ACTORS = [
    ("ActorVoChong", "Vợ, chồng"),
    ("ActorChaMe", "Cha, mẹ"),
    ("ActorCon", "Con"),
    ("ActorOngBa", "Ông bà"),
    ("ActorNguoiNuocNgoai", "Người nước ngoài"),
    ("ActorNguoiGiamHo", "Người giám hộ"),
]

# subject, predicate, object, note
MAPPING: list[tuple[str, str, str, str]] = [
    ("DoTuoiKetHon", "regulatedBy", "52-2014-QH13:d8:k1", "điểm a khoản 1 Điều 8"),
    ("DoTuoiKetHon", "regulatedBy", "52-2014-QH13:d3:k8", "định nghĩa tảo hôn"),
    ("TuNguyenKetHon", "regulatedBy", "52-2014-QH13:d8:k1", "điểm b khoản 1 Điều 8"),
    ("TuNguyenKetHon", "regulatedBy", "52-2014-QH13:d3:k9", "cưỡng ép kết hôn"),
    ("NangLucHanhViDanSu", "regulatedBy", "52-2014-QH13:d8:k1", "điểm c khoản 1 Điều 8"),
    ("CamKetHon", "regulatedBy", "52-2014-QH13:d5:k2", "các hành vi bị cấm"),
    ("CamKetHon", "regulatedBy", "52-2014-QH13:d8:k1", "điểm d dẫn chiếu Điều 5"),
    ("TaoHon", "regulatedBy", "52-2014-QH13:d3:k8", ""),
    ("TaoHon", "regulatedBy", "52-2014-QH13:d5:k2", ""),
    ("CuongEpKetHon", "regulatedBy", "52-2014-QH13:d3:k9", ""),
    ("CuongEpKetHon", "regulatedBy", "52-2014-QH13:d5:k2", ""),
    ("LuaDoiKetHon", "regulatedBy", "52-2014-QH13:d5:k2", ""),
    ("CanTroKetHon", "regulatedBy", "52-2014-QH13:d3:k10", ""),
    ("KetHonGiaTao", "regulatedBy", "52-2014-QH13:d3:k11", ""),
    ("KetHonGiaTao", "regulatedBy", "52-2014-QH13:d5:k2", ""),
    ("YeuSachCuaCai", "regulatedBy", "52-2014-QH13:d3:k12", ""),
    ("YeuSachCuaCai", "regulatedBy", "52-2014-QH13:d5:k2", ""),
    ("KetHonTraiPhapLuat", "regulatedBy", "52-2014-QH13:d3:k6", ""),
    ("KetHonTraiPhapLuat", "regulatedBy", "52-2014-QH13:d11:k1", ""),
    ("HuyKetHonTraiPhapLuat", "regulatedBy", "52-2014-QH13:d10:k1", ""),
    ("HuyKetHonTraiPhapLuat", "regulatedBy", "52-2014-QH13:d12:k1", ""),
    ("DangKyKetHon", "regulatedBy", "52-2014-QH13:d9:k1", ""),
    ("DangKyKetHon", "regulatedBy", "52-2014-QH13:d9:k2", "kết hôn lại sau ly hôn"),
    ("HonNhanCungGioiTinh", "regulatedBy", "52-2014-QH13:d8:k2", ""),
    ("ChungSongNhuVoChong", "regulatedBy", "52-2014-QH13:d3:k7", ""),
    ("ChungSongNhuVoChong", "regulatedBy", "52-2014-QH13:d14:k1", ""),
    ("ChungSongNhuVoChong", "regulatedBy", "52-2014-QH13:d16:k1", ""),
    ("ThoiKyHonNhan", "regulatedBy", "52-2014-QH13:d3:k13", ""),
    ("QuyenNghiaVuVoChong", "regulatedBy", "52-2014-QH13:d17:k0", ""),
    ("QuyenNghiaVuVoChong", "regulatedBy", "52-2014-QH13:d19:k1", ""),
    ("DaiDienVoChong", "regulatedBy", "52-2014-QH13:d24:k1", ""),
    ("DaiDienVoChong", "regulatedBy", "52-2014-QH13:d26:k1", ""),
    ("TaiSanChung", "regulatedBy", "52-2014-QH13:d33:k1", ""),
    ("TaiSanChung", "regulatedBy", "52-2014-QH13:d35:k1", ""),
    ("TaiSanRieng", "regulatedBy", "52-2014-QH13:d43:k1", ""),
    ("CheDoTaiSanLuatDinh", "regulatedBy", "52-2014-QH13:d28:k1", ""),
    ("CheDoTaiSanLuatDinh", "regulatedBy", "126-2014-ND-CP:d7:k0", "nghị định chi tiết"),
    ("CheDoTaiSanThoaThuan", "regulatedBy", "52-2014-QH13:d47:k0", ""),
    ("CheDoTaiSanThoaThuan", "regulatedBy", "52-2014-QH13:d48:k1", ""),
    ("CheDoTaiSanThoaThuan", "regulatedBy", "126-2014-ND-CP:d15:k1", ""),
    ("ChiaTaiSanTrongHonNhan", "regulatedBy", "52-2014-QH13:d38:k1", ""),
    ("LyHon", "regulatedBy", "52-2014-QH13:d3:k14", ""),
    ("LyHon", "regulatedBy", "52-2014-QH13:d51:k1", ""),
    ("LyHonThuanTinh", "regulatedBy", "52-2014-QH13:d55:k0", ""),
    ("LyHonTheoYeuCauMotBen", "regulatedBy", "52-2014-QH13:d56:k1", ""),
    ("HoaGiaiLyHon", "regulatedBy", "52-2014-QH13:d52:k0", ""),
    ("HoaGiaiLyHon", "regulatedBy", "52-2014-QH13:d54:k0", ""),
    ("ChiaTaiSanKhiLyHon", "regulatedBy", "52-2014-QH13:d59:k1", ""),
    ("ChiaTaiSanKhiLyHon", "regulatedBy", "52-2014-QH13:d62:k1", ""),
    ("ChiaTaiSanKhiLyHon", "regulatedBy", "52-2014-QH13:d61:k1", ""),
    ("NuoiConSauLyHon", "regulatedBy", "52-2014-QH13:d81:k1", ""),
    ("NuoiConSauLyHon", "regulatedBy", "52-2014-QH13:d81:k2", "người trực tiếp nuôi con"),
    ("NuoiConSauLyHon", "regulatedBy", "52-2014-QH13:d81:k3", "con dưới 36 tháng"),
    ("NuoiConSauLyHon", "regulatedBy", "52-2014-QH13:d82:k1", ""),
    ("NuoiConSauLyHon", "regulatedBy", "52-2014-QH13:d84:k1", ""),
    ("CapDuongSauLyHon", "regulatedBy", "52-2014-QH13:d115:k0", ""),
    ("CapDuongSauLyHon", "regulatedBy", "52-2014-QH13:d82:k2", "cấp dưỡng nuôi con"),
    ("XacDinhChaMeCon", "regulatedBy", "52-2014-QH13:d88:k1", ""),
    ("XacDinhChaMeCon", "regulatedBy", "52-2014-QH13:d89:k1", ""),
    ("NhanChaMeCon", "regulatedBy", "52-2014-QH13:d90:k1", ""),
    ("NhanChaMeCon", "regulatedBy", "52-2014-QH13:d91:k1", ""),
    ("NhanChaMeCon", "regulatedBy", "126-2014-ND-CP:d30:k1", ""),
    ("NghiaVuChaMe", "regulatedBy", "52-2014-QH13:d69:k1", ""),
    ("NghiaVuChaMe", "regulatedBy", "52-2014-QH13:d71:k1", ""),
    ("QuyenCuaCon", "regulatedBy", "52-2014-QH13:d70:k1", ""),
    ("QuyenCuaCon", "regulatedBy", "52-2014-QH13:d75:k1", ""),
    ("GiamHo", "regulatedBy", "52-2014-QH13:d73:k1", "đại diện cho con, nhắc người giám hộ"),
    ("GiamHo", "regulatedBy", "52-2014-QH13:d10:k2", "người giám hộ được yêu cầu hủy kết hôn trái pháp luật"),
    ("NhanConNuoi", "regulatedBy", "52-2014-QH13:d78:k1", "quan hệ cha nuôi mẹ nuôi; thủ tục nuôi con nuôi thuộc luật khác"),
    ("MangThaiHoNhanDao", "regulatedBy", "52-2014-QH13:d95:k1", ""),
    ("MangThaiHoNhanDao", "regulatedBy", "52-2014-QH13:d94:k0", ""),
    ("MangThaiHoThuongMai", "regulatedBy", "52-2014-QH13:d3:k23", ""),
    ("MangThaiHoThuongMai", "regulatedBy", "52-2014-QH13:d5:k2", ""),
    ("HoTroSinhSan", "regulatedBy", "52-2014-QH13:d93:k1", ""),
    ("HoTroSinhSan", "regulatedBy", "52-2014-QH13:d3:k21", ""),
    ("CapDuong", "regulatedBy", "52-2014-QH13:d107:k1", ""),
    ("CapDuong", "regulatedBy", "52-2014-QH13:d110:k0", ""),
    ("CapDuong", "regulatedBy", "52-2014-QH13:d3:k24", ""),
    ("MucCapDuong", "regulatedBy", "52-2014-QH13:d116:k1", ""),
    ("PhuongThucCapDuong", "regulatedBy", "52-2014-QH13:d117:k0", ""),
    ("ChamDutCapDuong", "regulatedBy", "52-2014-QH13:d118:k1", ""),
    ("NguoiYeuCauCapDuong", "regulatedBy", "52-2014-QH13:d119:k1", ""),
    ("TapQuan", "regulatedBy", "52-2014-QH13:d7:k1", ""),
    ("TapQuan", "regulatedBy", "52-2014-QH13:d3:k4", ""),
    ("TapQuanLacHau", "regulatedBy", "126-2014-ND-CP:d5:k2", ""),
    ("YeuToNuocNgoai", "regulatedBy", "52-2014-QH13:d3:k25", ""),
    ("YeuToNuocNgoai", "regulatedBy", "52-2014-QH13:d121:k1", ""),
    ("KetHonYeuToNuocNgoai", "regulatedBy", "52-2014-QH13:d126:k1", ""),
    ("KetHonYeuToNuocNgoai", "regulatedBy", "126-2014-ND-CP:d19:k1", ""),
    ("KetHonYeuToNuocNgoai", "regulatedBy", "02a-2015-TT-BTP:d6:k1", ""),
    ("LyHonYeuToNuocNgoai", "regulatedBy", "52-2014-QH13:d127:k1", ""),
    ("LyHonYeuToNuocNgoai", "regulatedBy", "126-2014-ND-CP:d41:k0", ""),
    ("XacDinhChaMeConYeuToNuocNgoai", "regulatedBy", "52-2014-QH13:d128:k1", ""),
    ("XacDinhChaMeConYeuToNuocNgoai", "regulatedBy", "126-2014-ND-CP:d30:k1", ""),
    ("CapDuongYeuToNuocNgoai", "regulatedBy", "52-2014-QH13:d129:k1", ""),
    ("HopPhapHoaLanhSu", "regulatedBy", "52-2014-QH13:d124:k0", ""),
    ("CongNhanBanAnNuocNgoai", "regulatedBy", "52-2014-QH13:d125:k1", ""),
    ("GiayXacNhanTinhTrangHonNhan", "regulatedBy", "126-2014-ND-CP:d27:k0", ""),
    ("GiayXacNhanTinhTrangHonNhan", "regulatedBy", "126-2014-ND-CP:d28:k1", ""),
    ("GiayXacNhanTinhTrangHonNhan", "regulatedBy", "02a-2015-TT-BTP:d9:k1", ""),
    ("GhiChuKetHonNuocNgoai", "regulatedBy", "126-2014-ND-CP:d38:k1", ""),
    ("GhiChuKetHonNuocNgoai", "regulatedBy", "02a-2015-TT-BTP:d10:k1", ""),
    ("TrungTamTuVanHonNhan", "regulatedBy", "126-2014-ND-CP:d51:k0", ""),
    ("TrungTamTuVanHonNhan", "regulatedBy", "126-2014-ND-CP:d53:k1", ""),
    ("TrungTamTuVanHonNhan", "regulatedBy", "02a-2015-TT-BTP:d14:k1", ""),
    ("ApDungPhapLuatNuocNgoai", "regulatedBy", "52-2014-QH13:d122:k1", ""),
    ("BaoLucGiaDinh", "regulatedBy", "52-2014-QH13:d5:k2", "điểm h khoản 2 Điều 5"),
    ("ThanhVienGiaDinh", "regulatedBy", "52-2014-QH13:d3:k16", ""),
    ("52-2014-QH13:d7:k1", "detailedBy", "126-2014-ND-CP:d2:k1", "tập quán"),
    ("52-2014-QH13:d7:k1", "detailedBy", "126-2014-ND-CP:d3:k1", ""),
    ("52-2014-QH13:d7:k2", "detailedBy", "126-2014-ND-CP:d4:k1", ""),
    ("52-2014-QH13:d5:k2", "detailedBy", "126-2014-ND-CP:d5:k2", "tập quán lạc hậu"),
    ("52-2014-QH13:d28:k1", "detailedBy", "126-2014-ND-CP:d7:k0", "chế độ tài sản luật định"),
    ("52-2014-QH13:d33:k1", "detailedBy", "126-2014-ND-CP:d9:k1", "thu nhập hợp pháp"),
    ("52-2014-QH13:d43:k1", "detailedBy", "126-2014-ND-CP:d11:k1", "tài sản riêng khác"),
    ("52-2014-QH13:d32:k1", "detailedBy", "126-2014-ND-CP:d8:k1", "người thứ ba"),
    ("52-2014-QH13:d47:k0", "detailedBy", "126-2014-ND-CP:d15:k1", "thỏa thuận tài sản"),
    ("52-2014-QH13:d121:k4", "detailedBy", "126-2014-ND-CP:d1:k0", "chính phủ quy định chi tiết yếu tố nước ngoài"),
    ("52-2014-QH13:d126:k1", "detailedBy", "126-2014-ND-CP:d20:k1", "hồ sơ kết hôn yếu tố nước ngoài"),
    ("126-2014-ND-CP:d20:k1", "detailedBy", "02a-2015-TT-BTP:d6:k1", ""),
    ("126-2014-ND-CP:d24:k1", "detailedBy", "02a-2015-TT-BTP:d8:k1", "lễ đăng ký"),
    ("126-2014-ND-CP:d28:k2", "detailedBy", "02a-2015-TT-BTP:d9:k1", "giấy xác nhận"),
    ("126-2014-ND-CP:d34:k1", "detailedBy", "02a-2015-TT-BTP:d12:k1", "nhận cha mẹ con"),
    ("126-2014-ND-CP:d38:k1", "detailedBy", "02a-2015-TT-BTP:d10:k1", "ghi sổ kết hôn"),
    ("126-2014-ND-CP:d42:k1", "detailedBy", "02a-2015-TT-BTP:d11:k1", "ghi sổ ly hôn"),
    ("126-2014-ND-CP:d53:k1", "detailedBy", "02a-2015-TT-BTP:d14:k1", "trung tâm"),
    ("52-2014-QH13:d8:k1", "cites", "52-2014-QH13:d5:k2", "điểm d khoản 1 Điều 8"),
    ("52-2014-QH13:d8:k1", "hasException", "52-2014-QH13:d5:k2", "điều kiện loại trừ bởi các trường hợp cấm"),
    ("NormDieuKienKetHon", "hasCondition", "DoTuoiKetHon", ""),
    ("NormDieuKienKetHon", "hasCondition", "TuNguyenKetHon", ""),
    ("NormDieuKienKetHon", "hasCondition", "NangLucHanhViDanSu", ""),
    ("NormDieuKienKetHon", "hasException", "CamKetHon", ""),
    ("NormDieuKienKetHon", "hasSource", "52-2014-QH13:d8:k1", ""),
    ("NormChiaTaiSanLyHon", "hasCondition", "ChiaTaiSanKhiLyHon", ""),
    ("NormChiaTaiSanLyHon", "hasSource", "52-2014-QH13:d59:k1", ""),
    ("NormNuoiCon", "hasSource", "52-2014-QH13:d81:k1", ""),
    ("NormNuoiCon", "hasCondition", "NuoiConSauLyHon", ""),
    ("DoTuoiKetHon", "appliesToActor", "ActorVoChong", ""),
    ("NuoiConSauLyHon", "appliesToActor", "ActorChaMe", ""),
    ("NuoiConSauLyHon", "appliesToActor", "ActorCon", ""),
    ("CapDuong", "appliesToActor", "ActorChaMe", ""),
    ("CapDuong", "appliesToActor", "ActorCon", ""),
    ("KetHonYeuToNuocNgoai", "appliesToActor", "ActorNguoiNuocNgoai", ""),
    ("GiamHo", "appliesToActor", "ActorNguoiGiamHo", ""),
]


def _esc(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def build_ttl() -> str:
    lines = [
        "@prefix fl: <http://kltn.local/family-law#> .",
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .",
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
        "@prefix skos: <http://www.w3.org/2004/02/skos/core#> .",
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",
        "",
        "fl: a owl:Ontology ;",
        '  rdfs:label "Ontology hôn nhân và gia đình Việt Nam"@vi .',
        "",
        "fl:LegalConcept a owl:Class .",
        "fl:LegalProvision a owl:Class .",
        "fl:LegalNorm a owl:Class .",
        "fl:Actor a owl:Class .",
        "fl:regulatedBy a owl:ObjectProperty ; rdfs:domain fl:LegalConcept ; rdfs:range fl:LegalProvision .",
        "fl:detailedBy a owl:ObjectProperty ; rdfs:domain fl:LegalProvision ; rdfs:range fl:LegalProvision .",
        "fl:cites a owl:ObjectProperty ; rdfs:domain fl:LegalProvision ; rdfs:range fl:LegalProvision .",
        "fl:hasException a owl:ObjectProperty .",
        "fl:hasCondition a owl:ObjectProperty ; rdfs:domain fl:LegalNorm ; rdfs:range fl:LegalConcept .",
        "fl:hasSource a owl:ObjectProperty ; rdfs:domain fl:LegalNorm ; rdfs:range fl:LegalProvision .",
        "fl:appliesToActor a owl:ObjectProperty ; rdfs:domain fl:LegalConcept ; rdfs:range fl:Actor .",
        "fl:narrowerThan a owl:ObjectProperty ; rdfs:domain fl:LegalConcept ; rdfs:range fl:LegalConcept .",
        "fl:provisionId a owl:DatatypeProperty ; rdfs:range xsd:string .",
        "",
    ]
    for actor_id, label in ACTORS:
        lines.append(f"fl:{actor_id} a fl:Actor ; rdfs:label \"{_esc(label)}\"@vi .")
    lines.append("")
    lines.append(
        "fl:NormDieuKienKetHon a fl:LegalNorm ; rdfs:label \"Chuẩn mực điều kiện kết hôn\"@vi ."
    )
    lines.append(
        "fl:NormChiaTaiSanLyHon a fl:LegalNorm ; rdfs:label \"Chuẩn mực chia tài sản khi ly hôn\"@vi ."
    )
    lines.append("fl:NormNuoiCon a fl:LegalNorm ; rdfs:label \"Chuẩn mực nuôi con sau ly hôn\"@vi .")
    lines.append("")
    for concept_id, label, alts, _parent in CONCEPTS:
        parts = [f"fl:{concept_id} a fl:LegalConcept", f'  rdfs:label "{_esc(label)}"@vi']
        for alt in alts:
            parts.append(f'  skos:altLabel "{_esc(alt)}"@vi')
        lines.append(" ;\n".join(parts) + " .")
        lines.append("")
    return "\n".join(lines)


def build_csv() -> str:
    rows = ["subject,predicate,object,note"]
    for concept_id, _label, _alts, parent in CONCEPTS:
        if parent:
            rows.append(f"{concept_id},narrowerThan,{parent},")
    for subject, predicate, obj, note in MAPPING:
        note_cell = '"' + note.replace('"', '""') + '"' if note else ""
        rows.append(f"{subject},{predicate},{obj},{note_cell}")
    return "\n".join(rows) + "\n"


def main() -> None:
    ONTOLOGY_PATH.parent.mkdir(parents=True, exist_ok=True)
    ONTOLOGY_PATH.write_text(build_ttl(), encoding="utf-8")
    MAPPING_PATH.write_text(build_csv(), encoding="utf-8")
    print(f"concepts={len(CONCEPTS)} triples_rows={len(MAPPING)} -> {ONTOLOGY_PATH.name}")


if __name__ == "__main__":
    main()

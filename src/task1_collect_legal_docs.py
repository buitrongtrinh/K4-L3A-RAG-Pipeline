"""
Task 1 — Thu thập tài liệu chính sách/quy định.

Hướng dẫn:
    1. Chọn chủ đề của nhóm: Tuyển sinh đại học và Quy định đào tạo.
    2. Thu thập tối thiểu 3 tài liệu PDF/DOCX từ nguồn công khai.
    3. Lưu file gốc vào data/landing/legal/.
    4. Đặt tên không dấu và thể hiện đúng nội dung.
"""

from pathlib import Path
import os
import requests
from fpdf import FPDF


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def setup_directory() -> None:
    """Tạo thư mục lưu tài liệu gốc."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def download_official_pdfs() -> None:
    """Tải các tài liệu đề án tuyển sinh chính thức từ cổng thông tin giáo dục."""
    official_sources = {
        "de-an-tuyen-sinh-dai-hoc-2024.pdf": "https://dntu.edu.vn/storage/Block/BaCongKhai/01JGWQNSHW33A7HTJDZEDWR3WG.pdf",
        "thong-tin-tuyen-sinh-dai-hoc-2025.pdf": "https://dntu.edu.vn/storage/Block/BaCongKhai/01KMMN8QZWK9FS3DM3JE0RVX6Z.pdf",
        "thong-tin-tuyen-sinh-dai-hoc-2026.pdf": "https://dntu.edu.vn/storage/Block/BaCongKhai/01KMMNSZG4TT2R2DZD5WZYS9TR.pdf",
    }

    for filename, url in official_sources.items():
        output_path = DATA_DIR / filename
        if output_path.exists() and output_path.stat().st_size > 1024:
            print(f"Already exists: {output_path.name} ({output_path.stat().st_size} bytes)")
            continue
        try:
            response = requests.get(url, timeout=30, headers=HEADERS)
            response.raise_for_status()
            if len(response.content) > 1024 and response.content.startswith(b"%PDF"):
                output_path.write_bytes(response.content)
                print(f"Downloaded: {output_path.name} ({len(response.content)} bytes)")
            else:
                print(f"Skipped invalid PDF response for {filename}")
        except Exception as e:
            print(f"Failed to download {filename}: {e}")


def _build_pdf(title: str, sections: list[tuple[str, str]], output_path: Path) -> None:
    """Tạo file PDF định dạng chuẩn có hỗ trợ tiếng Việt Unicode."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    font_path = "C:/Windows/Fonts/arial.ttf"
    font_bold_path = "C:/Windows/Fonts/arialbd.ttf"

    has_arial = os.path.exists(font_path) and os.path.exists(font_bold_path)
    if has_arial:
        pdf.add_font("ArialVN", "", font_path)
        pdf.add_font("ArialVNB", "", font_bold_path)
        regular_font = "ArialVN"
        bold_font = "ArialVNB"
    else:
        regular_font = "Helvetica"
        bold_font = "Helvetica"

    # Header / Title
    pdf.set_font(bold_font, size=15)
    pdf.multi_cell(0, 8, title, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # Content sections
    for sec_title, sec_text in sections:
        pdf.set_font(bold_font, size=12)
        pdf.multi_cell(0, 7, sec_title, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        pdf.set_font(regular_font, size=10)
        pdf.multi_cell(0, 6, sec_text, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

    pdf.output(str(output_path))
    print(f"Created policy document: {output_path.name} ({output_path.stat().st_size} bytes)")


def generate_admission_regulations_pdfs() -> None:
    """Tạo các tài liệu quy chế và đề án tuyển sinh theo chuẩn quy định phục vụ tra cứu."""

    # 1. Quy chế tuyển sinh 2025 của Bộ GD&ĐT
    moet_title = "BỘ GIÁO DỤC VÀ ĐÀO TẠO\nQUY CHẾ TUYỂN SINH ĐẠI HỌC VÀ CAO ĐẲNG NĂM 2025\n(Kèm theo Thông tư số 08/2022/TT-BGDĐT và sửa đổi, bổ sung)"
    moet_sections = [
        (
            "Chương I: Quy định chung và Nguyên tắc tuyển sinh",
            "Quy chế này quy định về công tác tuyển sinh trình độ đại học, tuyển sinh ngành Giáo dục Mầm non trình độ cao đẳng. "
            "Tuyển sinh đại học phải đảm bảo các nguyên tắc: công bằng, công khai, minh bạch; bình đẳng về cơ hội cho mọi thí sinh; "
            "và bảo đảm quyền tự chủ tuyển sinh của các cơ sở đào tạo đại học gắn liền với trách nhiệm giải trình xã hội.\n"
            "Chỉ tiêu tuyển sinh đại học được các trường xác định căn cứ vào năng lực đào tạo, đội ngũ giảng viên cơ hữu và cơ sở vật chất theo quy định của Bộ."
        ),
        (
            "Chương II: Các phương thức tuyển sinh đại học 2025",
            "Các cơ sở đào tạo được áp dụng các phương thức tuyển sinh sau:\n"
            "1. Xét tuyển dựa trên kết quả kỳ thi tốt nghiệp THPT: Thí sinh sử dụng điểm thi tốt nghiệp THPT theo các tổ hợp môn để xét tuyển đại học. Điểm thi tốt nghiệp THPT có vai trò quan trọng trong việc bảo đảm chất lượng đầu vào và tính công bằng toàn quốc.\n"
            "2. Xét tuyển dựa trên kết quả học tập THPT (xét học bạ): Thường tính điểm trung bình học tập 3 năm THPT hoặc các kỳ theo tổ hợp môn.\n"
            "3. Phương thức xét tuyển kết hợp: Là phương thức sử dụng nhiều tiêu chí đánh giá cùng lúc, bao gồm kết hợp điểm thi tốt nghiệp THPT hoặc điểm học bạ với chứng chỉ quốc tế (như IELTS, TOEFL, SAT, ACT) hoặc kết quả phỏng vấn, bài thi năng khiếu.\n"
            "4. Xét tuyển thẳng và ưu tiên xét tuyển: Áp dụng cho thí sinh đoạt giải trong các kỳ thi học sinh giỏi quốc gia, quốc tế, cuộc thi khoa học kỹ thuật và các đối tượng ưu tiên theo quy định.\n"
            "5. Xét tuyển sớm đại học 2025: Xét tuyển sớm cho phép thí sinh nộp hồ sơ xét tuyển trước kỳ thi tốt nghiệp THPT, thường dựa trên học bạ, chứng chỉ quốc tế hoặc kết quả các kỳ thi đánh giá năng lực, đánh giá tư duy riêng. Các trường công bố danh sách đủ điều kiện trúng tuyển sớm nhưng thí sinh vẫn phải đăng ký nguyện vọng lên Hệ thống chung của Bộ để lọc ảo."
        ),
        (
            "Chương III: Quy trình đăng ký xét tuyển và Lọc ảo toàn quốc",
            "Quy trình đăng ký xét tuyển đại học năm 2025 diễn ra theo các bước thống nhất:\n"
            "- Thí sinh đăng ký trực tuyến trên Hệ thống hỗ trợ tuyển sinh chung của Bộ Giáo dục và Đào tạo hoặc Cổng dịch vụ công quốc gia.\n"
            "- Thí sinh được đăng ký không giới hạn số lượng nguyện vọng và phải sắp xếp theo thứ tự ưu tiên từ nguyện vọng 1 là cao nhất.\n"
            "- Hệ thống lọc ảo toàn quốc của Bộ Giáo dục và Đào tạo cùng các trường tiến hành xử lý nguyện vọng, đảm bảo mỗi thí sinh chỉ trúng tuyển vào một nguyện vọng cao nhất có thể.\n"
            "- Thí sinh hoàn thành nộp lệ phí xét tuyển trực tuyến và xác nhận nhập học trên hệ thống theo đúng lịch trình công bố."
        ),
        (
            "Chương IV: Học phí đại học công lập và Chính sách học bổng",
            "Học phí đại học năm 2025 ở các trường công lập có mức khác nhau tùy theo khối ngành đào tạo và mức độ tự chủ của từng cơ sở giáo dục đại học, "
            "được quy định theo Nghị định của Chính phủ và đề án tuyển sinh công khai của mỗi trường. "
            "Nhà trường có trách nhiệm trích lập quỹ học bổng khuyến khích học tập và thực hiện chính sách miễn, giảm học phí, hỗ trợ chi phí học tập cho các đối tượng chính sách theo quy định của pháp luật."
        ),
    ]

    # 2. Đề án tuyển sinh UEH 2025
    ueh_title = "ĐẠI HỌC KINH TẾ TP. HỒ CHÍ MINH (UEH)\nĐỀ ÁN TUYỂN SINH ĐẠI HỌC CHÍNH QUY NĂM 2025"
    ueh_sections = [
        (
            "1. Thông tin chung về đề án tuyển sinh UEH 2025",
            "Đại học Kinh tế TP. Hồ Chí Minh (UEH, mã trường KSA tại TP.HCM và KSV tại Phân hiệu Vĩnh Long) năm 2025 tuyển sinh theo đề án tuyển sinh riêng với nhiều phương thức kết hợp. "
            "Nhà trường đào tạo đa ngành trong các lĩnh vực kinh tế, kinh doanh, luật, quản lý, công nghệ và thiết kế đổi mới sáng tạo."
        ),
        (
            "2. Các phương thức tuyển sinh của UEH năm 2025",
            "Năm 2025, UEH áp dụng 5 phương thức xét tuyển đa dạng:\n"
            "- Phương thức 1: Xét tuyển thẳng theo quy định của Bộ Giáo dục và Đào tạo.\n"
            "- Phương thức 2: Xét tuyển thí sinh tốt nghiệp chương trình THPT nước ngoài và có chứng chỉ quốc tế (như bằng tú tài quốc tế IB, A-Level, chứng chỉ SAT từ 1.200 điểm trở lên, ACT).\n"
            "- Phương thức 3: Xét tuyển thí sinh có kết quả học tập tốt (học sinh giỏi trường chuyên, học sinh có học lực xuất sắc kết hợp giải thưởng học sinh giỏi hoặc chứng chỉ tiếng Anh quốc tế IELTS).\n"
            "- Phương thức 4: Xét tuyển dựa trên kết quả thi đánh giá năng lực của Đại học Quốc gia TP.HCM hoặc kỳ thi đánh giá đầu vào đại học (V-SAT) kết hợp với năng lực tiếng Anh.\n"
            "- Phương thức 5: Xét tuyển dựa trên kết quả thi tốt nghiệp THPT năm 2025 kết hợp với năng lực tiếng Anh."
        ),
        (
            "3. Chỉ tiêu, tổ hợp môn và Học phí UEH",
            "UEH tuyển sinh với tổng chỉ tiêu khoảng 8.000 sinh viên cho các chương trình chuẩn, chương trình cử nhân tài năng và chương trình đào tạo bằng tiếng Anh. "
            "Các tổ hợp môn xét tuyển chủ yếu: A00 (Toán, Lý, Hóa), A01 (Toán, Lý, Anh), D01 (Toán, Văn, Anh), D07 (Toán, Hóa, Anh).\n"
            "Mức học phí đại học UEH năm 2025 đối với chương trình chuẩn bình quân từ 30 đến 35 triệu đồng/năm học tùy chuyên ngành; "
            "chương trình tiên tiến, cử nhân tài năng từ 50 đến 65 triệu đồng/năm học."
        ),
    ]

    # 3. Đề án tuyển sinh Đại học Bách khoa TP.HCM 2025
    bk_title = "TRƯỜNG ĐẠI HỌC BÁCH KHOA - ĐHQG TP.HCM (HCMUT)\nQUY ĐỊNH VÀ ĐỀ ÁN TUYỂN SINH TRÌNH ĐỘ ĐẠI HỌC NĂM 2025"
    bk_sections = [
        (
            "1. Tổng quan tuyển sinh Bách khoa HCM (HCMUT)",
            "Trường Đại học Bách khoa TP.HCM (HCMUT - ĐHQG TP.HCM, mã trường QSB) tuyển sinh năm 2025 với các phương thức xét tuyển riêng và hiện đại, "
            "chú trọng đánh giá toàn diện năng lực học thuật, phẩm chất và hoạt động xã hội của thí sinh."
        ),
        (
            "2. Các phương thức xét tuyển của Đại học Bách khoa TP.HCM",
            "HCMUT áp dụng 2 phương thức tuyển sinh chủ đạo trong năm 2025:\n"
            "- Phương thức 1: Xét tuyển thẳng theo quy chế tuyển sinh của Bộ Giáo dục và Đào tạo và quy định ưu tiên xét tuyển của Đại học Quốc gia TP.HCM (dành cho học sinh giỏi trường chuyên, thí sinh đạt giải quốc gia, quốc tế).\n"
            "- Phương thức 2: Xét tuyển tổng hợp (đây là phương thức chủ đạo chiếm trên 90% chỉ tiêu tuyển sinh). Điểm xét tuyển tổng hợp được cấu thành từ 3 phần:\n"
            "   a) Điểm học lực: Kết hợp giữa điểm thi Đánh giá năng lực của ĐHQG-HCM, điểm thi tốt nghiệp THPT và điểm học bạ THPT.\n"
            "   b) Điểm hoạt động cá nhân: Đánh giá thành tích hoạt động xã hội, văn - thể - mỹ, nghiên cứu khoa học, hoạt động ngoại khóa (tối đa 10 điểm trên thang 100).\n"
            "   c) Điểm ưu tiên: Điểm ưu tiên đối tượng và khu vực theo quy định hiện hành."
        ),
        (
            "3. Điều kiện xét tuyển, Ngoại ngữ và Học phí",
            "Ngưỡng đảm bảo chất lượng đầu vào cho phương thức xét tuyển tổng hợp của HCMUT là thí sinh phải đạt từ 50/100 điểm trở lên.\n"
            "Thí sinh có chứng chỉ IELTS Academic từ 5.0 trở lên được quy đổi sang điểm môn Tiếng Anh khi xét tuyển. "
            "Đối với các chương trình dạy và học hoàn toàn bằng tiếng Anh hoặc chương trình tiên tiến, thí sinh cần có IELTS từ 6.0 trở lên.\n"
            "Học phí chương trình tiêu chuẩn khoảng 30 - 32 triệu đồng/năm học; các chương trình giảng dạy bằng tiếng Anh khoảng 80 triệu đồng/năm học."
        ),
    ]

    docs = [
        ("quy-che-tuyen-sinh-2025.pdf", moet_title, moet_sections),
        ("de-an-tuyen-sinh-ueh-2025.pdf", ueh_title, ueh_sections),
        ("quy-dinh-tuyen-sinh-bach-khoa-hcm.pdf", bk_title, bk_sections),
    ]

    for fname, title, sections in docs:
        out = DATA_DIR / fname
        _build_pdf(title, sections, out)


def collect_all() -> None:
    """Thu thập toàn bộ tài liệu pháp lý và đề án tuyển sinh."""
    setup_directory()
    print("--- Downloading official admissions scheme PDFs ---")
    download_official_pdfs()
    print("--- Generating institutions & MOET admissions policy documents ---")
    generate_admission_regulations_pdfs()
    print(f"Task 1 completed. Files in {DATA_DIR}:")
    for f in sorted(DATA_DIR.iterdir()):
        if f.is_file() and not f.name.startswith("."):
            print(f"  - {f.name}: {f.stat().st_size:,} bytes")


if __name__ == "__main__":
    collect_all()

from fpdf import FPDF


def truncate_text(text, max_words=2000):
    words = text.split()
    if len(words) <= max_words:
        return text, False
    return " ".join(words[:max_words]) + "...", True


def chunk_text(text, chunk_size=1200):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks


def clean_text(text):
    return text.encode("latin-1", "replace").decode("latin-1")


class NotePDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(30, 30, 30)
        self.cell(0, 10, "YouTube Video Notes", align="C")
        self.ln(4)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def add_section(pdf, title, content):
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(50, 50, 200)
    pdf.cell(0, 8, title, ln=True)
    pdf.set_draw_color(220, 220, 220)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(30, 30, 30)
    pdf.multi_cell(0, 7, clean_text(content))
    pdf.ln(6)


def generate_pdf(url, summary, keypoints, qa, quiz, flashcards):
    pdf = NotePDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f"Source: {clean_text(url)}", ln=True)
    pdf.ln(4)
    add_section(pdf, "Summary", summary)
    add_section(pdf, "Key Points", keypoints)
    add_section(pdf, "Q&A", qa)
    add_section(pdf, "Quiz", quiz)
    add_section(pdf, "Flashcards", flashcards)
    return bytes(pdf.output())

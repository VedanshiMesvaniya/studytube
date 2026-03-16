from fpdf import FPDF
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

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

def generate_chart(chart_type, title, labels, values, theme='Dark'):
    bg = '#13131e' if theme == 'Dark' else '#ffffff'
    fg = '#eeeef5' if theme == 'Dark' else '#1a0f2e'
    accent = '#a78bfa' if theme == 'Dark' else '#7c3aed'
    accent2 = '#818cf8' if theme == 'Dark' else '#6366f1'
    grid_color = '#2a2a40' if theme == 'Dark' else '#ddd0ff'

    colors = [
        '#a78bfa', '#818cf8', '#6ee7b7', '#fbbf24',
        '#f472b6', '#34d399', '#60a5fa', '#f87171'
    ]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)

    if chart_type == 'bar':
        bars = ax.bar(labels, values, color=colors[:len(labels)],
                      edgecolor='none', zorder=3)
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(values) * 0.02,
                    str(val), ha='center', va='bottom',
                    color=fg, fontsize=9, fontweight='500')
        ax.set_ylim(0, max(values) * 1.18)

    elif chart_type == 'line':
        ax.plot(labels, values, color=accent, linewidth=2.5,
                marker='o', markersize=7, markerfacecolor=accent2,
                markeredgecolor=bg, markeredgewidth=2, zorder=3)
        ax.fill_between(range(len(labels)), values,
                        alpha=0.12, color=accent)
        ax.set_ylim(0, max(values) * 1.2)

    elif chart_type == 'pie':
        wedges, texts, autotexts = ax.pie(
            values, labels=labels, colors=colors[:len(labels)],
            autopct='%1.1f%%', startangle=90,
            wedgeprops=dict(edgecolor=bg, linewidth=2)
        )
        for text in texts:
            text.set_color(fg)
            text.set_fontsize(9)
        for autotext in autotexts:
            autotext.set_color(bg)
            autotext.set_fontsize(8)
            autotext.set_fontweight('bold')

    if chart_type != 'pie':
        ax.tick_params(colors=fg, labelsize=9)
        ax.spines['bottom'].set_color(grid_color)
        ax.spines['left'].set_color(grid_color)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.yaxis.grid(True, color=grid_color, linewidth=0.5, zorder=0)
        ax.set_axisbelow(True)
        plt.xticks(rotation=20 if len(max(labels, key=len)) > 8 else 0)

    ax.set_title(title, color=fg, fontsize=13, fontweight='600', pad=16)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150,
                bbox_inches='tight', facecolor=bg)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode()
    plt.close()
    return img_b64

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
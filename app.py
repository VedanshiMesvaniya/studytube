import streamlit as st
import streamlit.components.v1 as components
import re
from transcript import get_transcript, SUPPORTED_LANGUAGES
from summarizer import get_summary, get_keypoints, get_qa, get_quiz, get_flashcards, get_visuals
from utils import generate_pdf, truncate_text, generate_chart

st.set_page_config(
    page_title="StudyTube",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='22' fill='%237c3aed'/><text y='74' x='50' text-anchor='middle' font-size='58' fill='white' font-family='serif'>S</text></svg>",
    layout="centered",
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None}
)

for key, val in [('theme', 'Dark'), ('results', None), ('quiz_submitted', False)]:
    if key not in st.session_state:
        st.session_state[key] = val

T = {
    'Dark': {
        'bg': '#0d0d14', 'surface': '#13131e', 'surface2': '#1a1a28',
        'border': '#2a2a40', 'text': '#eeeef5', 'text2': '#7878a0',
        'accent': '#a78bfa', 'accent2': '#818cf8', 'accent_dark': '#7c3aed',
        'accent_bg': 'rgba(167,139,250,0.12)', 'btn_text': '#ffffff',
        'correct': '#86efac', 'correct_bg': '#052e16',
        'wrong': '#fca5a5', 'wrong_bg': '#2d0707',
        'card_back': '#1e1040', 'card_back_text': '#ddd6fe',
        'tab_active_text': '#ffffff', 'input_bg': '#13131e',
        'aurora1': 'rgba(124,58,237,0.18)', 'aurora2': 'rgba(79,70,229,0.14)',
        'aurora3': 'rgba(16,185,129,0.08)',
    },
    'Light': {
        'bg': '#faf7ff', 'surface': '#ffffff', 'surface2': '#f0ebff',
        'border': '#ddd0ff', 'text': '#1a0f2e', 'text2': '#6b5b95',
        'accent': '#7c3aed', 'accent2': '#6366f1', 'accent_dark': '#5b21b6',
        'accent_bg': 'rgba(124,58,237,0.08)', 'btn_text': '#ffffff',
        'correct': '#15803d', 'correct_bg': '#f0fdf4',
        'wrong': '#b91c1c', 'wrong_bg': '#fff1f1',
        'card_back': '#f5f0ff', 'card_back_text': '#5b21b6',
        'tab_active_text': '#ffffff', 'input_bg': '#ffffff',
        'aurora1': 'rgba(124,58,237,0.07)', 'aurora2': 'rgba(99,102,241,0.05)',
        'aurora3': 'rgba(16,185,129,0.04)',
    },
}

def get_css(theme_name):
    if theme_name == 'System':
        d = T['Dark']
        l = T['Light']
        return f"""<style>
        @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,800&family=Nunito:wght@400;500;600&display=swap');
        html,body,[class*="css"]{{font-family:'Nunito',sans-serif!important;font-size:17px!important}}
        [data-testid="stDeployButton"],[data-testid="stToolbar"],#MainMenu,footer,header{{display:none!important;visibility:hidden!important}}

        .stForm{{background:transparent!important;border:none!important;padding:0!important}}
        .stTextInput>div>div>input{{border-radius:14px!important;font-family:'Nunito',sans-serif!important;font-size:1.05rem!important;padding:16px 20px!important;transition:all .25s!important}}
        .stButton>button,[data-testid="stFormSubmitButton"]>button{{border:none!important;border-radius:14px!important;font-family:'Nunito',sans-serif!important;font-weight:600!important;font-size:1.05rem!important;padding:15px 28px!important;transition:all .25s!important;letter-spacing:0.3px!important}}
        .stButton>button:hover,[data-testid="stFormSubmitButton"]>button:hover{{filter:brightness(1.12)!important;transform:translateY(-2px)!important}}
        .stSelectbox>div>div{{border-radius:12px!important;font-family:'Nunito',sans-serif!important}}
        .stTabs [data-baseweb="tab-list"]{{border-radius:14px!important;padding:5px!important;gap:4px!important;border:none!important}}
        .stTabs [data-baseweb="tab"]{{background:transparent!important;border-radius:11px!important;font-family:'Nunito',sans-serif!important;font-size:0.95rem!important;font-weight:500!important;padding:9px 18px!important;border:none!important;transition:all .2s!important}}
        .stTabs [data-baseweb="tab-panel"]{{border-radius:0 0 18px 18px!important;padding:28px!important;border-width:1.5px!important;border-top:none!important;font-family:'Nunito',sans-serif!important;font-size:1.05rem!important;line-height:1.85!important}}
        .stMarkdown p,.stMarkdown li{{font-family:'Nunito',sans-serif!important;font-size:1.05rem!important;line-height:1.85!important}}
        .stMarkdown h1,.stMarkdown h2,.stMarkdown h3{{font-family:'Bricolage Grotesque',sans-serif!important;font-weight:700!important}}
        .stExpander{{border-radius:14px!important;margin-bottom:10px!important;border-width:1.5px!important}}
        .stExpander summary p{{font-family:'Nunito',sans-serif!important;font-size:1rem!important;font-weight:500!important}}
        .stRadio label p{{font-family:'Nunito',sans-serif!important;font-size:1rem!important}}
        [data-testid="stDownloadButton"]>button{{background:transparent!important;border-radius:14px!important;font-family:'Nunito',sans-serif!important;font-weight:600!important;font-size:1.05rem!important;padding:14px 24px!important;transition:all .25s!important;border-width:1.5px!important}}
        hr{{opacity:1!important;margin:28px 0!important}}
        .stApp::before{{content:'';position:fixed;inset:0;pointer-events:none;z-index:0;animation:aurora 12s ease-in-out infinite alternate}}
        @keyframes aurora{{0%{{opacity:1}}50%{{opacity:0.7}}100%{{opacity:1}}}}
        [data-testid="stAppViewContainer"]>section{{position:relative;z-index:1}}
        .hero-title{{font-family:'Bricolage Grotesque',sans-serif;font-size:3.4rem;font-weight:800;text-align:center;line-height:1.1;margin-bottom:8px;letter-spacing:-1px}}
        .hero-sub{{font-family:'Nunito',sans-serif;font-size:1.1rem;text-align:center;margin-bottom:2rem;font-weight:400;letter-spacing:0.1px;line-height:1.6}}
        .section-badge{{display:inline-block;border-radius:20px;font-size:0.75rem;font-weight:600;padding:4px 12px;margin-bottom:16px;letter-spacing:1px;text-transform:uppercase;font-family:'Nunito',sans-serif}}
        .correct-answer{{border-radius:10px;padding:11px 16px;font-size:0.95rem;margin-top:6px;font-family:'Nunito',sans-serif;font-weight:500}}
        .wrong-answer{{border-radius:10px;padding:11px 16px;font-size:0.95rem;margin-top:6px;font-family:'Nunito',sans-serif;font-weight:500}}
        .quiz-q{{border-radius:16px;padding:22px;margin-bottom:18px;border-width:1.5px}}
        .quiz-q p{{font-weight:600!important;margin-bottom:10px;font-size:1.05rem!important;font-family:'Nunito',sans-serif!important}}
        .word-count{{display:inline-block;border-radius:20px;font-size:0.78rem;font-weight:600;padding:4px 12px;margin-bottom:16px;letter-spacing:0.5px;font-family:'Nunito',sans-serif}}
        .visual-card{{border-radius:16px;padding:20px;margin-bottom:20px;border-width:1.5px}}
        .visual-title{{font-family:'Bricolage Grotesque',sans-serif;font-size:1.1rem;font-weight:700;margin-bottom:14px}}
        .no-visual{{border-radius:14px;padding:28px;text-align:center;font-family:'Nunito',sans-serif;font-size:0.95rem;opacity:0.6}}
        .theme-btn{{position:fixed;top:16px;right:20px;z-index:9999;font-size:13px;font-weight:600;text-decoration:none;border-radius:10px;padding:7px 14px;line-height:1;font-family:'Nunito',sans-serif;box-shadow:0 2px 16px rgba(0,0,0,0.2);transition:all .2s;letter-spacing:0.3px}}

        @media(prefers-color-scheme:dark){{
            .stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{{background:{d['bg']}!important;position:relative!important}}
            .stApp::before{{background:radial-gradient(ellipse 80% 60% at 10% 20%,{d['aurora1']},transparent),radial-gradient(ellipse 60% 50% at 90% 10%,{d['aurora2']},transparent),radial-gradient(ellipse 70% 40% at 50% 90%,{d['aurora3']},transparent)}}
            .stTextInput>div>div>input{{background:{d['input_bg']}!important;border:1.5px solid {d['border']}!important;color:{d['text']}!important}}
            .stTextInput>div>div>input:focus{{border-color:{d['accent']}!important;box-shadow:0 0 0 4px {d['accent_bg']}!important}}
            .stTextInput>div>div>input::placeholder{{color:{d['text2']}!important}}
            .stSelectbox>div>div{{background:{d['input_bg']}!important;border-color:{d['border']}!important;color:{d['text']}!important}}
            .stTabs [data-baseweb="tab-list"]{{background:{d['surface']}!important}}
            .stTabs [data-baseweb="tab"]{{color:{d['text2']}!important}}
            .stTabs [aria-selected="true"]{{background:linear-gradient(135deg,{d['accent']},{d['accent2']})!important;color:{d['tab_active_text']}!important;font-weight:600!important}}
            .stTabs [data-baseweb="tab-panel"]{{background:{d['surface']}!important;border-color:{d['border']}!important;color:{d['text']}!important}}
            .stMarkdown p,.stMarkdown li{{color:{d['text']}!important}}
            .stMarkdown h1,.stMarkdown h2,.stMarkdown h3{{color:{d['text']}!important}}
            .stButton>button,[data-testid="stFormSubmitButton"]>button{{background:linear-gradient(135deg,{d['accent']},{d['accent2']})!important;color:{d['btn_text']}!important}}
            [data-testid="stDownloadButton"]>button{{color:{d['accent']}!important;border-color:{d['accent']}!important}}
            [data-testid="stDownloadButton"]>button:hover{{background:{d['accent_bg']}!important}}
            .stExpander{{background:{d['surface2']}!important;border-color:{d['border']}!important}}
            .stExpander summary p{{color:{d['text']}!important}}
            [data-testid="stExpanderToggleIcon"]{{color:{d['accent']}!important}}
            .stRadio label p{{color:{d['text']}!important}}
            .stRadio [data-baseweb="radio"] div{{border-color:{d['accent']}!important}}
            .stAlert{{background:{d['surface2']}!important;border-color:{d['border']}!important;border-radius:14px!important}}
            .stAlert p{{color:{d['text']}!important}}
            .stSpinner>div{{border-top-color:{d['accent']}!important}}
            hr{{border-color:{d['border']}!important}}
            .hero-title{{color:{d['text']}}}
            .hero-accent{{background:linear-gradient(135deg,{d['accent']},{d['accent2']});-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}
            .hero-sub{{color:{d['text2']}}}
            .section-badge{{background:{d['accent_bg']};color:{d['accent']};border:1px solid {d['accent_bg']}}}
            .correct-answer{{background:{d['correct_bg']};border:1px solid {d['correct']};color:{d['correct']}}}
            .wrong-answer{{background:{d['wrong_bg']};border:1px solid {d['wrong']};color:{d['wrong']}}}
            .quiz-q{{background:{d['surface2']};border-color:{d['border']}}}
            .quiz-q p{{color:{d['text']}!important}}
            .word-count{{background:{d['accent_bg']};color:{d['accent']};border:1px solid {d['accent_bg']}}}
            .visual-card{{background:{d['surface2']};border:1.5px solid {d['border']}}}
            .visual-title{{color:{d['text']}}}
            .no-visual{{background:{d['surface2']};color:{d['text2']}}}
            .theme-btn{{background:{d['surface']};color:{d['text']};border:1.5px solid {d['border']}}}
            .theme-btn:hover{{border-color:{d['accent']};color:{d['accent']}!important}}
            .stForm{{background:transparent!important;border:none!important;padding:0!important}}
        }}
        @media(prefers-color-scheme:light){{
            .stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{{background:{l['bg']}!important;position:relative!important}}
            .stApp::before{{background:radial-gradient(ellipse 80% 60% at 10% 20%,{l['aurora1']},transparent),radial-gradient(ellipse 60% 50% at 90% 10%,{l['aurora2']},transparent),radial-gradient(ellipse 70% 40% at 50% 90%,{l['aurora3']},transparent)}}
            .stTextInput>div>div>input{{background:{l['input_bg']}!important;border:1.5px solid {l['border']}!important;color:{l['text']}!important}}
            .stTextInput>div>div>input:focus{{border-color:{l['accent']}!important;box-shadow:0 0 0 4px {l['accent_bg']}!important}}
            .stTextInput>div>div>input::placeholder{{color:{l['text2']}!important}}
            .stSelectbox>div>div{{background:{l['input_bg']}!important;border-color:{l['border']}!important;color:{l['text']}!important}}
            .stTabs [data-baseweb="tab-list"]{{background:{l['surface2']}!important}}
            .stTabs [data-baseweb="tab"]{{color:{l['text2']}!important}}
            .stTabs [aria-selected="true"]{{background:linear-gradient(135deg,{l['accent']},{l['accent2']})!important;color:{l['tab_active_text']}!important;font-weight:600!important}}
            .stTabs [data-baseweb="tab-panel"]{{background:{l['surface']}!important;border-color:{l['border']}!important;color:{l['text']}!important}}
            .stMarkdown p,.stMarkdown li{{color:{l['text']}!important}}
            .stMarkdown h1,.stMarkdown h2,.stMarkdown h3{{color:{l['text']}!important}}
            .stButton>button,[data-testid="stFormSubmitButton"]>button{{background:linear-gradient(135deg,{l['accent']},{l['accent2']})!important;color:{l['btn_text']}!important}}
            [data-testid="stDownloadButton"]>button{{color:{l['accent']}!important;border-color:{l['accent']}!important}}
            [data-testid="stDownloadButton"]>button:hover{{background:{l['accent_bg']}!important}}
            .stExpander{{background:{l['surface']}!important;border-color:{l['border']}!important}}
            .stExpander summary p{{color:{l['text']}!important}}
            [data-testid="stExpanderToggleIcon"]{{color:{l['accent']}!important}}
            .stRadio label p{{color:{l['text']}!important}}
            .stRadio [data-baseweb="radio"] div{{border-color:{l['accent']}!important}}
            .stAlert{{background:{l['surface2']}!important;border-color:{l['border']}!important;border-radius:14px!important}}
            .stAlert p{{color:{l['text']}!important}}
            .stSpinner>div{{border-top-color:{l['accent']}!important}}
            hr{{border-color:{l['border']}!important}}
            .hero-title{{color:{l['text']}}}
            .hero-accent{{background:linear-gradient(135deg,{l['accent']},{l['accent2']});-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}
            .hero-sub{{color:{l['text2']}}}
            .section-badge{{background:{l['accent_bg']};color:{l['accent']};border:1px solid {l['accent_bg']}}}
            .correct-answer{{background:{l['correct_bg']};border:1px solid {l['correct']};color:{l['correct']}}}
            .wrong-answer{{background:{l['wrong_bg']};border:1px solid {l['wrong']};color:{l['wrong']}}}
            .quiz-q{{background:{l['surface2']};border-color:{l['border']}}}
            .quiz-q p{{color:{l['text']}!important}}
            .word-count{{background:{l['accent_bg']};color:{l['accent']};border:1px solid {l['accent_bg']}}}
            .visual-card{{background:{l['surface2']};border:1.5px solid {l['border']}}}
            .visual-title{{color:{l['text']}}}
            .no-visual{{background:{l['surface2']};color:{l['text2']}}}
            .theme-btn{{background:{l['surface']};color:{l['text']};border:1.5px solid {l['border']}}}
            .theme-btn:hover{{border-color:{l['accent']};color:{l['accent']}!important}}
            .stForm{{background:transparent!important;border:none!important;padding:0!important}}
        }}
        </style>"""

    t = T[theme_name]
    return f"""<style>
    @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,800&family=Nunito:wght@400;500;600&display=swap');
    html,body,[class*="css"]{{font-family:'Nunito',sans-serif!important;font-size:17px!important}}
    [data-testid="stDeployButton"],[data-testid="stToolbar"],#MainMenu,footer,header{{display:none!important;visibility:hidden!important}}

    .stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{{background:{t['bg']}!important;position:relative!important}}
    .stApp::before{{
        content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
        background:
            radial-gradient(ellipse 80% 60% at 10% 20%,{t['aurora1']},transparent),
            radial-gradient(ellipse 60% 50% at 90% 10%,{t['aurora2']},transparent),
            radial-gradient(ellipse 70% 40% at 50% 90%,{t['aurora3']},transparent);
        animation:aurora 12s ease-in-out infinite alternate;
    }}
    @keyframes aurora{{0%{{opacity:1}}50%{{opacity:0.7}}100%{{opacity:1}}}}
    [data-testid="stAppViewContainer"]>section{{position:relative;z-index:1}}
    .stForm{{background:transparent!important;border:none!important;padding:0!important}}

    .stTextInput>div>div>input{{
        background:{t['input_bg']}!important;border:1.5px solid {t['border']}!important;
        border-radius:14px!important;color:{t['text']}!important;
        font-family:'Nunito',sans-serif!important;font-size:1.05rem!important;
        padding:16px 20px!important;transition:all .25s!important;
    }}
    .stTextInput>div>div>input:focus{{border-color:{t['accent']}!important;box-shadow:0 0 0 4px {t['accent_bg']}!important}}
    .stTextInput>div>div>input::placeholder{{color:{t['text2']}!important}}

    .stSelectbox>div>div{{
        background:{t['input_bg']}!important;border:1.5px solid {t['border']}!important;
        border-radius:12px!important;color:{t['text']}!important;
        font-family:'Nunito',sans-serif!important;transition:all .25s!important;
    }}
    .stSelectbox label p{{color:{t['text2']}!important;font-size:0.85rem!important;font-family:'Nunito',sans-serif!important}}

    .stButton>button,[data-testid="stFormSubmitButton"]>button{{
        background:linear-gradient(135deg,{t['accent']},{t['accent2']})!important;
        color:{t['btn_text']}!important;border:none!important;border-radius:14px!important;
        font-family:'Nunito',sans-serif!important;font-weight:600!important;
        font-size:1.05rem!important;padding:15px 28px!important;
        transition:all .25s!important;letter-spacing:0.3px!important;
    }}
    .stButton>button:hover,[data-testid="stFormSubmitButton"]>button:hover{{
        filter:brightness(1.12)!important;transform:translateY(-2px)!important;
        box-shadow:0 10px 30px {t['accent_bg']}!important;
    }}

    .stTabs [data-baseweb="tab-list"]{{background:{t['surface']}!important;border-radius:14px!important;padding:5px!important;gap:4px!important;border:none!important}}
    .stTabs [data-baseweb="tab"]{{background:transparent!important;color:{t['text2']}!important;border-radius:11px!important;font-family:'Nunito',sans-serif!important;font-size:0.95rem!important;font-weight:500!important;padding:9px 18px!important;border:none!important;transition:all .2s!important}}
    .stTabs [aria-selected="true"]{{background:linear-gradient(135deg,{t['accent']},{t['accent2']})!important;color:{t['tab_active_text']}!important;font-weight:600!important}}
    .stTabs [data-baseweb="tab-panel"]{{background:{t['surface']}!important;border-radius:0 0 18px 18px!important;padding:28px!important;border:1.5px solid {t['border']}!important;border-top:none!important;color:{t['text']}!important;font-family:'Nunito',sans-serif!important;font-size:1.05rem!important;line-height:1.85!important}}

    .stMarkdown p{{color:{t['text']}!important;font-family:'Nunito',sans-serif!important;font-size:1.05rem!important;line-height:1.85!important}}
    .stMarkdown li{{color:{t['text']}!important;font-family:'Nunito',sans-serif!important;font-size:1.05rem!important;line-height:1.85!important}}
    .stMarkdown h1,.stMarkdown h2,.stMarkdown h3{{font-family:'Bricolage Grotesque',sans-serif!important;color:{t['text']}!important;font-weight:700!important}}

    .stExpander{{background:{t['surface2']}!important;border:1.5px solid {t['border']}!important;border-radius:14px!important;margin-bottom:10px!important}}
    .stExpander summary p{{color:{t['text']}!important;font-family:'Nunito',sans-serif!important;font-size:1rem!important;font-weight:500!important}}
    [data-testid="stExpanderToggleIcon"]{{color:{t['accent']}!important}}
    .stRadio label p{{color:{t['text']}!important;font-family:'Nunito',sans-serif!important;font-size:1rem!important}}
    .stRadio [data-baseweb="radio"] div{{border-color:{t['accent']}!important}}

    [data-testid="stDownloadButton"]>button{{
        background:transparent!important;color:{t['accent']}!important;
        border:1.5px solid {t['accent']}!important;border-radius:14px!important;
        font-family:'Nunito',sans-serif!important;font-weight:600!important;
        font-size:1.05rem!important;padding:14px 24px!important;transition:all .25s!important;
    }}
    [data-testid="stDownloadButton"]>button:hover{{background:{t['accent_bg']}!important;transform:translateY(-2px)!important}}

    .stSpinner>div{{border-top-color:{t['accent']}!important}}
    [data-testid="stCaptionContainer"] p{{color:{t['text2']}!important;font-size:0.85rem!important}}
    .stAlert{{background:{t['surface2']}!important;border-color:{t['border']}!important;border-radius:14px!important}}
    .stAlert p{{color:{t['text']}!important}}
    hr{{border-color:{t['border']}!important;opacity:1!important;margin:28px 0!important}}

    .hero-title{{font-family:'Bricolage Grotesque',sans-serif;font-size:3.4rem;font-weight:800;color:{t['text']};text-align:center;line-height:1.1;margin-bottom:8px;letter-spacing:-1px}}
    .hero-accent{{background:linear-gradient(135deg,{t['accent']},{t['accent2']});-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}
    .hero-sub{{font-family:'Nunito',sans-serif;font-size:1.1rem;color:{t['text2']};text-align:center;margin-bottom:2rem;font-weight:400;letter-spacing:0.1px;line-height:1.6}}
    .section-badge{{display:inline-block;background:{t['accent_bg']};color:{t['accent']};border:1px solid {t['accent_bg']};border-radius:20px;font-size:0.75rem;font-weight:600;padding:4px 12px;margin-bottom:16px;letter-spacing:1px;text-transform:uppercase;font-family:'Nunito',sans-serif}}
    .correct-answer{{background:{t['correct_bg']};border:1px solid {t['correct']};border-radius:10px;padding:11px 16px;color:{t['correct']};font-size:0.95rem;margin-top:6px;font-family:'Nunito',sans-serif;font-weight:500}}
    .wrong-answer{{background:{t['wrong_bg']};border:1px solid {t['wrong']};border-radius:10px;padding:11px 16px;color:{t['wrong']};font-size:0.95rem;margin-top:6px;font-family:'Nunito',sans-serif;font-weight:500}}
    .quiz-q{{background:{t['surface2']};border:1.5px solid {t['border']};border-radius:16px;padding:22px;margin-bottom:18px}}
    .quiz-q p{{color:{t['text']}!important;font-weight:600!important;margin-bottom:10px;font-size:1.05rem!important;font-family:'Nunito',sans-serif!important}}
    .word-count{{display:inline-block;background:{t['accent_bg']};color:{t['accent']};border:1px solid {t['accent_bg']};border-radius:20px;font-size:0.78rem;font-weight:600;padding:4px 12px;margin-bottom:16px;letter-spacing:0.5px;font-family:'Nunito',sans-serif}}
    .visual-card{{background:{t['surface2']};border:1.5px solid {t['border']};border-radius:16px;padding:20px;margin-bottom:20px}}
    .visual-title{{font-family:'Bricolage Grotesque',sans-serif;font-size:1.1rem;font-weight:700;color:{t['text']};margin-bottom:14px}}
    .no-visual{{background:{t['surface2']};border-radius:14px;padding:28px;text-align:center;font-family:'Nunito',sans-serif;font-size:0.95rem;color:{t['text2']}}}
    .theme-btn{{position:fixed;top:16px;right:20px;z-index:9999;font-size:13px;font-weight:600;text-decoration:none;background:{t['surface']};color:{t['text']};border:1.5px solid {t['border']};border-radius:10px;padding:7px 14px;line-height:1;font-family:'Nunito',sans-serif;box-shadow:0 2px 16px rgba(0,0,0,0.2);transition:all .2s;letter-spacing:0.3px}}
    .theme-btn:hover{{border-color:{t['accent']};color:{t['accent']}!important}}
    </style>"""


def render_mermaid(mermaid_code, theme_name):
    bg = '#13131e' if theme_name != 'Light' else '#ffffff'
    t = T['Dark'] if theme_name != 'Light' else T['Light']
    dark = 'true' if theme_name != 'Light' else 'false'
    return f"""<!DOCTYPE html><html><head>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
    body{{background:transparent;margin:0;padding:8px}}
    .mermaid svg{{border-radius:12px;max-width:100%}}
    </style>
    </head><body>
    <div class="mermaid">
    %%{{init:{{'theme':'{"dark" if theme_name != "Light" else "default"}','themeVariables':{{'primaryColor':'{t["accent"]}','primaryTextColor':'{t["text"]}','primaryBorderColor':'{t["border"]}','lineColor':'{t["text2"]}','background':'{bg}','mainBkg':'{t["surface2"]}'}}}}}}%%
    {mermaid_code}
    </div>
    <script>mermaid.initialize({{startOnLoad:true,theme:'{"dark" if theme_name != "Light" else "default"}'}});</script>
    </body></html>"""


def parse_quiz(text):
    questions = []
    blocks = re.split(r'\nQ\d+:', '\n' + text.strip())
    blocks = [b.strip() for b in blocks if b.strip()]
    for block in blocks:
        lines = [l.strip() for l in block.split('\n') if l.strip()]
        if not lines:
            continue
        question = lines[0]
        options = {}
        answer = None
        for line in lines[1:]:
            m = re.match(r'^([A-D])\)\s*(.*)', line)
            if m:
                options[m.group(1)] = m.group(2)
            elif line.lower().startswith('answer:'):
                answer = re.sub(r'[^A-D]', '', line.split(':', 1)[1].strip().upper())
                if answer:
                    answer = answer[0]
        if question and len(options) >= 2 and answer:
            questions.append({'question': question, 'options': options, 'answer': answer})
    return questions


def parse_flashcards(text):
    pairs = []
    cards = text.strip().split('FRONT:')
    for card in cards:
        if 'BACK:' in card:
            parts = card.split('BACK:', 1)
            front = parts[0].strip()
            back = parts[1].strip()
            if front and back:
                pairs.append((front, back))
    return pairs


def render_flashcards_html(pairs, theme_name):
    t = T['Dark'] if theme_name == 'System' else T[theme_name]
    cards_html = ""
    for front, back in pairs:
        f = front.replace('<', '&lt;').replace('>', '&gt;')
        b = back.replace('<', '&lt;').replace('>', '&gt;')
        cards_html += f"""
        <div class="fc" onclick="this.classList.toggle('flipped')">
          <div class="fc-inner">
            <div class="fc-front">
              <span class="fc-tag">concept</span>
              <p>{f}</p>
              <span class="fc-hint">tap to reveal</span>
            </div>
            <div class="fc-back">
              <span class="fc-tag">definition</span>
              <p>{b}</p>
            </div>
          </div>
        </div>"""
    rows = (len(pairs) + 1) // 2
    height = rows * 230 + 80
    return f"""<!DOCTYPE html><html><head>
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{background:transparent;font-family:'Nunito',sans-serif;padding:4px 0}}
    .hint{{color:{t['text2']};font-size:11.5px;text-align:center;margin-bottom:16px;letter-spacing:1.5px;text-transform:uppercase;font-weight:600}}
    .grid{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
    .fc{{perspective:1200px;height:210px;cursor:pointer;user-select:none}}
    .fc-inner{{position:relative;width:100%;height:100%;transition:transform .7s cubic-bezier(.4,0,.2,1);transform-style:preserve-3d}}
    .fc.flipped .fc-inner{{transform:rotateY(180deg)}}
    .fc-front,.fc-back{{position:absolute;inset:0;backface-visibility:hidden;-webkit-backface-visibility:hidden;display:flex;flex-direction:column;align-items:center;justify-content:center;border-radius:18px;padding:22px;text-align:center}}
    .fc-front{{background:{t['surface']};border:1.5px solid {t['border']};background-image:radial-gradient(ellipse at top left,{t['aurora1']},transparent 60%)}}
    .fc-back{{background:linear-gradient(135deg,{t['card_back']},{t['surface2']});border:1.5px solid {t['accent']};transform:rotateY(180deg)}}
    .fc-tag{{font-size:9px;letter-spacing:2px;text-transform:uppercase;margin-bottom:10px;font-weight:700;color:{t['text2']};border:1px solid {t['border']};border-radius:20px;padding:2px 8px}}
    .fc-back .fc-tag{{color:{t['accent']};border-color:{t['accent_bg']}}}
    .fc-front p{{color:{t['text']};font-size:14px;line-height:1.65;font-weight:500}}
    .fc-back p{{color:{t['card_back_text']};font-size:13px;line-height:1.65;font-weight:500}}
    .fc-hint{{font-size:10px;color:{t['text2']};margin-top:12px;letter-spacing:1px;text-transform:uppercase;opacity:0.5}}
    </style></head><body>
    <p class="hint">— tap a card to flip —</p>
    <div class="grid">{cards_html}</div>
    </body></html>""", height


# ---- INJECT CSS ----
st.markdown(get_css(st.session_state.theme), unsafe_allow_html=True)

# ---- THEME BUTTON ----
icons = {'Dark': 'Dark', 'Light': 'Light', 'System': 'Auto'}
indicators = {'Dark': '◐', 'Light': '○', 'System': '◑'}
cycle = {'Dark': 'Light', 'Light': 'System', 'System': 'Dark'}
current = st.session_state.theme
next_theme = cycle[current]

params = st.query_params
if 'theme' in params:
    new = params['theme']
    if new in ['Dark', 'Light', 'System'] and new != st.session_state.theme:
        st.session_state.theme = new
        st.query_params.clear()
        st.rerun()

t = T['Dark'] if st.session_state.theme == 'System' else T[st.session_state.theme]

st.markdown(f"""
<a href="?theme={next_theme}" target="_self" class="theme-btn">
    {indicators[current]} {icons[current]}
</a>
""", unsafe_allow_html=True)

# ---- HERO ----
st.markdown("""
<div style='padding:3rem 0 1.5rem 0'>
  <div class='hero-title'>Study<span class='hero-accent'>Tube</span></div>
  <div class='hero-sub'>Drop a YouTube link.<br>Walk away with a full set of study notes.</div>
</div>
""", unsafe_allow_html=True)

# ---- FORM ----
with st.form("main_form"):
    url = st.text_input("", placeholder="youtube.com/watch?v=...", label_visibility="collapsed")
    col1, col2 = st.columns([3, 1])
    with col1:
        submitted = st.form_submit_button("Generate Study Notes", use_container_width=True)
    with col2:
        lang_name = st.selectbox(
            "",
            list(SUPPORTED_LANGUAGES.keys()),
            index=0,
            label_visibility="collapsed"
        )

if submitted:
    url = url.strip()
    selected_lang = SUPPORTED_LANGUAGES[lang_name]

    if not url:
        st.error("Please paste a YouTube URL to get started.")
    elif not ("youtube.com" in url or "youtu.be" in url):
        st.error("That doesn't look like a YouTube link. Please check and try again.")
    else:
        with st.spinner("Fetching transcript..."):
            text, error = get_transcript(url, language=selected_lang)

        if error:
            st.error(error) 
        else:
            word_count = len(text.split())
            _, was_truncated = truncate_text(text)

            if was_truncated:
                st.info(f"Long video detected — Please wait...")
            else:
                st.markdown(f"<div class='word-count'>{word_count:,} words</div>", unsafe_allow_html=True)

            with st.spinner("Generating notes..."):
                from summarizer import get_all_notes, parse_all_notes
                raw_notes = get_all_notes(text)
                notes = parse_all_notes(raw_notes)
                summary = notes['summary']
                keypoints = notes['keypoints']
                qa = notes['qa']
                quiz_text = notes['quiz']
                flashcards_text = notes['flashcards']

            with st.spinner("Detecting visuals..."):
                visuals = get_visuals(text)
            

            st.session_state.results = {
                'url': url,
                'summary': summary,
                'keypoints': keypoints,
                'qa': qa,
                'quiz_text': quiz_text,
                'flashcards_text': flashcards_text,
                'quiz_questions': parse_quiz(quiz_text),
                'flashcard_pairs': parse_flashcards(flashcards_text),
                'visuals': visuals,
                'word_count': word_count,
                'was_truncated': was_truncated,
            }
            st.session_state.quiz_submitted = False

# ---- RESULTS ----
if st.session_state.results:
    r = st.session_state.results

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Summary", "Key Points", "Q & A", "Quiz", "Flashcards", "Visuals"
    ])

    with tab1:
        st.markdown("<div class='section-badge'>Summary</div>", unsafe_allow_html=True)
        st.write(r['summary'])

    with tab2:
        st.markdown("<div class='section-badge'>Key Points</div>", unsafe_allow_html=True)
        st.write(r['keypoints'])

    with tab3:
        st.markdown("<div class='section-badge'>Q & A</div>", unsafe_allow_html=True)
        st.write(r['qa'])

    with tab4:
        st.markdown("<div class='section-badge'>Quiz</div>", unsafe_allow_html=True)
        questions = r['quiz_questions']
        if not questions:
            st.write(r['quiz_text'])
        else:
            for i, q in enumerate(questions):
                st.markdown(f"<div class='quiz-q'><p>Q{i+1}. {q['question']}</p></div>", unsafe_allow_html=True)
                opts = [f"{k})  {v}" for k, v in q['options'].items()]
                selected = st.radio("", opts, key=f"quiz_{i}", index=None, label_visibility="collapsed")
                if st.session_state.quiz_submitted and selected is not None:
                    if selected[0] == q['answer']:
                        st.markdown("<div class='correct-answer'>Correct</div>", unsafe_allow_html=True)
                    else:
                        correct_text = q['options'].get(q['answer'], '')
                        st.markdown(f"<div class='wrong-answer'>Wrong — correct answer: {q['answer']}) {correct_text}</div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Submit Answers", use_container_width=True):
                    st.session_state.quiz_submitted = True
                    st.rerun()
            with col2:
                if st.button("Reset Quiz", use_container_width=True):
                    st.session_state.quiz_submitted = False
                    for i in range(len(questions)):
                        if f"quiz_{i}" in st.session_state:
                            del st.session_state[f"quiz_{i}"]
                    st.rerun()

    with tab5:
        st.markdown("<div class='section-badge'>Flashcards</div>", unsafe_allow_html=True)
        pairs = r['flashcard_pairs']
        if pairs:
            html_content, card_height = render_flashcards_html(pairs, st.session_state.theme)
            components.html(html_content, height=card_height, scrolling=False)
        else:
            st.write(r['flashcards_text'])

    with tab6:
        st.markdown("<div class='section-badge'>Visuals</div>", unsafe_allow_html=True)
        v = r['visuals']
        found_any = False

        if v.get('has_flowchart') and v.get('flowchart_mermaid'):
            found_any = True
            st.markdown(f"<div class='visual-card'><div class='visual-title'>{v.get('flowchart_title', 'Process Flow')}</div></div>", unsafe_allow_html=True)
            mermaid_html = render_mermaid(v['flowchart_mermaid'], st.session_state.theme)
            components.html(mermaid_html, height=380, scrolling=False)

        if v.get('has_chart') and v.get('chart_labels') and v.get('chart_values'):
            if len(v['chart_labels']) == len(v['chart_values']) and len(v['chart_labels']) > 0:
                found_any = True
                st.markdown("<br>", unsafe_allow_html=True)
                theme_for_chart = 'Dark' if st.session_state.theme != 'Light' else 'Light'
                try:
                    img_b64 = generate_chart(
                        v.get('chart_type', 'bar'),
                        v.get('chart_title', 'Data from Video'),
                        v['chart_labels'],
                        v['chart_values'],
                        theme=theme_for_chart
                    )
                    st.image(f"data:image/png;base64,{img_b64}", use_container_width=True)
                except Exception:
                    pass

        if v.get('has_mindmap') and v.get('mindmap_nodes'):
            found_any = True
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"<div class='visual-card'><div class='visual-title'>{v.get('mindmap_title', 'Concept Map')}</div></div>", unsafe_allow_html=True)
            nodes = v['mindmap_nodes']
            center = v.get('mindmap_title', 'Main Topic')
            mermaid_code = f"mindmap\n  root(({center}))\n"
            for node in nodes[:8]:
                mermaid_code += f"    {node}\n"
            mermaid_html = render_mermaid(mermaid_code, st.session_state.theme)
            components.html(mermaid_html, height=360, scrolling=False)

        if not found_any:
            st.markdown("<div class='no-visual'>No diagrams or charts detected in this video. Try a tutorial, lecture, or data-focused video for best results.</div>", unsafe_allow_html=True)

    st.markdown("---")

    with st.spinner("Preparing PDF..."):
        pdf_bytes = generate_pdf(
            r['url'], r['summary'], r['keypoints'],
            r['qa'], r['quiz_text'], r['flashcards_text']
        )

    st.download_button(
        label="Download Notes as PDF",
        data=pdf_bytes,
        file_name="studytube_notes.pdf",
        mime="application/pdf",
        use_container_width=True
    )
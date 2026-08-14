"""
Turns the raw '[QUIZ]' / '[FLASHCARDS]' text blocks produced by the LLM
into structured data the API can return as JSON. Moved here (unchanged
logic) from the old Streamlit app.py so the FastAPI layer can reuse it.
"""
import re


def parse_quiz(text: str) -> list[dict]:
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


def parse_flashcards(text: str) -> list[dict]:
    pairs = []
    cards = text.strip().split('FRONT:')
    for card in cards:
        if 'BACK:' in card:
            parts = card.split('BACK:', 1)
            front = parts[0].strip()
            back = parts[1].strip()
            if front and back:
                pairs.append({'front': front, 'back': back})
    return pairs

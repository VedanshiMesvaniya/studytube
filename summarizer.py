import os
import json
import time
from groq import Groq
from dotenv import load_dotenv
from utils import truncate_text, chunk_text

load_dotenv()

import streamlit as st

def get_client():
    try:
        import streamlit as st
        key = st.secrets["GROQ_API_KEY"]
    except Exception:
        key = os.getenv("GROQ_API_KEY")
    return Groq(api_key=key))

def ask_groq(prompt, max_tokens=1800, retries=3):
    client = get_client()
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            if '429' in str(e) and attempt < retries - 1:
                time.sleep(8)
                continue
            raise e

def compress_transcript(text):
    word_count = len(text.split())

    # short enough — no compression needed
    if word_count <= 2000:
        return text, 1

    chunks = chunk_text(text, chunk_size=1200)
    summaries = []

    for i, chunk in enumerate(chunks):
        prompt = f"""Summarize this transcript segment in 80-100 words.
Keep all key facts, names, numbers, and concepts.
Do not include any intro. Start directly.

Segment:
{chunk}"""
        try:
            summary = ask_groq(prompt, max_tokens=150)
            summaries.append(summary)
            # small delay between chunk calls to avoid TPM limit
            if i < len(chunks) - 1:
                time.sleep(2)
        except Exception:
            # if a chunk fails just skip it
            continue

    compressed = " ".join(summaries)

    # final safety truncate on the compressed version
    compressed, _ = truncate_text(compressed, max_words=2000)
    return compressed, len(chunks)

def get_all_notes(text):
    compressed, num_chunks = compress_transcript(text)

    prompt = f"""Analyze this video transcript and return ALL sections below in one response.

Use EXACTLY these section headers:

[SUMMARY]
Write a 150-200 word summary. No intro or preamble. Start directly.

[KEYPOINTS]
Write exactly 6 key points. Each MUST start with a dash and space:
- First key point here
- Second key point here
- Third key point here
- Fourth key point here
- Fifth key point here
- Sixth key point here
No paragraphs. No numbering. Dash bullet points ONLY.

[QA]
Generate 5 questions and answers. Format exactly:
Q: question here
A: answer here

[QUIZ]
Create 5 multiple choice questions. Format exactly:
Q1: question here
A) option one
B) option two
C) option three
D) option four
Answer: A

[FLASHCARDS]
Create 8 flashcards. Format exactly:
FRONT: term or concept
BACK: definition or explanation

Transcript:
{compressed}"""

    return ask_groq(prompt, max_tokens=1800), num_chunks

def parse_all_notes(raw):
    if isinstance(raw, tuple):
        raw = raw[0]

    sections = {
        'summary': '',
        'keypoints': '',
        'qa': '',
        'quiz': '',
        'flashcards': ''
    }

    markers = {
        'summary': '[SUMMARY]',
        'keypoints': '[KEYPOINTS]',
        'qa': '[QA]',
        'quiz': '[QUIZ]',
        'flashcards': '[FLASHCARDS]'
    }

    order = ['summary', 'keypoints', 'qa', 'quiz', 'flashcards']

    for i, key in enumerate(order):
        start_marker = markers[key]
        start_idx = raw.find(start_marker)
        if start_idx == -1:
            continue
        start_idx += len(start_marker)

        if i + 1 < len(order):
            next_marker = markers[order[i + 1]]
            end_idx = raw.find(next_marker)
            if end_idx == -1:
                sections[key] = raw[start_idx:].strip()
            else:
                sections[key] = raw[start_idx:end_idx].strip()
        else:
            sections[key] = raw[start_idx:].strip()

    return sections

def get_visuals(text):
    compressed, _ = compress_transcript(text)

    prompt = f"""Analyze this transcript and identify visual content.

Return ONLY a valid JSON object, no markdown, no explanation:
{{
  "has_flowchart": false,
  "flowchart_title": "",
  "flowchart_mermaid": "",
  "has_chart": false,
  "chart_type": "bar",
  "chart_title": "",
  "chart_labels": [],
  "chart_values": [],
  "has_mindmap": false,
  "mindmap_title": "",
  "mindmap_nodes": []
}}

Rules:
- has_flowchart: true only if transcript explains a clear process or steps
- flowchart_mermaid: valid mermaid flowchart TD syntax, short labels only
- has_chart: true only if transcript mentions actual numbers or statistics
- chart_type: bar, line, or pie only
- chart_labels and chart_values must match in length, max 8 items
- has_mindmap: true if transcript covers multiple related concepts
- mindmap_nodes: list of concept strings, max 8 items

Transcript:
{compressed}"""

    raw = ask_groq(prompt, max_tokens=600)
    try:
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())
    except Exception:
        return {
            "has_flowchart": False, "flowchart_title": "", "flowchart_mermaid": "",
            "has_chart": False, "chart_type": "", "chart_title": "",
            "chart_labels": [], "chart_values": [],
            "has_mindmap": False, "mindmap_title": "", "mindmap_nodes": []
        }

def get_summary(text):
    return parse_all_notes(get_all_notes(text)[0])['summary']

def get_keypoints(text):
    return parse_all_notes(get_all_notes(text)[0])['keypoints']

def get_qa(text):
    return parse_all_notes(get_all_notes(text)[0])['qa']

def get_quiz(text):
    return parse_all_notes(get_all_notes(text)[0])['quiz']

def get_flashcards(text):
    return parse_all_notes(get_all_notes(text)[0])['flashcards']

import os
import re
from datetime import date
import httpx
from . import crud
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
MAX_RECORDS = 50
SYSTEM_PROMPT = (
    "You answer questions about a students database. Use ONLY the data provided "
    "in the context. If the answer is not in the context, say you don't know. "
    "Do not invent students or numbers. Be concise."
)
def _fetch_relevant(question: str) -> list[dict]:
    """Pick records using simple, safe rules based on the question text."""
    q = question.lower()
    filters: dict = {}
    year = re.search(r"\b(19|20)\d{2}\b", q)
    if year:
        y = int(year.group())
        if re.search(r"\b(after|since|later than)\b", q):
            filters["born_after"] = date(y, 12, 31)      # born after year y
        elif re.search(r"\b(before|earlier than)\b", q):
            filters["born_before"] = date(y, 1, 1)       # born before year y
        else:
            filters["born_after"] = date(y - 1, 12, 31)
            filters["born_before"] = date(y + 1, 1, 1)
    for course in crud.distinct_courses():
        if course.lower() in q:
            filters["course"] = course
            break
    return crud.list_students(limit=MAX_RECORDS, **filters)
def _format_record(r: dict) -> str:
    return (
        f"- id={r['id']}, name={r['name']}, dob={r['date_of_birth']}, "
        f"course={r['course'] or 'N/A'}, email={r['email'] or 'N/A'}, "
        f"enrolled={r['enrollment_date'] or 'N/A'}"
    )
def ask(question: str) -> dict:
    records = _fetch_relevant(question)
    total = crud.count_students()
    context = (
        f"Total students in database: {total}\n"
        f"Records relevant to the question ({len(records)} shown):\n"
        + ("\n".join(_format_record(r) for r in records) or "(none)")
    )
    payload = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "options": {"temperature": 0},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
    }
    resp = httpx.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=120)
    resp.raise_for_status()
    answer = resp.json()["message"]["content"].strip()
    return {
        "question": question,
        "answer": answer,
        "records_used": len(records),
        "model": OLLAMA_MODEL,
    }

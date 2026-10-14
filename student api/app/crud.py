import sqlite3
from datetime import date
from typing import Optional
from .database import get_conn
FIELDS = ["name", "date_of_birth", "email", "phone", "course", "address", "enrollment_date"]
def _to_params(data: dict) -> dict:
    """Convert date objects to ISO strings for storage."""
    return {k: (v.isoformat() if isinstance(v, date) else v) for k, v in data.items()}
def create_student(data: dict) -> dict:
    data = _to_params(data)
    cols = ", ".join(FIELDS)
    marks = ", ".join(f":{f}" for f in FIELDS)
    params = {f: data.get(f) for f in FIELDS}
    with get_conn() as conn:
        cur = conn.execute(f"INSERT INTO students ({cols}) VALUES ({marks})", params)
        row = conn.execute("SELECT * FROM students WHERE id = ?", (cur.lastrowid,)).fetchone()
    return dict(row)
def get_student(student_id: int) -> Optional[dict]:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    return dict(row) if row else None
def list_students(
    name: Optional[str] = None,
    course: Optional[str] = None,
    born_after: Optional[date] = None,
    born_before: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[dict]:
    query = "SELECT * FROM students WHERE 1=1"
    params: list = []
    if name:
        query += " AND name LIKE ?"
        params.append(f"%{name}%")
    if course:
        query += " AND course LIKE ?"
        params.append(f"%{course}%")
    if born_after:
        query += " AND date_of_birth > ?"
        params.append(born_after.isoformat())
    if born_before:
        query += " AND date_of_birth < ?"
        params.append(born_before.isoformat())
    query += " ORDER BY id LIMIT ? OFFSET ?"
    params += [limit, skip]
    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]
def count_students() -> int:
    with get_conn() as conn:
        return conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
def update_student(student_id: int, changes: dict) -> Optional[dict]:
    changes = _to_params(changes)
    if not changes:
        return get_student(student_id)
    sets = ", ".join(f"{k} = :{k}" for k in changes)  # keys come from the schema, not the user
    with get_conn() as conn:
        cur = conn.execute(
            f"UPDATE students SET {sets} WHERE id = :_id", {**changes, "_id": student_id}
        )
        if cur.rowcount == 0:
            return None
        row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    return dict(row)
def delete_student(student_id: int) -> bool:
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    return cur.rowcount > 0
def distinct_courses() -> list[str]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT DISTINCT course FROM students WHERE course IS NOT NULL"
        ).fetchall()
    return [r[0] for r in rows]
# Re-exported so main.py can catch it
IntegrityError = sqlite3.IntegrityError

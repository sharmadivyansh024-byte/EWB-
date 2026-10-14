"""Students Database CRUD API - FastAPI + SQLite (+ optional Ollama AI)."""
from contextlib import asynccontextmanager
from datetime import date
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException, Query, Response, status

from . import ai, crud
from .database import init_db
from .schemas import AskRequest, AskResponse, Student, StudentCreate, StudentUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # create the table on startup if it doesn't exist
    yield


app = FastAPI(
    title="Students Database API",
    description="CRUD API for student records using FastAPI and SQLite.",
    version="1.0.0",
    lifespan=lifespan,
)


def _not_found(student_id: int) -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, f"Student {student_id} not found")


@app.get("/", tags=["Health"])
def root():
    return {"message": "Students API is running. Open /docs for interactive docs."}


# ---------- CREATE ----------
@app.post("/students", response_model=Student, status_code=status.HTTP_201_CREATED, tags=["Students"])
def create_student(student: StudentCreate):
    try:
        return crud.create_student(student.model_dump())
    except crud.IntegrityError:
        raise HTTPException(status.HTTP_409_CONFLICT, "A student with this email already exists")


# ---------- READ (list / filter) ----------
@app.get("/students", response_model=list[Student], tags=["Students"])
def list_students(
    name: Optional[str] = Query(None, description="Partial name match"),
    course: Optional[str] = Query(None, description="Partial course match"),
    born_after: Optional[date] = Query(None, description="DOB strictly after YYYY-MM-DD"),
    born_before: Optional[date] = Query(None, description="DOB strictly before YYYY-MM-DD"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    return crud.list_students(name, course, born_after, born_before, skip, limit)


# ---------- READ (one) ----------
@app.get("/students/{student_id}", response_model=Student, tags=["Students"])
def get_student(student_id: int):
    student = crud.get_student(student_id)
    if not student:
        raise _not_found(student_id)
    return student


# ---------- UPDATE ----------
@app.put("/students/{student_id}", response_model=Student, tags=["Students"])
@app.patch("/students/{student_id}", response_model=Student, tags=["Students"])
def update_student(student_id: int, changes: StudentUpdate):
    try:
        updated = crud.update_student(student_id, changes.model_dump(exclude_unset=True))
    except crud.IntegrityError:
        raise HTTPException(status.HTTP_409_CONFLICT, "A student with this email already exists")
    if not updated:
        raise _not_found(student_id)
    return updated


# ---------- DELETE ----------
@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Students"])
def delete_student(student_id: int):
    if not crud.delete_student(student_id):
        raise _not_found(student_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------- OPTIONAL: AI (Ollama) ----------
@app.post("/ai/ask", response_model=AskResponse, tags=["AI (optional)"])
def ask_ai(body: AskRequest):
    try:
        return ai.ask(body.question)
    except (httpx.ConnectError, httpx.TimeoutException):
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Cannot reach Ollama. Start it with 'ollama serve' and run "
            f"'ollama pull {ai.OLLAMA_MODEL}'.",
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Ollama error: {e.response.text}")
